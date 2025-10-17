#!/usr/bin/env python3
"""
yfinance株価監視ツールの使用例
基本的な使用方法を示すサンプルスクリプトです。
"""

from stock_price_monitor import StockPriceMonitor
from looker_studio_exporter import LookerStudioExporter
import time

def example_basic_usage():
    """基本的な使用例"""
    print("=== 基本的な使用例 ===")
    
    # 監視する株式シンボル
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    # 株価監視インスタンスを作成
    monitor = StockPriceMonitor(symbols, output_dir="example_data")
    
    # 一回限りのデータ取得
    print("一回限りのデータ取得を実行中...")
    monitor.run_single_fetch()
    print("完了！")

def example_looker_studio_export():
    """Looker Studio用エクスポートの例"""
    print("\n=== Looker Studio用エクスポート例 ===")
    
    # 監視する株式シンボル
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
    
    # エクスポーターを作成
    exporter = LookerStudioExporter(symbols, output_dir="example_looker_data")
    
    # 日次データをエクスポート
    print("日次データをエクスポート中...")
    daily_data = exporter.export_daily_data()
    
    if daily_data is not None:
        print(f"エクスポート完了: {len(daily_data)}件のデータ")
        print("\n取得したデータのサンプル:")
        print(daily_data[['symbol', 'company_name', 'current_price', 'change_percent']].head())
    
    # 履歴データをエクスポート
    print("\n履歴データをエクスポート中...")
    historical_data = exporter.export_historical_data(period="5d")
    
    if historical_data is not None:
        print(f"履歴データエクスポート完了: {len(historical_data)}件のデータ")

def example_custom_symbols():
    """カスタム株式シンボルの例"""
    print("\n=== カスタム株式シンボルの例 ===")
    
    # 日本株のみを監視
    japanese_stocks = [
        '7203.T',  # トヨタ自動車
        '6758.T',  # ソニー
        '9984.T',  # ソフトバンクグループ
        '9432.T',  # 日本電信電話
        '6861.T',  # キーエンス
    ]
    
    # 日本株専用の監視インスタンス
    jp_monitor = StockPriceMonitor(japanese_stocks, output_dir="japanese_stocks")
    
    print("日本株のデータを取得中...")
    jp_monitor.run_single_fetch()
    print("日本株データ取得完了！")

def example_continuous_monitoring():
    """継続的監視の例（短時間）"""
    print("\n=== 継続的監視の例（1分間隔、3回実行） ===")
    
    symbols = ['AAPL', 'MSFT']
    monitor = StockPriceMonitor(symbols, output_dir="continuous_example")
    
    print("1分間隔で3回データを取得します...")
    print("（実際の使用では、Ctrl+Cで停止できます）")
    
    # 実際の継続監視の代わりに、3回だけ実行
    for i in range(3):
        print(f"\n--- {i+1}回目のデータ取得 ---")
        monitor.run_single_fetch()
        if i < 2:  # 最後の実行後は待機しない
            print("1分待機中...")
            time.sleep(60)  # 1分待機
    
    print("継続監視の例が完了しました！")

def main():
    """メイン関数 - すべての例を実行"""
    print("yfinance株価監視ツール - 使用例")
    print("=" * 50)
    
    try:
        # 基本的な使用例
        example_basic_usage()
        
        # Looker Studio用エクスポート例
        example_looker_studio_export()
        
        # カスタム株式シンボルの例
        example_custom_symbols()
        
        # 継続的監視の例（短時間）
        # example_continuous_monitoring()  # コメントアウト（時間がかかるため）
        
        print("\n" + "=" * 50)
        print("すべての例が完了しました！")
        print("\n生成されたファイル:")
        print("- example_data/stock_prices.csv")
        print("- example_looker_data/daily_stock_data.csv")
        print("- example_looker_data/historical_stock_data.csv")
        print("- japanese_stocks/stock_prices.csv")
        
    except KeyboardInterrupt:
        print("\n実行が中断されました。")
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()
