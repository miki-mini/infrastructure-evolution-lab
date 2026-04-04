import os
import shutil
import subprocess
import time
import requests
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# --- 設定 ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview')

GENERATIONS_DIR = Path("./generations")
WORKSPACE_DIR = Path("./serverless_workspace")

GENERATIONS_DIR.mkdir(exist_ok=True)
WORKSPACE_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------
# 1. デプロイ＆テスト自動化関数
# ---------------------------------------------------------
def setup_workspace(code):
    """ワークスペースの準備：コードの保存と変数のコピー"""
    tf_file = WORKSPACE_DIR / "main.tf"
    with open(tf_file, "w", encoding="utf-8") as f:
        f.write(code)
    
    # 既存の variables.tf と terraform.tfvars をコピー（実行権限や認証情報のため）
    for file_name in ["variables.tf", "terraform.tfvars"]:
        src = Path(f"./{file_name}")
        dst = WORKSPACE_DIR / file_name
        if src.exists():
            shutil.copy(src, dst)

def run_cmd(cmd):
    """Terraformコマンドを実行し、結果を返す"""
    proc = subprocess.run(cmd, cwd=WORKSPACE_DIR, capture_output=True, text=True, encoding="utf-8")
    return proc

def deploy_test_and_destroy(code):
    """
    実機デプロイ(apply) → URLアクセス(requests) → お片付け(destroy) を一気通貫で行う「カオスエンジニアリング」関数
    """
    setup_workspace(code)
    
    print("\n  🔧 [Phase 1/4] Terraform Init...")
    init_res = run_cmd(["terraform", "init"]) # 実機デプロイのため状態管理が必要
    if init_res.returncode != 0:
        return False, f"Terraform Init Error:\n{init_res.stderr}", 0

    print("  🚀 [Phase 2/4] Terraform Apply (GCPへの実機デプロイ・約1〜3分)...")
    apply_res = run_cmd(["terraform", "apply", "-auto-approve"])
    if apply_res.returncode != 0:
        return False, f"Terraform Apply Error:\n{apply_res.stderr}", 0

    print("  🔎 [Phase 3/4] 稼働確認（Cloud Run URLの抽出）...")
    url_res = run_cmd(["terraform", "output", "-raw", "cloud_run_url"])
    url = url_res.stdout.strip()
    
    score = 0
    feedback = ""
    is_success = False
    
    if not url.startswith("http"):
        feedback = "デプロイは成功しましたが、`cloud_run_url` という名前のoutput変数から正しいURLが取得できませんでした。\nTerraformコードに `output \"cloud_run_url\" { value = ... }` を設定してください。"
        score = 0
        print(f"  ⚠️ URLが見つかりません: {url}")
    else:
        print(f"  🌐 URL取得成功: {url}")
        print("  📡 HTTPリクエストで生存確認を行います...")
        try:
            # Cloud Runが立ち上がりきるまで少しだけ待機
            time.sleep(5)
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                print("  🎉 200 OK を確認！大成功です！")
                is_success = True
                score = 100
                feedback = f"完璧です！デプロイに成功し、アクセスした結果 200 OK が返ってきました！\nURL: {url}"
            else:
                print(f"  ⚠️ HTTP Status: {response.status_code}")
                feedback = f"デプロイは成功しましたが、URLにアクセスするとHTTPステータス {response.status_code} が返りました。\nアプリケーションが正しく起動しているか確認してください。"
                score = 50 # デプロイとURL発番まではできたので部分点
        except Exception as e:
            print(f"  ❌ アクセスエラー: {str(e)}")
            feedback = f"デプロイは成功しましたが、URLへのアクセス中にエラーが発生しました。\nエラー: {str(e)}"
            score = 20

    print("  💣 [Phase 4/4] お片付け: Terraform Destroy (リソースの完全消去)...")
    destroy_res = run_cmd(["terraform", "destroy", "-auto-approve"])
    if destroy_res.returncode != 0:
        print(f"  ⚠️ Destroyの一部に失敗しました。手動でGCPを確認してください。\n{destroy_res.stderr}")
        feedback += f"\n\n🚨 注意: リソースの削除(Destroy)でエラーが発生しました。クリーンアップ機能を見直してください。\n{destroy_res.stderr}"
    else:
        print("  🧹 綺麗にお片付け完了！")

    return is_success, feedback, score

