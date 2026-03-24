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

def evolve_infrastructure(current_code, generation):
    print(f"🧬 第 {generation} 世代の錬金術を開始します...")

    # 2. 【適応度関数】をプロンプトに込める
    prompt = f"""
    あなたは「インフラの錬金術師」です。以下のTerraformコードを魔改造して進化させてください。

    【現在のコード (Generation {generation})】
    {current_code}

    【進化のルール（適応度関数）】
    1. コスト削減: スポットVMを活用し、定価課金を徹底的に排除せよ。
    2. 不死身（レジリエンス）: MIG（身代わり製造機）を使い、1台が爆発（終了）しても即座に復活させよ。
    3. ガードレール: 最大インスタンス数は3台まで。プロジェクトIDは変えないこと。

    出力は、改善されたTerraformコード（.tf）のみを返してください。
    余計な説明は一切不要です。
    """

    try:
        response = model.generate_content(prompt)
        new_code = response.text.replace("```hcl", "").replace("```", "").strip()
        return new_code
    except Exception as e:
        return f"💥 錬金失敗（爆発）: {str(e)}"

# 3. 実験の実行
if __name__ == "__main__":
    # 前の世代を読み込む
    base_file = Path("main.tf")
    if not base_file.exists():
        print("エラー: main.tf（第0世代）が見当たりません！")
        exit()

    with open(base_file, "r", encoding="utf-8") as f:
        current_gen_code = f.read()

    # 進化！
    new_gen_code = evolve_infrastructure(current_gen_code, 0)

    # 結果を保存（第1世代として保存）
    next_gen_file = Path(f"./generations/gen_1.tf")
    with open(next_gen_file, "w", encoding="utf-8") as f:
        f.write(new_gen_code)

    print(f"✨ 進化完了！ ./generations/gen_1.tf を確認してください。")
    print(f"💬 コミットメッセージ案: 'Day 1: AI discovered Spot VMs and MIG!'")