# 🧪 Infrastructure Alchemist (インフラの錬金術師)

「壊れても笑っていられるインフラ」を、AIが自律進化（遺伝的アルゴリズム）によって錬成する変態的実験プロジェクトです。

本リポジトリには、2つの異なる進化実験のプロセスが記録されています。

## 📖 実験の概要

Gemini APIを利用し、AI自身にTerraformコードの作成・評価・次世代への継承を行わせることで、「最も安く、かつ最も頑丈なインフラ」を自動で模索させました。

### 👉 [**解説記事（Phase 2: Cloud Run自動デプロイ編）はこちら！**](https://zenn.dev/miki_mini/articles/3c92efc110f6bd)
### 👉 [**解説記事（Phase 1: VM自律進化編）はこちら！**](https://zenn.dev/miki_mini/articles/59044eddaa12cd)

---

## 🧬 進化のプロセス（2つのアプローチ）

### Phase 1: VMの自己修復と構文エラーフィードバック (`evolution_agent_vm.py`)
- **目的**: 究極の低コスト（Spot VM）と、消されても自動で蘇るレジリエンス（MIG）を両立するインフラの探索。
- **進化手法**: 人間がベースコードを与え、AIが「コスト削減・レジリエンス・美学」を基準に進化案を生成。Pythonが `terraform validate` で構文チェックを行い、エラーが出たらAIにフィードバックして自己修復させる構成でした。
- **到達形態**: 外部IPを一切持たないIAP経由アクセスの「不滅の要塞（Gen 9）」に到達。

### Phase 2: サーバーレスの完全デプロイ＆自動テストによる真のループ (`evolution_agent_serverless.py`)
- **目的**: Cloud Run等を用いた「完全なサーバーレス（Scale to Zero = 0円運用）」インフラの実装。
- **進化手法**: **「AIがコード出力 → 実機へ自動デプロイ (`terraform apply`) → PythonでHTTP死活監視 (`requests`) → 結果のスコアをAIへフィードバック → 全てを自動削除 (`terraform destroy`)」** という完全自動ループ（1ループ数分）を実装。
- **GCPの罠との死闘**:
  - 128MiBでの`startup_cpu_boost`発動不可（仕様違反）
  - IAMのEventual Consistency（反映情報の30秒遅延・時空の歪み）に対する `time_sleep`
  - Cloud Run V2のデフォルト保護 (`deletion_protection=false`) エラー
  - Secret Managerのバージョン中身空っぽエラー
- **到達形態 (Gen 8)**: Gen2実行環境の指定、Concurrency 80の極限チューニングを用いた「0円運用の最高峰」。
- **限界突破 (Gen 9)**: 「予算無制限」のルールを与えた途端、AIがグローバルロードバランサーとWAF（Cloud Armor）を召喚。しかしGCPの「ルーター反映まで10分かかる」という巨大な壁に激突し自爆。

---

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

# 依存モジュールのインストール
pip install google-generativeai python-dotenv requests
```

### AIエージェントの起動（自律進化の開始）
```bash
# .env ファイルに GEMINI_API_KEY=YOUR_KEY を記述してから実行

# [Phase 1] 構文エラーでの学習編（VM）
python evolution_agent_vm.py

# [Phase 2] 完全なデプロイとHTTPテストループ編（Cloud Run等）
python evolution_agent_serverless.py
```

### インフラの実機デプロイ（手動で行う場合）
もし自動スクリプトではなく手動で試す場合は、各種ディレクトリ（`serverless_workspace`等）で以下を実行してください。

```bash
# tfvarsファイルにGCPのプロジェクトIDを記述
echo 'project_id = "YOUR_PROJECT_ID"' > terraform.tfvars

terraform init
terraform apply
```

## ⚠️ カオスエンジニアリングの推奨事項

本プロジェクトのインフラは「壊れること」を前提に作られています。

- **VM編**: IAP経由でVMにSSH潜入し、ターミナルから `sudo poweroff` を叩き、MIGが新しいクローンを秒で蘇らせるのを観察してください。
- **Cloud Run編**: Cloud Runの自動デプロイループを回し続け、AIが自らどのようにコードを書き換え、時にGCPの謎のエラーにハマり、そしてプロンプトからのフィードバックを受けて学習していくかのドラマを楽しんでください。

---
*Created by Miki & Gemini / Claude*