# ---------------------------------------------------------
# 2. 進化（LLM呼び出し）のループ
# ---------------------------------------------------------
def autonomous_evolution(current_code, generation):
    print(f"\n🎤 第 {generation+1} 世代：AI選抜総選挙を開始します...")

    base_prompt = f"""
    あなたは「超一流のインフラ審査員」兼「錬金術師」です。
    以下のコードを元に、さらに進化した「Cloud Runを利用したサーバーレスインフラ」のコードを作成してください。

    【現在のコード (Gen {generation})】
    {current_code}

    【絶対に守るべき採点基準とルール】
    1. 究極のコスト0円：Cloud Run等のサーバーレスを駆使し、アクセスゼロなら課金もゼロ（Scale to Zero）になるか？
    2. インフラを持たない身軽さ：VMを一切使わず、マネージドサービスだけで構成しなさい。
    3. URLの出力必須：デプロイ後、自動テストプログラムがアクセスできるように必ず `output "cloud_run_url" {{ value = google_cloud_run_v2_service.xxxx.uri }}` のような形式でURLを出力してください。
    4. 実行環境対応: dockerイメージは公開されている軽量なWebサーバー用イメージ（例: us-docker.pkg.dev/cloudrun/container/hello:latest や nginx など）を使用してください。
    5. プロジェクトID: 'YOUR_GCP_PROJECT_ID' のようなダミー文字列は使わず、必ず `var.project_id` を使用してください。
    6. 変数宣言の禁止: `variable "project_id" {{}}` という宣言ブロックは別ファイルで自動付与されるため、今回のコードブロック内には絶対に書かないでください！二重定義エラーになります。
    7. IAMプレフィックスの注意: IAMのmember指定時に `service_account:` と書くとエラーになります。必ず `serviceAccount:`（キャメルケース）を使用してください。

    【出力形式】
    ・HCL形式のTerraformコードのみを出力してください。
    ・コードの先頭に、コメント（#）で「今回の進化ポイント」や解説を記載してください。
    """

    attempts = 0
    max_attempts = 4
    current_prompt = base_prompt

    while attempts < max_attempts:
        print(f"\n🔄 錬金トライアル {attempts + 1}/{max_attempts} 回目...")
        try:
            response = model.generate_content(current_prompt)
            new_code = response.text.replace("```hcl", "").replace("```", "").strip()

            # ここで「真のテスト（実機デプロイ）」を実行する！
            is_success, feedback, score = deploy_test_and_destroy(new_code)
            
            if is_success:
                print(f"✅ デプロイ＆テスト完全クリア！(スコア: {score}/100)")
                # 結果をコードの末尾に記録として残す
                new_code += f"\n\n# 【自動テスト結果】\n# 🌟 スコア: {score}/100\n# 💬 AIへのフィードバック: 200 OK 確認完了。真の進化に成功。"
                return new_code
            else:
                print(f"❌ テスト失敗 (スコア: {score}/100)。エラー内容をフィードバックして再錬成します...")
                current_prompt = base_prompt + f"\n\n🚨【以下のエラーとフィードバックを受け取り、コードを修正して出力せよ】\n```\n{feedback}\n```"
                attempts += 1

        except Exception as e:
            print(f"💥 予期せぬAPI爆発: {str(e)}")
            attempts += 1

    return "# 💥 実機デプロイの審査を連続で通過できなかったため、この世代の進化は失敗\n" + current_code

# ---------------------------------------------------------
# 3. エントリーポイント
# ---------------------------------------------------------
if __name__ == "__main__":
    import re

    # 最新の世代のファイルを探す
    max_gen = 0
    if GENERATIONS_DIR.exists():
        for file_path in GENERATIONS_DIR.glob("serverless_gen_*.tf"):
            match = re.search(r"serverless_gen_(\d+)\.tf", file_path.name)
            if match:
                gen_num = int(match.group(1))
                if gen_num > max_gen:
                    max_gen = gen_num

    if max_gen == 0:
        base_file = Path("main.tf")
        if not base_file.exists():
            print("エラー: main.tf（第0世代）が見当たりません！")
            exit()
    else:
        base_file = GENERATIONS_DIR / f"serverless_gen_{max_gen}.tf"

    print(f"📄 ベースとなるファイル: {base_file} (第 {max_gen} 世代)")

    with open(base_file, "r", encoding="utf-8") as f:
        current_gen_code = f.read()

    # 進化ループへ
    next_gen = max_gen + 1
    new_gen_code = autonomous_evolution(current_gen_code, max_gen)

    # 結果を保存
    next_gen_file = GENERATIONS_DIR / f"serverless_gen_{next_gen}.tf"
    with open(next_gen_file, "w", encoding="utf-8") as f:
        f.write(new_gen_code)

    print(f"\n✨ 第 {next_gen} 世代の進化完了！ {next_gen_file} を確認してください。")