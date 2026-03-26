import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# 1. 環境設定と安全装置
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-3-flash-preview') # 2026年最新のFlashモデル

# 進化の記録用フォルダ
Path("./generations").mkdir(exist_ok=True)

def autonomous_evolution(current_code, generation):
    print(f"🎤 第 {generation+1} 世代：AI選抜総選挙を開始します（候補3案）...")

    # 審査基準（適応度関数）をプロンプトに詳しく書く
    prompt = f"""
    あなたは「超一流のインフラ審査員」兼「錬金術師」です。
    以下のコードを元に、さらに進化した「3つの異なる進化案（A, B, C）」を内部で作成し、
    その中で【最もコストが安く、かつ頑丈で、コードが美しい1案】だけを最終的に出力してください。

    【現在のコード (Gen {generation})】
    {current_code}

    【審査員のこだわり（採点基準）】
    1. 究極のコスト0円：Cloud RunやCloud Functions等のサーバーレスを駆使し、アクセスゼロなら課金もゼロ（Scale to Zero）になるか？（100点）
    2. インフラを持たない身軽さ：VMサーバーを一切使わず、マネージドサービスだけで構成できるか？（100点）
    3. 美学：不要なリソースが一つもなく、息を呑むほど美しい最先端クラウドネイティブ構成か？（100点）


    【出力形式】
    1. Mikiさんへの報告：新しく進化したポイントを、お仕事やお買い物に例えて3行で。
    2. 審査員コメント：なぜこの案が3個の中から選ばれたのかの理由。
    3. Terraformコード：当選したコードのみ。

    ⚠️【絶対厳守】出力は、最終的に選ばれた1案のTerraformコード（.tf）のみを返してください。
    「Mikiさんへの報告」や「審査員コメント」も含め、LLMからの返答メッセージはすべて、Terraformファイル内のコメント（`#`からはじまる行）としてコードの先頭に書いてください。平文での返答は一切不要です。
    """

    try:
        response = model.generate_content(prompt)
        new_code = response.text.replace("```hcl", "").replace("```", "").strip()
        return new_code
    except Exception as e:
        return f"💥 錬金失敗（爆発）: {str(e)}"

# 3. 実験の実行
if __name__ == "__main__":
    import re

    # 最新の世代のファイルを探す
    generations_dir = Path("./generations")
    max_gen = 0

    if generations_dir.exists():
        for file_path in generations_dir.glob("serverless_gen_*.tf"):
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
        base_file = generations_dir / f"serverless_gen_{max_gen}.tf"

    print(f"📄 ベースとなるファイル: {base_file} (第 {max_gen} 世代)")

    with open(base_file, "r", encoding="utf-8") as f:
        current_gen_code = f.read()

    # 進化（次の世代へ）！
    next_gen = max_gen + 1
    new_gen_code = autonomous_evolution(current_gen_code, max_gen)

    # 結果を保存
    next_gen_file = generations_dir / f"serverless_gen_{next_gen}.tf"
    with open(next_gen_file, "w", encoding="utf-8") as f:
        f.write(new_gen_code)

    print(f"✨ 進化完了！ {next_gen_file} を確認してください。")
    print(f"💬 コミットメッセージ案: 'Generation {next_gen}: Evolved from {base_file.name}'")