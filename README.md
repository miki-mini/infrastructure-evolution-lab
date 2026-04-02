# 🧪 Infrastructure Alchemist (インフラの錬金術師)

「壊れても笑っていられるインフラ」を、AIが自律進化（遺伝的アルゴリズム）によって錬成する変態的実験プロジェクトです。

## 📖 概要

Gemini APIを利用し、AI自身にTerraformコードの作成・構文解析（`terraform validate`）・評価・次世代への継承を行わせることで、「最も安く、かつ最も頑丈なインフラ」を探索させました。

本リポジトリには、その進化の過程（`generations/`）と、進化を司るエージェントスクリプト（`evolution_agent_vm.py`）、そして最終形態（GCPで実際に稼働証明済み）である第9世代のインフラコードが含まれています。

👉 [**詳細は実験の全貌をまとめた技術解説記事をご覧ください**](https://zenn.dev/miki_mini/articles/59044eddaa12cd)

## 🧬 進化の仕組み（Genetic IaC）

1. **シード作成**: 人間がベースとなるTerraformコードを与える
2. **突然変異**: Gemini APIが「コスト削減・レジリエンス・美学」を基準に3パターンの進化案を内部で生成
3. **門番（バリデーション）**: Pythonエージェントが `terraform validate` による文法チェックを実施。エラーならエラー文をGeminiにフィードバックし、最大3回まで自己修復させる
4. **自然選択**: 最も美しく採点が高かった1案を次世代の「親」として採用し、ループを繰り返す

## 🏰 最終到達形態：君主の自動人形（Gen 9）

第9世代（`vm_gen_9.tf`）にて、AIは以下の「不滅の要塞インフラ（The Sovereign Automaton）」に到達しました。

- **Spot VM (e2-micro)**: コストを限界まで削減
- **MIG (マネージド・インスタンス・グループ)**: GoogleにVMを強制終了されても、数秒で新品のクローンを自動錬成（究極のオートヒーリング）
- **外部IPの完全排除（沈黙の美学）**: インターネットからの直接アクセスを遮断し、Cloud NATで安全に外部と通信
- **IAPハッキング**: 鉄壁のファイアウォールの裏にある内部Webサーバーに対し、IAP経由のSSHポートフォワーディングでのみアクセス可能

## 🚀 使い方

### 前提条件
- Terraform のインストール
- Google Cloud CLI (`gcloud` コマンド) のインストールと認証設定
- Python 3.9 以上
- Gemini API Key

### セットアップ
```bash
# リポジトリのクローン
git clone https://github.com/miki-mini/infrastructure-evolution-lab.git
cd infrastructure-evolution-lab

# 依存モジュールのインストール (google-generativeai 等)
pip install google-generativeai python-dotenv
```

### AIエージェントの起動（自律進化の開始）
```bash
# .env ファイルに GEMINI_API_KEY=YOUR_KEY を記述してから実行
python evolution_agent_vm.py
```

### インフラの実機デプロイ（GCP）
```bash
# tfvarsファイルにGCPのプロジェクトIDを記述
echo 'project_id = "YOUR_PROJECT_ID"' > terraform.tfvars

terraform init
terraform plan
terraform apply
```

## ⚠️ カオスエンジニアリングの推奨事項

このインフラの「真のレジリエンス（死と再生）」を味わうためには、GCPの管理画面から行儀よくVMを削除するのではなく、以下の荒療治を推奨します。

1. IAP経由でVMの内部にSSH潜入する
2. ターミナルから `sudo poweroff` を叩き、物理電源を引き抜く
3. MIGの死活監視ロボットが異常を検知し、数秒後に「全く新しい仮想ディスクを持った新品のクローン」を自動で錬成する様をGCPコンソールから見守る

---
*Created by Miki & Gemini / Claude*
