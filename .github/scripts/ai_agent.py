import os
import requests
import subprocess
import sys

# === إعدادات الأمان ===
SAFETY_THRESHOLD = 0.8  # (80%) لن يقبل التعديل إذا نقص حجم الملف عن هذه النسبة

def get_file_size(path):
    """إرجاع حجم الملف الحالي بالبايت"""
    return os.path.getsize(path) if os.path.exists(path) else 0

def run_git_cmd(cmds):
    for cmd in cmds:
        subprocess.run(cmd, shell=True, check=False)

def solve_safely():
    api_key = os.getenv("KIMI_API_KEY")
    token = os.getenv("MY_ACCESS_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    
    # 1. قراءة سجل الخطأ
    if not os.path.exists("universal_error.log"):
        print("No error log found.")
        return

    with open("universal_error.log", "r") as f:
        # نقرأ آخر 4000 حرف فقط للتركيز على سبب الفشل الأخير
        error_context = f.read()[-4000:]

    # 2. هندسة الأوامر "الآمنة" (Safety Prompt)
    prompt = f"""
    You are a Conservative Senior Developer. A build failed with this log:
    {error_context}

    CRITICAL RULES (Follow strictly):
    1. Identify the file causing the error and fix it.
    2. DO NOT delete existing functions, classes, or logic. Only fix the specific error.
    3. If the error is complex or requires deleting code, DO NOT fix it.
    4. Provide the FULL content of the fixed file.
    
    RESPONSE FORMAT:
    FILE: [path/to/file]
    CONTENT:
    [full code here]
    """

    headers = {
        "Authorization": f"Bearer {api_key}", 
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "system", "content": "You are a code repair bot. You prioritize safety and stability."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0  # صفر يعني دقة مطلقة وعدم تأليف
    }

    print("🛡️ Agent is analyzing safely...")
    try:
        response = requests.post("https://api.moonshot.cn/v1/chat/completions", json=payload, headers=headers)
        if response.status_code != 200:
            print(f"❌ API Error: {response.text}")
            return

        res_text = response.json()['choices'][0]['message']['content']
        
        # استخراج البيانات
        file_path = res_text.split("FILE:")[1].split("CONTENT:")[0].strip()
        fixed_code = res_text.split("CONTENT:")[1].strip()

        # === 3. تفعيل حواجز الأمان (Safety Guardrails) ===
        old_size = get_file_size(file_path)
        new_size = len(fixed_code)

        # إذا كان الملف موجوداً وحاول الذكاء الاصطناعي تقليصه بشكل مريب
        if old_size > 0 and new_size < (old_size * SAFETY_THRESHOLD):
            print(f"⚠️ SAFETY ALERT: The agent tried to delete huge parts of '{file_path}'.")
            print(f"Old Size: {old_size}, New Size: {new_size}. Operation Aborted.")
            return

        # 4. تطبيق الإصلاح والحفظ
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(fixed_code)

        # 5. الرفع للمستودع (Push)
        remote = f"https://x-access-token:{token}@github.com/{repo}.git"
        run_git_cmd([
            f"git remote set-url origin {remote}",
            "git config --global user.name 'AI-Safe-Agent'",
            "git config --global user.email 'agent@safe-mode.ai'",
            f"git add {file_path}",
            f"git commit -m 'fix: AI repaired {os.path.basename(file_path)} (Safe Mode)'",
            "git push"
        ])
        print(f"✅ Successfully repaired {file_path}")

    except Exception as e:
        print(f"❌ Failed to parse or apply fix: {e}")

if __name__ == "__main__":
    solve_safely()
    
