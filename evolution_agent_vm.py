import os
import subprocess
import tempfile
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv# 1. 環境設定と安全装置
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview') # 2026年最新のFlashモデル

# 進化の記録用フォルダ
Path("./generations").mkdir(exist_ok=True)

def validate_terraform(code):
    """
    採点前の門番：terraform validate の結果を返す
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tf_file = Path(tmpdir) / "main.tf"
        with open(tf_file, "w", encoding="utf-8") as f:
            f.write(code)
        
        # init needed for validate
        init_proc = subprocess.run(["terraform", "init", "-backend=false"], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8")
        if init_proc.returncode != 0:
            return False, f"Terraform Init Error:\n{init_proc.stderr}"
            
        val_proc = subprocess.run(["terraform", "validate"], cwd=tmpdir, capture_output=True, text=True, encoding="utf-8")
        if val_proc.returncode != 0:
            return False, f"Terraform Validate Error:\n{val_proc.stderr}"
            
        return True, "Valid"

def autonomous_evolution(current_code, generation):
    print(f"🎤 第 {generation+1} 世代：AI選抜総選挙を開始します（候補3案）...")

    base_prompt = f"""
    あなたは「超一流のインフラ審査員」兼「錬金術師」です。
    以下のコードを元に、さらに進化した「3つの異なる進化案（A, B, C）」を内部で作成し、
    その中で【最もコストが安く、かつ頑丈で、コードが美しい1案】だけを最終的に出力してください。

    【現在のコード (Gen {generation})】
    {current_code}

    【審査員のこだわり（採点基準）】
    1. 泥臭いコスト削減：Spot VMを必ず維持しつつ、VM構成の限界まで無駄を削ぎ落としているか？（100点）
    ※Cloud Runなどのサーバーレスへ転生する「逃げ」は禁止とする。
    2. 頑丈さ：多重ゾーンのMIG（自動修復）が設定されており、Googleの気まぐれでVMを消されても秒で蘇るか？（100点）
    3. 美学：無駄な外部IPを持たず、洗練された「不死身の拠点」になっているか？（100点）


    【出力形式】
    1. Mikiさんへの報告：新しく進化したポイントを、お仕事やお買い物に例えて3行で。
    2. 審査員コメント：なぜこの案が3個の中から選ばれたのかの理由。
    3. Terraformコード：当選したコードのみ。

    ⚠️【絶対厳守】出力は、最終的に選ばれた1案のTerraformコード（.tf）のみを返してください。
    「Mikiさんへの報告」や「審査員コメント」も含め、LLMからの返答メッセージはすべて、Terraformファイル内のコメント（`#`からはじまる行）としてコードの先頭に書いてください。平文での返答は一切不要です。
    """

    attempts = 0
    max_attempts = 3
    current_prompt = base_prompt

    while attempts < max_attempts:
        print(f"🔄 錬金トライアル {attempts + 1}/{max_attempts} 回目...")
        try:
            response = model.generate_content(current_prompt)
            new_code = response.text.replace("```hcl", "").replace("```", "").strip()
            
            # 検証の門番を通す
            is_valid, error_msg = validate_terraform(new_code)
            if is_valid:
                print("✅ 門番の審査をパスしました（Syntax & Validate OK）")
                return new_code
            else:
                print(f"❌ 門番の審査で弾かれました。エラー内容をフィードバックして再錬成します...")
                print(error_msg[:300] + "..." if len(error_msg) > 300 else error_msg)
                
                # AIにエラーを教えて修正させる
                current_prompt = base_prompt + f"\\n\\n🚨【先ほどの出力で以下のTerraformエラーが発生しました。エラーを修正して再度出力せよ】\\n```\\n{error_msg}\\n```"
                attempts += 1
                
        except Exception as e:
            print(f"💥 予期せぬAPI爆発: {str(e)}")
            attempts += 1
            
    return "# 💥 門番の審査を3回連続で通過できなかったため、この世代の進化は失敗（元のコードを引き継ぎます）\\n" + current_code

# 3. 実験の実行
if __name__ == "__main__":
    import re

    # 最新の世代のファイルを探す
    generations_dir = Path("./generations")
    max_gen = 0

    if generations_dir.exists():
        for file_path in generations_dir.glob("vm_gen_*.tf"):
            match = re.search(r"vm_gen_(\d+)\.tf", file_path.name)
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
        base_file = generations_dir / f"vm_gen_{max_gen}.tf"

    print(f"📄 ベースとなるファイル: {base_file} (第 {max_gen} 世代)")

    with open(base_file, "r", encoding="utf-8") as f:
        current_gen_code = f.read()

    # 進化（次の世代へ）！
    next_gen = max_gen + 1
    new_gen_code = autonomous_evolution(current_gen_code, max_gen)

    # 結果を保存
    next_gen_file = generations_dir / f"vm_gen_{next_gen}.tf"
    with open(next_gen_file, "w", encoding="utf-8") as f:
        f.write(new_gen_code)

    print(f"✨ 進化完了！ {next_gen_file} を確認してください。")
    print(f"💬 コミットメッセージ案: 'Generation {next_gen}: Evolved from {base_file.name}'")