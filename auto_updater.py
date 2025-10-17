#!/usr/bin/env python3
"""
自動更新スケジューラー
指定した間隔で株価データを自動取得し、Looker Studio用データを更新します。
"""

import schedule
import time
import logging
import datetime
import os
import sys
from looker_studio_optimized import LookerStudioOptimized
import threading
import signal

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoUpdater:
    """自動更新スケジューラー"""
    
    def __init__(self, symbols: list, update_interval_minutes: int = 15):
        """
        初期化
        
        Args:
            symbols: 監視する株式シンボルのリスト
            update_interval_minutes: 更新間隔（分）
        """
        self.symbols = symbols
        self.update_interval = update_interval_minutes
        self.exporter = LookerStudioOptimized(symbols)
        self.running = False
        self.last_update = None
        
        # シグナルハンドラーを設定
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラー（Ctrl+C対応）"""
        logger.info("停止シグナルを受信しました。安全に停止します...")
        self.running = False
        sys.exit(0)
    
    def update_data(self):
        """データを更新"""
        try:
            logger.info("=" * 60)
            logger.info(f"データ更新を開始: {datetime.datetime.now()}")
            
            # データをエクスポート
            result = self.exporter.export_all_data(upload_to_sheets=True)
            
            if result:
                self.last_update = datetime.datetime.now()
                logger.info("データ更新が完了しました")
                
                # 更新結果をログに記録
                for data_type, df in result.items():
                    if df is not None:
                        logger.info(f"{data_type}: {len(df)}件のデータを更新")
            else:
                logger.error("データ更新に失敗しました")
                
        except Exception as e:
            logger.error(f"データ更新中にエラーが発生しました: {str(e)}")
    
    def schedule_updates(self):
        """スケジュールを設定"""
        # 指定した間隔で更新をスケジュール
        schedule.every(self.update_interval).minutes.do(self.update_data)
        
        # 毎日午前9時に更新（市場開始時）
        schedule.every().day.at("09:00").do(self.update_data)
        
        # 毎日午後4時に更新（市場終了時）
        schedule.every().day.at("16:00").do(self.update_data)
        
        logger.info(f"スケジュールを設定しました:")
        logger.info(f"- {self.update_interval}分間隔での更新")
        logger.info(f"- 毎日午前9時（市場開始時）")
        logger.info(f"- 毎日午後4時（市場終了時）")
    
    def run(self):
        """スケジューラーを実行"""
        self.running = True
        self.schedule_updates()
        
        # 初回実行
        logger.info("初回データ更新を実行します...")
        self.update_data()
        
        logger.info("自動更新スケジューラーを開始しました")
        logger.info("停止するには Ctrl+C を押してください")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("ユーザーによって停止されました")
        except Exception as e:
            logger.error(f"スケジューラー実行中にエラー: {str(e)}")
        finally:
            self.running = False
            logger.info("自動更新スケジューラーを停止しました")
    
    def run_once(self):
        """一回だけ実行"""
        logger.info("一回限りのデータ更新を実行します...")
        self.update_data()
        logger.info("一回限りの更新が完了しました")
    
    def get_status(self):
        """現在のステータスを取得"""
        status = {
            'running': self.running,
            'last_update': self.last_update,
            'next_update': schedule.next_run(),
            'symbols': self.symbols,
            'update_interval': self.update_interval
        }
        return status

def create_service_script():
    """サービス用スクリプトを作成"""
    service_script = """#!/bin/bash
# yfinance自動更新サービス

# 設定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/auto_updater.py"
LOG_FILE="$SCRIPT_DIR/auto_updater.log"
PID_FILE="$SCRIPT_DIR/auto_updater.pid"

# 関数
start_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo "サービスは既に実行中です (PID: $PID)"
            return 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    echo "サービスを開始しています..."
    nohup python3 "$PYTHON_SCRIPT" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "サービスを開始しました (PID: $(cat $PID_FILE))"
}

stop_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo "サービスを停止しています..."
            kill $PID
            rm -f "$PID_FILE"
            echo "サービスを停止しました"
        else
            echo "サービスは実行されていません"
            rm -f "$PID_FILE"
        fi
    else
        echo "PIDファイルが見つかりません"
    fi
}

status_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo "サービスは実行中です (PID: $PID)"
        else
            echo "サービスは停止しています"
            rm -f "$PID_FILE"
        fi
    else
        echo "サービスは停止しています"
    fi
}

# メイン処理
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 2
        start_service
        ;;
    status)
        status_service
        ;;
    *)
        echo "使用方法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
"""
    
    with open("auto_updater_service.sh", "w", encoding="utf-8") as f:
        f.write(service_script)
    
    # 実行権限を付与
    os.chmod("auto_updater_service.sh", 0o755)
    logger.info("サービス用スクリプトを作成しました: auto_updater_service.sh")

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
    
    print("yfinance自動更新スケジューラー")
    print("=" * 50)
    print("1. 一回限りのデータ更新")
    print("2. 自動更新スケジューラーを開始")
    print("3. サービス用スクリプトを作成")
    print("4. カスタム間隔でスケジューラーを開始")
    
    choice = input("選択 (1-4): ").strip()
    
    if choice == "1":
        # 一回限りの更新
        updater = AutoUpdater(symbols)
        updater.run_once()
        
    elif choice == "2":
        # デフォルト間隔（15分）でスケジューラー開始
        updater = AutoUpdater(symbols, update_interval_minutes=15)
        updater.run()
        
    elif choice == "3":
        # サービス用スクリプトを作成
        create_service_script()
        print("\nサービス用スクリプトが作成されました。")
        print("使用方法:")
        print("  ./auto_updater_service.sh start   # サービス開始")
        print("  ./auto_updater_service.sh stop    # サービス停止")
        print("  ./auto_updater_service.sh status  # ステータス確認")
        print("  ./auto_updater_service.sh restart # サービス再起動")
        
    elif choice == "4":
        # カスタム間隔でスケジューラー開始
        try:
            interval = int(input("更新間隔（分）を入力してください: "))
            updater = AutoUpdater(symbols, update_interval_minutes=interval)
            updater.run()
        except ValueError:
            print("無効な入力です。デフォルトの15分間隔で実行します。")
            updater = AutoUpdater(symbols, update_interval_minutes=15)
            updater.run()
    
    else:
        print("無効な選択です。一回限りのデータ更新を実行します。")
        updater = AutoUpdater(symbols)
        updater.run_once()

if __name__ == "__main__":
    main()
