import os
import requests
import subprocess
import json

# === إعدادات الأمان والموديل ===
SAFETY_THRESHOLD = 0.75  # حماية: يمنع حذف أكثر من 25% من الكود
# اسم الموديل كما طلبته بالضبط من OpenRouter
MODEL_ID = "qwen/qwen3-coder:free" 

def get_file_size(path):
    return os.path.getsize(path) if os.path.exists(path) else 0

def run_git_cmd(cmds):
    for cmd in cmds:
        print(f"Executing: {cmd}")
        subprocess.run(cmd, shell=True, check=False)

def solve_with_qwen():
    api_key = os.getenv("OPENROUTER_API_KEY")
    token = os.getenv("MY_ACCESS_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY is missing.")
        return

    # قراءة سجل الأخطاء
    if not os.path.exists("universal_error.log"):
        print("No error log found.")
        return

    with open("universal_error.log", "r") as f:
        error_context = f.read()[-6000:] # Qwen3 يتحمل سياقاً أكبر (Context)

    # البرومبت الموجه لـ Qwen3 خصيصاً
    prompt = f"""
    You are an Autonomous AI DevOps Agent powered by Qwen3.
    Target: Fix the build error in this repository.
    
    ERROR LOG:
    {error_context}

    STRICT RULES:
    1. Analyze the logic. Identify the specific file causing the failure.
    2. Rewrite the FULL content of that file with the fix.
    3. DO NOT remove existing features. Only fix the bug.
    4. If the error implies missing config (like gradle wrapper), create it.
    
    OUTPUT FORMAT (JSON ONLY):
    {{
        "filepath": "path/to/file.ext",
        "content": "CODE_HERE"
    }}
    """

    # إعدادات OpenRouter
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": f"https://github.com/{repo}", # مطلوب لـ OpenRouter
        "X-Title": "GitHub Auto-Fixer Agent"
    }
    
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "You are a senior coding agent. Output valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2, # منخفض للدقة
        "response_format": {"type": "json_object"} # Qwen يدعم الـ JSON Mode
    }

    print(f"🧠 Consulting {MODEL_ID} via OpenRouter...")
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.text}")
            return

        result = response.json()
        
        # استخراج الرد (قد يحتاج تنظيفاً من علامات Markdown)
        raw_content = result['choices'][0]['message']['content']
        # تنظيف الرد إذا كان يحتوي على ```json
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0]
        elif "```" in raw_content:
            raw_content = raw_content.split("```")[1].split("```")[0]

        ai_data = json.loads(raw_content)
        file_path = ai_data["filepath"]
        fixed_code = ai_data["content"]

        # === حواجز الأمان (Safety Guardrails) ===
        old_size = get_file_size(file_path)
        new_size = len(fixed_code)

        if old_size > 0 and new_size < (old_size * SAFETY_THRESHOLD):
            print(f"⚠️ SAFETY STOP: Qwen tried to delete too much code ({old_size} -> {new_size}). Fix rejected.")
            return

        # تطبيق الإصلاح
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(fixed_code)

        # الرفع
        remote = f"https://x-access-token:{token}@[github.com/](https://github.com/){repo}.git"
        run_git_cmd([
            f"git remote set-url origin {remote}",
            "git config --global user.name 'Qwen3-Agent'",
            "git config --global user.email 'qwen@openrouter.ai'",
            f"git add {file_path}",
            f"git commit -m 'fix: Qwen3 auto-repair for {os.path.basename(file_path)}'",
            "git push"
        ])
        print(f"✅ Qwen3 successfully repaired {file_path}!")

    except Exception as e:
        print(f"❌ Execution Failed: {str(e)}")
        # طباعة الرد الخام للمساعدة في التصحيح
        if 'raw_content' in locals():
            print(f"Raw AI Response: {raw_content[:500]}...")

if __name__ == "__main__":
    solve_with_qwen()
    
