# Streamlit ダッシュボード使用ガイド

## 📋 概要

このプロジェクトには2つのStreamlitダッシュボードが含まれています：

1. **`streamlit_dashboard.py`** - 基本的な株価ダッシュボード
2. **`advanced_streamlit_dashboard.py`** - 高度な分析機能付きダッシュボード

## 🚀 クイックスタート

### 1. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 基本的なダッシュボードの実行

```bash
streamlit run streamlit_dashboard.py
```

### 3. 高度なダッシュボードの実行

```bash
streamlit run advanced_streamlit_dashboard.py
```

## 📊 機能一覧

### 基本的なダッシュボード（streamlit_dashboard.py）

#### 🎯 主要機能
- **リアルタイム株価表示**: 現在の株価と変動率
- **インタラクティブチャート**: 価格と取引量の可視化
- **パフォーマンス比較**: 複数銘柄の比較
- **セクター分析**: セクター別パフォーマンス
- **データエクスポート**: CSV形式でのダウンロード

#### 📈 チャート種類
- **個別チャート**: ローソク足チャート + 取引量
- **パフォーマンス比較**: 正規化された価格推移
- **セクター分析**: セクター別平均変動率と取引量

#### ⚙️ 設定オプション
- **銘柄選択**: 複数銘柄の同時監視
- **期間設定**: 1日〜5年の期間選択
- **自動更新**: 指定間隔での自動データ更新

### 高度なダッシュボード（advanced_streamlit_dashboard.py）

#### 🎯 主要機能
- **テクニカル分析**: RSI、MACD、ボリンジャーバンド
- **相関分析**: 株式間の相関マトリックス
- **リスク・リターン分析**: ボラティリティとリターンの関係
- **ポートフォリオ分析**: ポートフォリオ構成の可視化
- **ウォッチリスト**: カスタム銘柄リスト

#### 📈 高度なチャート
- **テクニカル分析チャート**: 移動平均、RSI、MACD、ボリンジャーバンド
- **相関マトリックス**: ヒートマップ形式
- **リスク・リターンスキャッター**: 散布図形式
- **ポートフォリオ構成**: 円グラフ形式

#### 🧭 ナビゲーション
- **タブ形式**: ダッシュボード、テクニカル分析、相関分析、ポートフォリオ、設定
- **サイドバー**: 銘柄選択、期間設定、ウォッチリスト管理

## 🎨 使用方法

### 基本的なダッシュボード

#### 1. 銘柄選択
- サイドバーで監視したい銘柄を選択
- デフォルトで6銘柄が選択済み

#### 2. 期間設定
- データ期間を選択（1日〜5年）
- デフォルトは1ヶ月

#### 3. 自動更新
- チェックボックスで自動更新を有効化
- 更新間隔を10〜300秒で設定

#### 4. チャート表示
- **個別チャート**: 銘柄を選択してローソク足チャートを表示
- **パフォーマンス比較**: 選択した全銘柄の比較
- **セクター分析**: セクター別の分析
- **データテーブル**: 詳細データの表示とCSVダウンロード

### 高度なダッシュボード

#### 1. ナビゲーション
- 上部のタブで機能を切り替え
- 各タブで異なる分析機能を提供

#### 2. テクニカル分析
- 銘柄を選択してテクニカル指標を表示
- 移動平均、RSI、MACD、ボリンジャーバンドを同時表示

#### 3. 相関分析
- 株式間の相関関係をヒートマップで表示
- リスク・リターンの関係を散布図で表示

#### 4. ポートフォリオ分析
- 各銘柄の配分を設定
- ポートフォリオ構成を円グラフで表示

#### 5. ウォッチリスト
- カスタム銘柄を追加・削除
- セッション中に保持

## 🔧 カスタマイズ

### 銘柄の追加・変更

```python
# デフォルト銘柄リストを変更
self.default_symbols = [
    'AAPL', 'MSFT', 'GOOGL',  # 米国株
    '7203.T', '6758.T',       # 日本株
    'YOUR_SYMBOL'             # カスタム銘柄
]
```

### テクニカル指標の追加

```python
def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
    # 新しい指標を追加
    df['STOCH'] = # ストキャスティクス計算
    df['WILLIAMS_R'] = # ウィリアムズ%R計算
    return df
```

### チャートスタイルの変更

```python
# カラーテーマの変更
fig.update_layout(
    template="plotly_dark",  # ダークテーマ
    colorway=['#FF6B6B', '#4ECDC4', '#45B7D1']  # カスタムカラー
)
```

## 📱 レスポンシブデザイン

### モバイル対応
- 自動的にモバイル表示に最適化
- タッチ操作に対応
- 縦スクロールでの操作

### デスクトップ対応
- ワイドレイアウトで複数チャートを同時表示
- サイドバーでの設定変更
- キーボードショートカット対応

## 🚀 デプロイ

### Streamlit Cloud

1. **GitHubリポジトリを準備**
2. **Streamlit Cloudにアクセス**: https://share.streamlit.io/
3. **リポジトリを接続**
4. **アプリケーションファイルを指定**

### ローカルサーバー

```bash
# カスタムポートで実行
streamlit run streamlit_dashboard.py --server.port 8501

# 外部アクセスを許可
streamlit run streamlit_dashboard.py --server.address 0.0.0.0
```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.address", "0.0.0.0"]
```

## 🔍 トラブルシューティング

### よくある問題

#### 1. データが取得できない
```
エラー: データが取得できませんでした
```

**解決方法**:
- インターネット接続を確認
- 銘柄シンボルが正しいか確認
- Yahoo Financeのサービス状況を確認

#### 2. チャートが表示されない
```
エラー: チャートの描画に失敗しました
```

**解決方法**:
- ブラウザのJavaScriptを有効化
- ブラウザのキャッシュをクリア
- 別のブラウザで試行

#### 3. パフォーマンスが遅い
```
警告: アプリケーションの応答が遅い
```

**解決方法**:
- 監視銘柄数を減らす
- データ期間を短くする
- 自動更新間隔を長くする

### ログの確認

```bash
# Streamlitのログを確認
streamlit run streamlit_dashboard.py --logger.level debug
```

## 📊 パフォーマンス最適化

### データキャッシュ

```python
@st.cache_data
def get_stock_data(symbol: str, period: str):
    # データ取得処理
    return data
```

### セッション状態の活用

```python
# セッション状態でデータを保持
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = {}
```

### 非同期処理

```python
import asyncio

async def fetch_multiple_stocks(symbols):
    # 複数銘柄の並列取得
    tasks = [get_stock_data(symbol) for symbol in symbols]
    return await asyncio.gather(*tasks)
```

## 🔐 セキュリティ

### API制限の考慮
- Yahoo Finance APIの制限を遵守
- 適切な間隔でのデータ取得
- エラーハンドリングの実装

### データの取り扱い
- 機密情報の除外
- データの暗号化（必要に応じて）
- アクセス制御の実装

## 📚 参考リンク

- [Streamlit公式ドキュメント](https://docs.streamlit.io/)
- [Plotly公式ドキュメント](https://plotly.com/python/)
- [yfinance公式ドキュメント](https://pypi.org/project/yfinance/)
- [Streamlit Cloud](https://share.streamlit.io/)

## 🤝 貢献

バグ報告や機能追加の提案は、GitHubのIssuesでお知らせください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。
