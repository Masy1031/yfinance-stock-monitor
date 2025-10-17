#!/usr/bin/env python3
"""
Looker Studio用株価データエクスポーター
yfinanceから取得したデータをLooker Studioで最適に表示できる形式に変換します。
"""

import yfinance as yf
import pandas as pd
import datetime
import os
import logging
from typing import List, Dict, Optional
import json

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LookerStudioExporter:
    """Looker Studio用データエクスポーター"""
    
    def __init__(self, symbols: List[str], output_dir: str = "looker_data"):
        """
        初期化
        
        Args:
            symbols: 監視する株式シンボルのリスト
            output_dir: データ保存ディレクトリ
        """
        self.symbols = symbols
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Looker Studio用のファイル名
        self.daily_file = os.path.join(output_dir, "daily_stock_data.csv")
        self.historical_file = os.path.join(output_dir, "historical_stock_data.csv")
        self.summary_file = os.path.join(output_dir, "stock_summary.csv")
    
    def get_enhanced_stock_data(self, symbol: str, period: str = "1d") -> Optional[Dict]:
        """
        拡張された株式データを取得（Looker Studio用）
        
        Args:
            symbol: 株式シンボル
            period: データ取得期間
            
        Returns:
            拡張された株式データの辞書
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period=period, interval="1m" if period == "1d" else "1d")
            
            if hist.empty:
                logger.warning(f"{symbol}: データが取得できませんでした")
                return None
            
            # 基本情報
            company_name = info.get('longName', info.get('shortName', symbol))
            sector = info.get('sector', 'N/A')
            industry = info.get('industry', 'N/A')
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
            
            # ボラティリティ計算
            volatility = round(((day_high - day_low) / current_price) * 100, 2) if current_price != 0 else 0
            
            # データを整理
            data = {
                # 基本情報
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.datetime.now().strftime('%H:%M:%S'),
                'symbol': symbol,
                'company_name': company_name,
                'sector': sector,
                'industry': industry,
                'currency': currency,
                
                # 価格情報
                'current_price': current_price,
                'previous_close': previous_close,
                'open_price': round(latest['Open'], 2),
                'day_high': day_high,
                'day_low': day_low,
                'change': change,
                'change_percent': change_percent,
                
                # 範囲情報
                'day_range': f"{day_low} - {day_high}",
                'fifty_two_week_high': fifty_two_week_high,
                'fifty_two_week_low': fifty_two_week_low,
                'fifty_two_week_range': f"{fifty_two_week_low} - {fifty_two_week_high}",
                
                # 取引量情報
                'volume': int(latest['Volume']),
                'average_volume': info.get('averageVolume', latest['Volume']),
                'volume_ratio': round(latest['Volume'] / info.get('averageVolume', latest['Volume']), 2) if info.get('averageVolume') else 1.0,
                
                # 市場情報
                'market_cap': info.get('marketCap', 'N/A'),
                'enterprise_value': info.get('enterpriseValue', 'N/A'),
                'shares_outstanding': info.get('sharesOutstanding', 'N/A'),
                
                # 財務指標
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'peg_ratio': info.get('pegRatio', 'N/A'),
                'price_to_book': info.get('priceToBook', 'N/A'),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                
                # 技術指標
                'volatility': volatility,
                'beta': info.get('beta', 'N/A'),
                'rsi_14': 'N/A',  # RSIは別途計算が必要
                
                # パフォーマンス指標
                'performance_1d': change_percent,
                'performance_1w': 'N/A',  # 週次パフォーマンス
                'performance_1m': 'N/A',  # 月次パフォーマンス
                'performance_1y': 'N/A',  # 年次パフォーマンス
                
                # Looker Studio用の追加フィールド
                'price_category': self._categorize_price(current_price),
                'change_category': self._categorize_change(change_percent),
                'volume_category': self._categorize_volume(latest['Volume'], info.get('averageVolume', latest['Volume'])),
                'market_cap_category': self._categorize_market_cap(info.get('marketCap', 0)),
            }
            
            return data
            
        except Exception as e:
            logger.error(f"{symbol}のデータ取得中にエラーが発生しました: {str(e)}")
            return None
    
    def _categorize_price(self, price: float) -> str:
        """価格をカテゴリに分類"""
        if price < 10:
            return "Low Price"
        elif price < 50:
            return "Medium Price"
        elif price < 100:
            return "High Price"
        else:
            return "Very High Price"
    
    def _categorize_change(self, change_percent: float) -> str:
        """価格変動をカテゴリに分類"""
        if change_percent < -5:
            return "Large Decrease"
        elif change_percent < -1:
            return "Decrease"
        elif change_percent < 1:
            return "Stable"
        elif change_percent < 5:
            return "Increase"
        else:
            return "Large Increase"
    
    def _categorize_volume(self, volume: int, avg_volume: int) -> str:
        """取引量をカテゴリに分類"""
        if avg_volume == 0:
            return "Unknown"
        
        ratio = volume / avg_volume
        if ratio < 0.5:
            return "Low Volume"
        elif ratio < 1.5:
            return "Normal Volume"
        elif ratio < 3:
            return "High Volume"
        else:
            return "Very High Volume"
    
    def _categorize_market_cap(self, market_cap: int) -> str:
        """時価総額をカテゴリに分類"""
        if market_cap == 0 or market_cap == 'N/A':
            return "Unknown"
        
        if market_cap < 2e9:  # 20億未満
            return "Small Cap"
        elif market_cap < 10e9:  # 100億未満
            return "Mid Cap"
        elif market_cap < 200e9:  # 2000億未満
            return "Large Cap"
        else:
            return "Mega Cap"
    
    def export_daily_data(self):
        """日次データをエクスポート"""
        logger.info("日次データのエクスポートを開始します")
        
        all_data = []
        for symbol in self.symbols:
            logger.info(f"{symbol}のデータを取得中...")
            data = self.get_enhanced_stock_data(symbol, period="1d")
            if data:
                all_data.append(data)
        
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(self.daily_file, index=False, encoding='utf-8-sig')
            logger.info(f"日次データを{self.daily_file}に保存しました")
            return df
        else:
            logger.warning("日次データが取得できませんでした")
            return None
    
    def export_historical_data(self, period: str = "1mo"):
        """履歴データをエクスポート"""
        logger.info(f"履歴データのエクスポートを開始します（期間: {period}）")
        
        all_data = []
        for symbol in self.symbols:
            logger.info(f"{symbol}の履歴データを取得中...")
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                if not hist.empty:
                    for date, row in hist.iterrows():
                        data = {
                            'date': date.strftime('%Y-%m-%d'),
                            'symbol': symbol,
                            'open': round(row['Open'], 2),
                            'high': round(row['High'], 2),
                            'low': round(row['Low'], 2),
                            'close': round(row['Close'], 2),
                            'volume': int(row['Volume']),
                            'adj_close': round(row['Close'], 2),  # 調整後終値
                        }
                        all_data.append(data)
            except Exception as e:
                logger.error(f"{symbol}の履歴データ取得中にエラー: {str(e)}")
        
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(self.historical_file, index=False, encoding='utf-8-sig')
            logger.info(f"履歴データを{self.historical_file}に保存しました")
            return df
        else:
            logger.warning("履歴データが取得できませんでした")
            return None
    
    def export_summary_data(self):
        """サマリーデータをエクスポート"""
        logger.info("サマリーデータのエクスポートを開始します")
        
        summary_data = []
        for symbol in self.symbols:
            logger.info(f"{symbol}のサマリーデータを取得中...")
            data = self.get_enhanced_stock_data(symbol, period="1d")
            if data:
                # サマリー用の簡略化されたデータ
                summary = {
                    'symbol': data['symbol'],
                    'company_name': data['company_name'],
                    'sector': data['sector'],
                    'current_price': data['current_price'],
                    'change_percent': data['change_percent'],
                    'volume': data['volume'],
                    'market_cap_category': data['market_cap_category'],
                    'price_category': data['price_category'],
                    'change_category': data['change_category'],
                    'last_updated': data['timestamp']
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
    
    def export_all_data(self):
        """すべてのデータをエクスポート"""
        logger.info("すべてのデータのエクスポートを開始します")
        
        daily_df = self.export_daily_data()
        historical_df = self.export_historical_data()
        summary_df = self.export_summary_data()
        
        # エクスポート結果のサマリー
        logger.info("=" * 50)
        logger.info("エクスポート完了サマリー:")
        logger.info(f"日次データ: {len(daily_df) if daily_df is not None else 0}件")
        logger.info(f"履歴データ: {len(historical_df) if historical_df is not None else 0}件")
        logger.info(f"サマリーデータ: {len(summary_df) if summary_df is not None else 0}件")
        logger.info("=" * 50)
        
        return {
            'daily': daily_df,
            'historical': historical_df,
            'summary': summary_df
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
    exporter = LookerStudioExporter(symbols)
    
    # 実行モードを選択
    print("Looker Studio用データエクスポート")
    print("=" * 40)
    print("1. 日次データのみエクスポート")
    print("2. 履歴データのみエクスポート")
    print("3. サマリーデータのみエクスポート")
    print("4. すべてのデータをエクスポート")
    
    choice = input("選択 (1-4): ").strip()
    
    if choice == "1":
        exporter.export_daily_data()
    elif choice == "2":
        exporter.export_historical_data()
    elif choice == "3":
        exporter.export_summary_data()
    elif choice == "4":
        exporter.export_all_data()
    else:
        print("無効な選択です。すべてのデータをエクスポートします。")
        exporter.export_all_data()

if __name__ == "__main__":
    main()
