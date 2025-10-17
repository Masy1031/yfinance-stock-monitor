#!/usr/bin/env python3
"""
リアルタイム株価取得ツール
yfinanceを使用して株価データを取得し、Looker Studio用のCSVファイルに保存します。
"""

import yfinance as yf
import pandas as pd
import time
import datetime
import os
import logging
from typing import List, Dict, Optional
import json

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stock_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StockPriceMonitor:
    """リアルタイム株価監視クラス"""
    
    def __init__(self, symbols: List[str], output_dir: str = "data"):
        """
        初期化
        
        Args:
            symbols: 監視する株式シンボルのリスト
            output_dir: データ保存ディレクトリ
        """
        self.symbols = symbols
        self.output_dir = output_dir
        self.data_file = os.path.join(output_dir, "stock_prices.csv")
        
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        
        # CSVファイルのヘッダーを初期化
        self._initialize_csv()
    
    def _initialize_csv(self):
        """CSVファイルのヘッダーを初期化"""
        if not os.path.exists(self.data_file):
            headers = [
                'timestamp', 'symbol', 'price', 'change', 'change_percent',
                'volume', 'market_cap', 'previous_close', 'open', 'high', 'low',
                'day_range', 'fifty_two_week_high', 'fifty_two_week_low'
            ]
            df = pd.DataFrame(columns=headers)
            df.to_csv(self.data_file, index=False, encoding='utf-8-sig')
            logger.info(f"CSVファイルを初期化しました: {self.data_file}")
    
    def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """
        単一株式のデータを取得
        
        Args:
            symbol: 株式シンボル
            
        Returns:
            株式データの辞書、エラーの場合はNone
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                logger.warning(f"{symbol}: データが取得できませんでした")
                return None
            
            # 最新の価格データを取得
            latest = hist.iloc[-1]
            
            # データを整理
            data = {
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': symbol,
                'price': round(latest['Close'], 2),
                'change': round(latest['Close'] - latest['Open'], 2),
                'change_percent': round(((latest['Close'] - latest['Open']) / latest['Open']) * 100, 2),
                'volume': int(latest['Volume']),
                'market_cap': info.get('marketCap', 'N/A'),
                'previous_close': round(latest['Open'], 2),
                'open': round(latest['Open'], 2),
                'high': round(latest['High'], 2),
                'low': round(latest['Low'], 2),
                'day_range': f"{round(latest['Low'], 2)} - {round(latest['High'], 2)}",
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A')
            }
            
            return data
            
        except Exception as e:
            logger.error(f"{symbol}のデータ取得中にエラーが発生しました: {str(e)}")
            return None
    
    def get_all_stock_data(self) -> List[Dict]:
        """
        すべての株式データを取得
        
        Returns:
            株式データのリスト
        """
        all_data = []
        
        for symbol in self.symbols:
            logger.info(f"{symbol}のデータを取得中...")
            data = self.get_stock_data(symbol)
            if data:
                all_data.append(data)
            time.sleep(1)  # API制限を避けるため
        
        return all_data
    
    def save_to_csv(self, data: List[Dict]):
        """
        データをCSVファイルに保存
        
        Args:
            data: 保存するデータのリスト
        """
        if not data:
            logger.warning("保存するデータがありません")
            return
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(self.data_file, mode='a', header=False, index=False, encoding='utf-8-sig')
            logger.info(f"{len(data)}件のデータをCSVファイルに保存しました")
        except Exception as e:
            logger.error(f"CSVファイル保存中にエラーが発生しました: {str(e)}")
    
    def run_continuous_monitoring(self, interval_minutes: int = 5):
        """
        継続的な監視を実行
        
        Args:
            interval_minutes: データ取得間隔（分）
        """
        logger.info(f"株価監視を開始します。間隔: {interval_minutes}分")
        logger.info(f"監視対象: {', '.join(self.symbols)}")
        
        try:
            while True:
                logger.info("=" * 50)
                logger.info(f"データ取得開始: {datetime.datetime.now()}")
                
                # データを取得
                data = self.get_all_stock_data()
                
                # CSVに保存
                self.save_to_csv(data)
                
                # 次の取得まで待機
                logger.info(f"次の取得まで{interval_minutes}分待機します...")
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            logger.info("監視を停止しました")
        except Exception as e:
            logger.error(f"監視中にエラーが発生しました: {str(e)}")
    
    def run_single_fetch(self):
        """一回だけデータを取得して保存"""
        logger.info("一回限りのデータ取得を実行します")
        data = self.get_all_stock_data()
        self.save_to_csv(data)
        logger.info("データ取得完了")

def main():
    """メイン関数"""
    # 監視する株式シンボル（例：日本株、米国株）
    symbols = [
        'AAPL',  # Apple
        'MSFT',  # Microsoft
        'GOOGL', # Google
        'AMZN',  # Amazon
        'TSLA',  # Tesla
        '7203.T', # トヨタ自動車
        '6758.T', # ソニー
        '9984.T', # ソフトバンクグループ
    ]
    
    # 監視インスタンスを作成
    monitor = StockPriceMonitor(symbols)
    
    # 実行モードを選択
    print("実行モードを選択してください:")
    print("1. 一回限りのデータ取得")
    print("2. 継続的な監視（5分間隔）")
    print("3. 継続的な監視（カスタム間隔）")
    
    choice = input("選択 (1-3): ").strip()
    
    if choice == "1":
        monitor.run_single_fetch()
    elif choice == "2":
        monitor.run_continuous_monitoring(interval_minutes=5)
    elif choice == "3":
        try:
            interval = int(input("間隔（分）を入力してください: "))
            monitor.run_continuous_monitoring(interval_minutes=interval)
        except ValueError:
            print("無効な入力です。デフォルトの5分間隔で実行します。")
            monitor.run_continuous_monitoring(interval_minutes=5)
    else:
        print("無効な選択です。一回限りのデータ取得を実行します。")
        monitor.run_single_fetch()

if __name__ == "__main__":
    main()
