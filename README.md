# yfinance リアルタイム株価監視ツール

yfinanceを使用してリアルタイムな株価データを取得し、Looker Studioで可視化するためのPythonツールです。

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![yfinance](https://img.shields.io/badge/yfinance-0.2.66+-green.svg)](https://pypi.org/project/yfinance/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 クイックスタート

```bash
# リポジトリをクローン
git clone https://github.com/your-username/yfinance-stock-monitor.git
cd yfinance-stock-monitor

# 依存関係をインストール
pip install -r requirements.txt

# 株価データを取得
python looker_studio_optimized.py
```

## 機能

- **リアルタイム株価取得**: yfinanceを使用して最新の株価データを取得
- **継続的監視**: 指定した間隔で株価データを自動取得
- **Looker Studio対応**: 可視化に最適化されたデータ形式でエクスポート
- **複数株式対応**: 複数の株式シンボルを同時に監視
- **詳細データ**: 価格、取引量、財務指標、技術指標など豊富なデータを取得

## ファイル構成

```
yfinance/
├── stock_price_monitor.py      # メインの株価監視ツール
├── looker_studio_exporter.py   # Looker Studio用データエクスポーター
├── requirements.txt            # 必要なPythonパッケージ
├── README.md                   # このファイル
├── data/                       # データ保存ディレクトリ（自動作成）
└── looker_data/                # Looker Studio用データ（自動作成）
```

## インストール

### 1. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 基本的な使用方法

#### リアルタイム株価監視

```bash
python stock_price_monitor.py
```

実行すると以下のオプションが表示されます：
- **1. 一回限りのデータ取得**: 現在の株価を一度だけ取得
- **2. 継続的な監視（5分間隔）**: 5分ごとに株価を取得
- **3. 継続的な監視（カスタム間隔）**: 任意の間隔で株価を取得

#### Looker Studio用データエクスポート

```bash
python looker_studio_exporter.py
```

実行すると以下のオプションが表示されます：
- **1. 日次データのみエクスポート**: 現在の詳細データ
- **2. 履歴データのみエクスポート**: 過去の価格履歴
- **3. サマリーデータのみエクスポート**: 簡略化されたデータ
- **4. すべてのデータをエクスポート**: 上記すべて

## 監視対象株式

デフォルトで以下の株式が監視対象に設定されています：

### 米国株
- **AAPL**: Apple Inc.
- **MSFT**: Microsoft Corporation
- **GOOGL**: Alphabet Inc. (Google)
- **AMZN**: Amazon.com Inc.
- **TSLA**: Tesla Inc.
- **NVDA**: NVIDIA Corporation
- **META**: Meta Platforms Inc.
- **NFLX**: Netflix Inc.

### 日本株
- **7203.T**: トヨタ自動車株式会社
- **6758.T**: ソニーグループ株式会社
- **9984.T**: ソフトバンクグループ株式会社
- **9432.T**: 日本電信電話株式会社

## データ形式

### リアルタイムデータ（stock_price_monitor.py）

CSVファイルに以下の列が含まれます：

| 列名 | 説明 |
|------|------|
| timestamp | データ取得日時 |
| symbol | 株式シンボル |
| price | 現在価格 |
| change | 価格変動 |
| change_percent | 価格変動率（%） |
| volume | 取引量 |
| market_cap | 時価総額 |
| previous_close | 前日終値 |
| open | 始値 |
| high | 高値 |
| low | 安値 |
| day_range | 日中レンジ |
| fifty_two_week_high | 52週高値 |
| fifty_two_week_low | 52週安値 |

### Looker Studio用データ（looker_studio_exporter.py）

#### 日次データ（daily_stock_data.csv）
詳細な株式情報を含む包括的なデータセット

#### 履歴データ（historical_stock_data.csv）
過去の価格履歴データ

#### サマリーデータ（stock_summary.csv）
可視化に最適化された簡略化されたデータ

## Looker Studioでの可視化

### 1. データソースの設定

1. Looker Studioにログイン
2. 「作成」→「データソース」を選択
3. 「ファイルをアップロード」を選択
4. 生成されたCSVファイルをアップロード

### 2. 推奨チャート

#### ダッシュボード
- **株価トレンド**: 時系列での価格変動
- **セクター別パフォーマンス**: セクターごとの平均変動率
- **取引量分析**: 取引量と価格変動の関係
- **リスク分析**: ボラティリティとベータ値

#### 個別株式分析
- **価格チャート**: 日中の価格変動
- **取引量チャート**: 取引量の推移
- **財務指標**: P/E比、時価総額など
- **パフォーマンス比較**: 複数株式の比較

### 3. データ更新

- **手動更新**: スクリプトを実行してCSVファイルを再生成
- **自動更新**: スケジューラーを使用して定期実行（要設定）

## カスタマイズ

### 監視対象株式の変更

`stock_price_monitor.py`と`looker_studio_exporter.py`の`symbols`リストを編集：

```python
symbols = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'YOUR_SYMBOL',  # 追加したい株式
]
```

### 取得間隔の変更

```python
# 1分間隔で監視
monitor.run_continuous_monitoring(interval_minutes=1)

# 15分間隔で監視
monitor.run_continuous_monitoring(interval_minutes=15)
```

### データ保存先の変更

```python
# カスタムディレクトリに保存
monitor = StockPriceMonitor(symbols, output_dir="my_data")
```

## 注意事項

### API制限
- Yahoo Finance APIには制限があります
- 大量のリクエストを送信する場合は適切な間隔を設定してください
- 商用利用の場合はYahoo Financeの利用規約を確認してください

### データの正確性
- このツールは教育・研究目的で作成されています
- 投資判断には必ず公式のデータソースを確認してください
- データの遅延や不正確性の可能性があります

### 法的免責事項
- このツールは投資アドバイスではありません
- 投資リスクは自己責任で行ってください
- Yahoo Financeの利用規約に従って使用してください

## トラブルシューティング

### よくある問題

#### 1. データが取得できない
```
エラー: データが取得できませんでした
```
**解決方法**: 
- インターネット接続を確認
- 株式シンボルが正しいか確認
- しばらく待ってから再実行

#### 2. パッケージのインストールエラー
```
エラー: No module named 'yfinance'
```
**解決方法**:
```bash
pip install yfinance pandas numpy
```

#### 3. 権限エラー
```
エラー: Permission denied
```
**解決方法**:
- 管理者権限で実行
- ファイルの書き込み権限を確認

### ログファイル

実行時に`stock_monitor.log`ファイルが作成され、詳細なログが記録されます。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能追加の提案は、GitHubのIssuesでお知らせください。

## 参考リンク

- [yfinance公式ドキュメント](https://pypi.org/project/yfinance/)
- [Looker Studio公式サイト](https://lookerstudio.google.com/)
- [Yahoo Finance利用規約](https://policies.yahoo.com/us/en/yahoo/terms/otos/index.htm)
