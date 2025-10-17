# GitHub アップロード手順書

このプロジェクトをGitHubにアップロードするための詳細な手順を説明します。

## 📋 事前準備

### 1. GitHubアカウントの作成
- [GitHub](https://github.com/)にアクセス
- アカウントを作成（まだの場合）

### 2. Gitの設定
```bash
# ユーザー名とメールアドレスを設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 🚀 アップロード手順

### 方法1: コマンドラインを使用（推奨）

#### ステップ1: リポジトリの初期化
```bash
# プロジェクトディレクトリで実行
git init
```

#### ステップ2: ファイルをステージング
```bash
# すべてのファイルを追加
git add .

# または特定のファイルのみ追加
git add README.md requirements.txt *.py
```

#### ステップ3: 初回コミット
```bash
git commit -m "Initial commit: yfinance stock monitor project"
```

#### ステップ4: GitHubでリポジトリを作成
1. GitHubにログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ名を入力（例：`yfinance-stock-monitor`）
4. 説明を追加（例：`Real-time stock price monitoring tool with Looker Studio integration`）
5. Public/Privateを選択
6. 「Create repository」をクリック

#### ステップ5: リモートリポジトリと接続
```bash
# リモートリポジトリを追加（URLは実際のリポジトリURLに置き換え）
git remote add origin https://github.com/your-username/yfinance-stock-monitor.git

# メインブランチを設定
git branch -M main

# 初回プッシュ
git push -u origin main
```

### 方法2: GitHub Webインターフェースを使用

#### ステップ1: リポジトリを作成
1. GitHubにログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ名と説明を入力
4. 「Create repository」をクリック

#### ステップ2: ファイルをアップロード
1. リポジトリページで「Add file」→「Upload files」をクリック
2. ファイルをドラッグ&ドロップまたは選択
3. コミットメッセージを入力
4. 「Commit changes」をクリック

## 📁 アップロードするファイル

### 必須ファイル
- `README.md` - プロジェクトの説明
- `requirements.txt` - 依存関係
- `LICENSE` - ライセンス情報
- `*.py` - Pythonスクリプト
- `.gitignore` - Git除外設定

### 除外されるファイル（.gitignoreで設定済み）
- `__pycache__/` - Pythonキャッシュ
- `data/` - データファイル
- `*.log` - ログファイル
- `service_account_key.json` - 機密情報

## 🔧 追加設定

### リポジトリの説明を追加
1. リポジトリページで「Settings」をクリック
2. 「About」セクションで説明を追加
3. ウェブサイトURLやトピックを設定

### ブランチ保護ルールの設定
1. 「Settings」→「Branches」をクリック
2. 「Add rule」をクリック
3. 保護ルールを設定

## 📝 今後の更新手順

### ファイルを更新した場合
```bash
# 変更をステージング
git add .

# コミット
git commit -m "Update: 変更内容の説明"

# プッシュ
git push origin main
```

### 新しい機能を追加した場合
```bash
# 新しいブランチを作成
git checkout -b feature/new-feature

# 変更をコミット
git add .
git commit -m "Add: 新機能の説明"

# ブランチをプッシュ
git push origin feature/new-feature

# GitHubでプルリクエストを作成
```

## ⚠️ 注意事項

### 機密情報の取り扱い
- APIキーやパスワードは絶対にアップロードしない
- `.gitignore`で除外設定を確認
- 既にアップロードしてしまった場合は、GitHubの履歴から削除が必要

### ファイルサイズ制限
- 単一ファイル: 100MB
- リポジトリ全体: 1GB（推奨）
- 大きなファイルはGit LFSを使用

### ライセンスの確認
- 使用しているライブラリのライセンスを確認
- 適切なライセンスファイルを配置

## 🆘 トラブルシューティング

### 認証エラー
```bash
# パーソナルアクセストークンを使用
git remote set-url origin https://your-token@github.com/username/repo.git
```

### プッシュエラー
```bash
# リモートの変更を取得
git pull origin main

# 競合を解決後、再度プッシュ
git push origin main
```

### ファイルが表示されない
- `.gitignore`の設定を確認
- `git status`でファイルの状態を確認
- `git add`でファイルを明示的に追加

## 📚 参考リンク

- [GitHub公式ドキュメント](https://docs.github.com/)
- [Git公式ドキュメント](https://git-scm.com/doc)
- [GitHub CLI](https://cli.github.com/) - コマンドラインでのGitHub操作
