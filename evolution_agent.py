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

    【今回の進化指令（適応度関数）】
    1. コストの極限追求: 月額料金を「うまい棒」数本分でも安くする方法を考えよ。
    2. 復元力の強化: Googleの全データセンターが爆発しても、30秒で復活する執念を見せよ。
    3. ガードレール: 最大インスタンス数は3台まで。プロジェクトIDは変えないこと。
    4. Mikiさんへの解説: 新しく追加した機能を、技術を知らない人でもわかるように、「お買い物」や「お仕事」に例えて3行で報告せよ。

    ⚠️【絶対厳守】出力は、改善されたTerraformコード（.tf）のみを返してください。
    「Mikiさんへの解説」も含め、LLMからの返答メッセージはすべて、Terraformファイル内のコメント（`#`からはじまる行）としてコードの先頭に書いてください。平文での返答は一切不要です。
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
        for file_path in generations_dir.glob("gen_*.tf"):
            match = re.search(r"gen_(\d+)\.tf", file_path.name)
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
        base_file = generations_dir / f"gen_{max_gen}.tf"

    print(f"📄 ベースとなるファイル: {base_file} (第 {max_gen} 世代)")

    with open(base_file, "r", encoding="utf-8") as f:
        current_gen_code = f.read()

    # 進化（次の世代へ）！
    next_gen = max_gen + 1
    new_gen_code = evolve_infrastructure(current_gen_code, max_gen)

    # 結果を保存
    next_gen_file = generations_dir / f"gen_{next_gen}.tf"
    with open(next_gen_file, "w", encoding="utf-8") as f:
        f.write(new_gen_code)

    print(f"✨ 進化完了！ {next_gen_file} を確認してください。")
    print(f"💬 コミットメッセージ案: 'Generation {next_gen}: Evolved from {base_file.name}'")