# 仮想通貨価格リアルタイム監視システム

## プロジェクト内容
CoinGecko APIを使用して仮想通貨の価格をリアルタイムで監視するシステムです。複数の仮想通貨の価格変動を継続的に追跡し、変動があった場合のみ表示する効率的な監視機能を備えています。Pythonを使ったAPI連携とリアルタイム処理技術を学習することを目的として実装しました。

## プロジェクト構成
```
crypto_price_monitor/
├── price_tracker.py        # メインプログラム
├── requirements.txt         # 依存関係管理
├── README.md               # プロジェクト説明書
└── .gitignore              # Git除外ファイル設定
```

## 必要要件/開発環境
- **Python 3.7以上**
- **インターネット接続** (API通信のため)
- **VSCode** (開発環境)
- **Git** (バージョン管理)

### 使用ライブラリ
- **requests 2.32.3** HTTPリクエスト処理

## 機能
- **リアルタイム価格監視** 複数通貨の同時監視機能
- **価格変動検知** 変動があった場合のみ表示
- **カラー表示** 上昇・下降を色で視覚化
- **統計情報管理** 価格履歴の統計分析
- **データ保存機能** 監視結果のログ出力
- **エラーハンドリング** API制限や接続エラーへの対応
- **設定カスタマイズ** 監視間隔や対象通貨の変更

## 実行方法

### 1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/crypto_price_monitor.git
cd crypto_price_monitor
```

### 2. 仮想環境の作成・アクティベート
**Windows**
```bash
python -m venv myenv
myenv\Scripts\activate
```

**macOS**
```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. プログラムの実行
```bash
python price_tracker.py
```

実行後、ビットコイン、イーサリアム、リップルの価格監視が開始されます。
停止するには Ctrl+C を押してください。

## API制限について
無料プランでは10-30回/分のAPI制限があるため、監視間隔は60秒に設定されています。

## 開発者
YuYu 
