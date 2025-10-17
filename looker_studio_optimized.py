#!/usr/bin/env python3
"""
Looker Studio最適化エクスポーター
Google Sheets連携とCSV直接アップロードの両方に対応した
株価データエクスポートツール
"""

import yfinance as yf
import pandas as pd
import datetime
import os
import logging
from typing import List, Dict, Optional
import json
import gspread
from google.oauth2.service_account import Credentials
import time

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LookerStudioOptimized:
    """Looker Studio最適化エクスポーター"""
    
    def __init__(self, symbols: List[str], output_dir: str = "looker_optimized"):
        """
        初期化
        
        Args:
            symbols: 監視する株式シンボルのリスト
            output_dir: データ保存ディレクトリ
        """
        self.symbols = symbols
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Looker Studio用の最適化されたファイル
        self.dashboard_data_file = os.path.join(output_dir, "dashboard_data.csv")
        self.time_series_file = os.path.join(output_dir, "time_series_data.csv")
        self.summary_file = os.path.join(output_dir, "summary_data.csv")
        self.performance_file = os.path.join(output_dir, "performance_data.csv")
        
        # Google Sheets設定（オプション）
        self.gc = None
        self.setup_google_sheets()
    
    def setup_google_sheets(self):
        """Google Sheets APIの設定（オプション）"""
        try:
            # サービスアカウントキーファイルのパス
            service_account_file = "service_account_key.json"
            
            if os.path.exists(service_account_file):
                # スコープの設定
                scope = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                
                # 認証情報の作成
                creds = Credentials.from_service_account_file(service_account_file, scopes=scope)
                self.gc = gspread.authorize(creds)
                logger.info("Google Sheets API認証が完了しました")
            else:
                logger.info("Google Sheets API認証ファイルが見つかりません。CSV出力のみ使用します。")
                
        except Exception as e:
            logger.warning(f"Google Sheets API設定中にエラー: {str(e)}")
            self.gc = None
    
    def get_optimized_stock_data(self, symbol: str) -> Optional[Dict]:
        """
        Looker Studio用に最適化された株式データを取得
        
        Args:
            symbol: 株式シンボル
            
        Returns:
            最適化された株式データの辞書
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                logger.warning(f"{symbol}: データが取得できませんでした")
                return None
            
            # 基本情報
            company_name = info.get('longName', info.get('shortName', symbol))
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            currency = info.get('currency', 'USD')
            
            # 最新データ
            latest = hist.iloc[-1]
            current_price = round(latest['Close'], 2)
            previous_close = round(latest['Open'], 2)
            change = round(current_price - previous_close, 2)
            change_percent = round((change / previous_close) * 100, 2) if previous_close != 0 else 0
            
            # 日中の範囲
            day_high = round(latest['High'], 2)
            day_low = round(latest['Low'], 2)
            
            # 52週間の範囲
            fifty_two_week_high = info.get('fiftyTwoWeekHigh', day_high)
            fifty_two_week_low = info.get('fiftyTwoWeekLow', day_low)
            
            # 現在の日時
            now = datetime.datetime.now()
            
            # Looker Studio用に最適化されたデータ構造
            data = {
                # === 基本識別情報 ===
                'stock_symbol': symbol,
                'company_name': company_name,
                'sector': sector,
                'industry': industry,
                'currency': currency,
                
                # === 日時情報 ===
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M:%S'),
                'datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                'year': now.year,
                'month': now.month,
                'day': now.day,
                'hour': now.hour,
                'minute': now.minute,
                'weekday': now.strftime('%A'),
                'weekday_number': now.weekday(),
                
                # === 価格情報 ===
                'current_price': current_price,
                'previous_close': previous_close,
                'open_price': round(latest['Open'], 2),
                'day_high': day_high,
                'day_low': day_low,
                'price_change': change,
                'price_change_percent': change_percent,
                
                # === 範囲情報 ===
                'day_range_low': day_low,
                'day_range_high': day_high,
                'day_range_spread': round(day_high - day_low, 2),
                'fifty_two_week_high': fifty_two_week_high,
                'fifty_two_week_low': fifty_two_week_low,
                'fifty_two_week_spread': round(fifty_two_week_high - fifty_two_week_low, 2),
                
                # === 取引量情報 ===
                'volume': int(latest['Volume']),
                'average_volume': info.get('averageVolume', latest['Volume']),
                'volume_ratio': round(latest['Volume'] / info.get('averageVolume', latest['Volume']), 2) if info.get('averageVolume') else 1.0,
                
                # === 市場情報 ===
                'market_cap': info.get('marketCap', 0),
                'market_cap_billions': round(info.get('marketCap', 0) / 1e9, 2) if info.get('marketCap') else 0,
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float_shares': info.get('floatShares', 0),
                
                # === 財務指標 ===
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'dividend_rate': info.get('dividendRate', 0),
                
                # === 技術指標 ===
                'beta': info.get('beta', 0),
                'volatility': round(((day_high - day_low) / current_price) * 100, 2) if current_price != 0 else 0,
                'rsi_14': 0,  # 後で計算
                
                # === パフォーマンス指標 ===
                'performance_1d': change_percent,
                'performance_1w': 0,  # 週次パフォーマンス
                'performance_1m': 0,  # 月次パフォーマンス
                'performance_1y': 0,  # 年次パフォーマンス
                
                # === Looker Studio用カテゴリ分類 ===
                'price_category': self._categorize_price(current_price),
                'change_category': self._categorize_change(change_percent),
                'volume_category': self._categorize_volume(latest['Volume'], info.get('averageVolume', latest['Volume'])),
                'market_cap_category': self._categorize_market_cap(info.get('marketCap', 0)),
                'sector_category': self._categorize_sector(sector),
                'volatility_category': self._categorize_volatility(((day_high - day_low) / current_price) * 100 if current_price != 0 else 0),
                
                # === 分析用フラグ ===
                'is_gain': change > 0,
                'is_loss': change < 0,
                'is_high_volume': latest['Volume'] > info.get('averageVolume', latest['Volume']) * 1.5 if info.get('averageVolume') else False,
                'is_high_volatility': ((day_high - day_low) / current_price) * 100 > 5 if current_price != 0 else False,
                'is_large_cap': info.get('marketCap', 0) > 10e9,
                'is_dividend_stock': info.get('dividendYield', 0) > 0,
            }
            
            return data
            
        except Exception as e:
            logger.error(f"{symbol}のデータ取得中にエラーが発生しました: {str(e)}")
            return None
    
    def _categorize_price(self, price: float) -> str:
        """価格をカテゴリに分類"""
        if price < 10:
            return "Under $10"
        elif price < 25:
            return "$10-$25"
        elif price < 50:
            return "$25-$50"
        elif price < 100:
            return "$50-$100"
        elif price < 200:
            return "$100-$200"
        else:
            return "Over $200"
    
    def _categorize_change(self, change_percent: float) -> str:
        """価格変動をカテゴリに分類"""
        if change_percent < -5:
            return "Large Decrease (>-5%)"
        elif change_percent < -2:
            return "Decrease (-2% to -5%)"
        elif change_percent < -0.5:
            return "Small Decrease (-0.5% to -2%)"
        elif change_percent < 0.5:
            return "Stable (-0.5% to 0.5%)"
        elif change_percent < 2:
            return "Small Increase (0.5% to 2%)"
        elif change_percent < 5:
            return "Increase (2% to 5%)"
        else:
            return "Large Increase (>5%)"
    
    def _categorize_volume(self, volume: int, avg_volume: int) -> str:
        """取引量をカテゴリに分類"""
        if avg_volume == 0:
            return "Unknown"
        
        ratio = volume / avg_volume
        if ratio < 0.5:
            return "Very Low (<50%)"
        elif ratio < 0.8:
            return "Low (50%-80%)"
        elif ratio < 1.2:
            return "Normal (80%-120%)"
        elif ratio < 2:
            return "High (120%-200%)"
        else:
            return "Very High (>200%)"
    
    def _categorize_market_cap(self, market_cap: int) -> str:
        """時価総額をカテゴリに分類"""
        if market_cap == 0:
            return "Unknown"
        
        if market_cap < 300e6:  # 3億未満
            return "Micro Cap (<$300M)"
        elif market_cap < 2e9:  # 20億未満
            return "Small Cap ($300M-$2B)"
        elif market_cap < 10e9:  # 100億未満
            return "Mid Cap ($2B-$10B)"
        elif market_cap < 200e9:  # 2000億未満
            return "Large Cap ($10B-$200B)"
        else:
            return "Mega Cap (>$200B)"
    
    def _categorize_sector(self, sector: str) -> str:
        """セクターをカテゴリに分類"""
        if not sector or sector == 'Unknown':
            return 'Unknown'
        
        # 主要セクターの分類
        tech_sectors = ['Technology', 'Software', 'Hardware', 'Semiconductors']
        finance_sectors = ['Financial Services', 'Banks', 'Insurance']
        healthcare_sectors = ['Healthcare', 'Biotechnology', 'Pharmaceuticals']
        consumer_sectors = ['Consumer Discretionary', 'Consumer Staples', 'Retail']
        
        if any(tech in sector for tech in tech_sectors):
            return 'Technology'
        elif any(fin in sector for fin in finance_sectors):
            return 'Financial'
        elif any(health in sector for health in healthcare_sectors):
            return 'Healthcare'
        elif any(cons in sector for cons in consumer_sectors):
            return 'Consumer'
        else:
            return 'Other'
    
    def _categorize_volatility(self, volatility: float) -> str:
        """ボラティリティをカテゴリに分類"""
        if volatility < 1:
            return "Very Low (<1%)"
        elif volatility < 2:
            return "Low (1%-2%)"
        elif volatility < 3:
            return "Medium (2%-3%)"
        elif volatility < 5:
            return "High (3%-5%)"
        else:
            return "Very High (>5%)"
    
    def export_dashboard_data(self):
        """ダッシュボード用データをエクスポート"""
        logger.info("ダッシュボード用データのエクスポートを開始します")
        
        all_data = []
        for symbol in self.symbols:
            logger.info(f"{symbol}のデータを取得中...")
            data = self.get_optimized_stock_data(symbol)
            if data:
                all_data.append(data)
            time.sleep(0.5)  # API制限を避けるため
        
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(self.dashboard_data_file, index=False, encoding='utf-8-sig')
            logger.info(f"ダッシュボード用データを{self.dashboard_data_file}に保存しました")
            return df
        else:
            logger.warning("ダッシュボード用データが取得できませんでした")
            return None
    
    def export_time_series_data(self, period: str = "1mo"):
        """時系列データをエクスポート"""
        logger.info(f"時系列データのエクスポートを開始します（期間: {period}）")
        
        all_data = []
        for symbol in self.symbols:
            logger.info(f"{symbol}の時系列データを取得中...")
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                if not hist.empty:
                    for date, row in hist.iterrows():
                        data = {
                            'date': date.strftime('%Y-%m-%d'),
                            'datetime': date.strftime('%Y-%m-%d %H:%M:%S'),
                            'year': date.year,
                            'month': date.month,
                            'day': date.day,
                            'weekday': date.strftime('%A'),
                            'weekday_number': date.weekday(),
                            'stock_symbol': symbol,
                            'open_price': round(row['Open'], 2),
                            'high_price': round(row['High'], 2),
                            'low_price': round(row['Low'], 2),
                            'close_price': round(row['Close'], 2),
                            'volume': int(row['Volume']),
                            'price_change': round(row['Close'] - row['Open'], 2),
                            'price_change_percent': round(((row['Close'] - row['Open']) / row['Open']) * 100, 2) if row['Open'] != 0 else 0,
                            'daily_range': round(row['High'] - row['Low'], 2),
                            'daily_range_percent': round(((row['High'] - row['Low']) / row['Close']) * 100, 2) if row['Close'] != 0 else 0,
                        }
                        all_data.append(data)
            except Exception as e:
                logger.error(f"{symbol}の時系列データ取得中にエラー: {str(e)}")
        
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(self.time_series_file, index=False, encoding='utf-8-sig')
            logger.info(f"時系列データを{self.time_series_file}に保存しました")
            return df
        else:
            logger.warning("時系列データが取得できませんでした")
            return None
    
    def export_summary_data(self):
        """サマリーデータをエクスポート"""
        logger.info("サマリーデータのエクスポートを開始します")
        
        summary_data = []
        for symbol in self.symbols:
            logger.info(f"{symbol}のサマリーデータを取得中...")
            data = self.get_optimized_stock_data(symbol)
            if data:
                # サマリー用の簡略化されたデータ
                summary = {
                    'stock_symbol': data['stock_symbol'],
                    'company_name': data['company_name'],
                    'sector': data['sector'],
                    'sector_category': data['sector_category'],
                    'current_price': data['current_price'],
                    'price_change_percent': data['price_change_percent'],
                    'volume': data['volume'],
                    'market_cap_category': data['market_cap_category'],
                    'price_category': data['price_category'],
                    'change_category': data['change_category'],
                    'is_gain': data['is_gain'],
                    'is_high_volume': data['is_high_volume'],
                    'last_updated': data['datetime']
                }
                summary_data.append(summary)
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            df.to_csv(self.summary_file, index=False, encoding='utf-8-sig')
            logger.info(f"サマリーデータを{self.summary_file}に保存しました")
            return df
        else:
            logger.warning("サマリーデータが取得できませんでした")
            return None
    
    def export_performance_data(self, period: str = "1y"):
        """パフォーマンスデータをエクスポート"""
        logger.info(f"パフォーマンスデータのエクスポートを開始します（期間: {period}）")
        
        performance_data = []
        for symbol in self.symbols:
            logger.info(f"{symbol}のパフォーマンスデータを取得中...")
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                if not hist.empty:
                    # パフォーマンス計算
                    current_price = hist['Close'].iloc[-1]
                    start_price = hist['Close'].iloc[0]
                    
                    # 各期間のパフォーマンス
                    performance_1d = 0
                    performance_1w = 0
                    performance_1m = 0
                    performance_3m = 0
                    performance_6m = 0
                    performance_1y = round(((current_price - start_price) / start_price) * 100, 2)
                    
                    # 各期間のデータが存在する場合の計算
                    if len(hist) >= 2:
                        performance_1d = round(((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100, 2)
                    
                    if len(hist) >= 7:
                        performance_1w = round(((current_price - hist['Close'].iloc[-7]) / hist['Close'].iloc[-7]) * 100, 2)
                    
                    if len(hist) >= 30:
                        performance_1m = round(((current_price - hist['Close'].iloc[-30]) / hist['Close'].iloc[-30]) * 100, 2)
                    
                    if len(hist) >= 90:
                        performance_3m = round(((current_price - hist['Close'].iloc[-90]) / hist['Close'].iloc[-90]) * 100, 2)
                    
                    if len(hist) >= 180:
                        performance_6m = round(((current_price - hist['Close'].iloc[-180]) / hist['Close'].iloc[-180]) * 100, 2)
                    
                    data = {
                        'stock_symbol': symbol,
                        'current_price': current_price,
                        'performance_1d': performance_1d,
                        'performance_1w': performance_1w,
                        'performance_1m': performance_1m,
                        'performance_3m': performance_3m,
                        'performance_6m': performance_6m,
                        'performance_1y': performance_1y,
                        'best_performance': max(performance_1d, performance_1w, performance_1m, performance_3m, performance_6m, performance_1y),
                        'worst_performance': min(performance_1d, performance_1w, performance_1m, performance_3m, performance_6m, performance_1y),
                        'volatility': round(hist['Close'].pct_change().std() * 100, 2),
                        'max_price': round(hist['High'].max(), 2),
                        'min_price': round(hist['Low'].min(), 2),
                        'avg_volume': int(hist['Volume'].mean()),
                        'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    performance_data.append(data)
            except Exception as e:
                logger.error(f"{symbol}のパフォーマンスデータ取得中にエラー: {str(e)}")
        
        if performance_data:
            df = pd.DataFrame(performance_data)
            df.to_csv(self.performance_file, index=False, encoding='utf-8-sig')
            logger.info(f"パフォーマンスデータを{self.performance_file}に保存しました")
            return df
        else:
            logger.warning("パフォーマンスデータが取得できませんでした")
            return None
    
    def upload_to_google_sheets(self, spreadsheet_name: str = "Stock Data for Looker Studio"):
        """Google Sheetsにデータをアップロード"""
        if not self.gc:
            logger.warning("Google Sheets APIが設定されていません")
            return False
        
        try:
            # スプレッドシートを作成または取得
            try:
                spreadsheet = self.gc.open(spreadsheet_name)
                logger.info(f"既存のスプレッドシート '{spreadsheet_name}' を開きました")
            except gspread.SpreadsheetNotFound:
                spreadsheet = self.gc.create(spreadsheet_name)
                logger.info(f"新しいスプレッドシート '{spreadsheet_name}' を作成しました")
            
            # 各データファイルをアップロード
            files_to_upload = [
                (self.dashboard_data_file, "Dashboard Data"),
                (self.time_series_file, "Time Series Data"),
                (self.summary_file, "Summary Data"),
                (self.performance_file, "Performance Data")
            ]
            
            for file_path, sheet_name in files_to_upload:
                if os.path.exists(file_path):
                    # ワークシートを作成または取得
                    try:
                        worksheet = spreadsheet.worksheet(sheet_name)
                        worksheet.clear()
                    except gspread.WorksheetNotFound:
                        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=50)
                    
                    # CSVデータを読み込み
                    df = pd.read_csv(file_path)
                    
                    # ヘッダーを追加
                    worksheet.update('A1', [df.columns.values.tolist()])
                    
                    # データを追加
                    if not df.empty:
                        worksheet.update('A2', df.values.tolist())
                    
                    logger.info(f"{sheet_name}をGoogle Sheetsにアップロードしました")
            
            # スプレッドシートのURLを表示
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
            logger.info(f"スプレッドシートURL: {spreadsheet_url}")
            
            return True
            
        except Exception as e:
            logger.error(f"Google Sheetsアップロード中にエラー: {str(e)}")
            return False
    
    def export_all_data(self, upload_to_sheets: bool = False):
        """すべてのデータをエクスポート"""
        logger.info("すべてのデータのエクスポートを開始します")
        
        # 各データをエクスポート
        dashboard_df = self.export_dashboard_data()
        time_series_df = self.export_time_series_data()
        summary_df = self.export_summary_data()
        performance_df = self.export_performance_data()
        
        # Google Sheetsにアップロード（オプション）
        if upload_to_sheets:
            self.upload_to_google_sheets()
        
        # エクスポート結果のサマリー
        logger.info("=" * 60)
        logger.info("エクスポート完了サマリー:")
        logger.info(f"ダッシュボードデータ: {len(dashboard_df) if dashboard_df is not None else 0}件")
        logger.info(f"時系列データ: {len(time_series_df) if time_series_df is not None else 0}件")
        logger.info(f"サマリーデータ: {len(summary_df) if summary_df is not None else 0}件")
        logger.info(f"パフォーマンスデータ: {len(performance_df) if performance_df is not None else 0}件")
        logger.info("=" * 60)
        
        return {
            'dashboard': dashboard_df,
            'time_series': time_series_df,
            'summary': summary_df,
            'performance': performance_df
        }

def main():
    """メイン関数"""
    # 監視する株式シンボル
    symbols = [
        'AAPL',  # Apple
        'MSFT',  # Microsoft
        'GOOGL', # Google
        'AMZN',  # Amazon
        'TSLA',  # Tesla
        'NVDA',  # NVIDIA
        'META',  # Meta
        'NFLX',  # Netflix
        '7203.T', # トヨタ自動車
        '6758.T', # ソニー
        '9984.T', # ソフトバンクグループ
        '9432.T', # 日本電信電話
    ]
    
    # エクスポーターを作成
    exporter = LookerStudioOptimized(symbols)
    
    # 実行モードを選択
    print("Looker Studio最適化エクスポーター")
    print("=" * 50)
    print("1. ダッシュボードデータのみエクスポート")
    print("2. 時系列データのみエクスポート")
    print("3. サマリーデータのみエクスポート")
    print("4. パフォーマンスデータのみエクスポート")
    print("5. すべてのデータをエクスポート（CSVのみ）")
    print("6. すべてのデータをエクスポート（Google Sheets含む）")
    
    choice = input("選択 (1-6): ").strip()
    
    if choice == "1":
        exporter.export_dashboard_data()
    elif choice == "2":
        exporter.export_time_series_data()
    elif choice == "3":
        exporter.export_summary_data()
    elif choice == "4":
        exporter.export_performance_data()
    elif choice == "5":
        exporter.export_all_data(upload_to_sheets=False)
    elif choice == "6":
        exporter.export_all_data(upload_to_sheets=True)
    else:
        print("無効な選択です。すべてのデータをエクスポートします。")
        exporter.export_all_data(upload_to_sheets=False)

if __name__ == "__main__":
    main()
