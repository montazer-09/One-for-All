import os
import requests
import subprocess
import sys

# إعدادات الألوان للطباعة (لسهولة القراءة في الـ Logs)
CYAN = '\033[96m'
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

def run_cmd(cmd):
    """تشغيل أوامر النظام وإرجاع النتيجة"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()

def get_kimi_fix(error_log):
    """إرسال الخطأ إلى Kimi AI والحصول على الحل"""
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print(f"{RED}Error: KIMI_API_KEY is missing!{RESET}")
        sys.exit(1)

    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # هندسة الأوامر (Prompt Engineering) لضمان الدقة
    prompt = f"""
    CRITICAL BUILD ERROR DETECTED:
    {error_log}

    You are a Senior DevOps & Software Architect.
    TASK:
    1. Analyze the error log.
    2. Identify the SPECIFIC file causing the error.
    3. Rewrite the COMPLETE file with the fix applied.
    
    OUTPUT FORMAT (Strictly follow this):
    <<<FILE_PATH>>>
    path/to/faulty/file.ext
    <<<CODE_START>>>
    [Put the complete fixed code here]
    <<<CODE_END>>>
    """

    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {"role": "system", "content": "You are an autonomous code-fixing agent."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2  # درجة منخفضة للدقة العالية
    }

    print(f"{CYAN}🤖 Asking Kimi for a solution...{RESET}")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"{RED}API Error: {response.text}{RESET}")
        return None

def apply_fix_and_push(ai_response):
    """تطبيق الحل وعمل Push للمستودع"""
    try:
        # استخراج مسار الملف والكود من رد الذكاء الاصطناعي
        file_path = ai_response.split("<<<FILE_PATH>>>")[1].split("<<<CODE_START>>>")[0].strip()
        code_content = ai_response.split("<<<CODE_START>>>")[1].split("<<<CODE_END>>>")[0].strip()

        print(f"{GREEN}✔ Fixing file: {file_path}{RESET}")

        # كتابة الكود الجديد
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(code_content)

        # إعداد Git باستخدام التوكن الخاص بك
        token = os.getenv("MY_ACCESS_TOKEN")
        repo = os.getenv("GITHUB_REPOSITORY")
        
        # أمر سحري للمصادقة باستخدام التوكن
        run_cmd(f"git remote set-url origin https://x-access-token:{token}@github.com/{repo}.git")
        run_cmd("git config --global user.name 'Kimi-Auto-Fixer'")
        run_cmd("git config --global user.email 'ai@bot.com'")
        
        # الرفع (Commit & Push)
        run_cmd(f"git add {file_path}")
        commit_msg = f"fix: AI auto-repair for {os.path.basename(file_path)}"
        run_cmd(f"git commit -m '{commit_msg}'")
        run_cmd("git push")
        
        print(f"{GREEN}🚀 Successfully pushed fix to repository!{RESET}")

    except Exception as e:
        print(f"{RED}❌ Failed to apply fix: {str(e)}\nResponse was:\n{ai_response}{RESET}")

if __name__ == "__main__":
    # قراءة ملف الخطأ الذي تم توليده من الخطوة السابقة
    if os.path.exists("build_error.log"):
        with open("build_error.log", "r") as f:
            log_content = f.read()
            # نرسل فقط آخر 2000 حرف لتوفير التوكيز والتركيز على الخطأ الأخير
            fix = get_kimi_fix(log_content[-4000:])
            if fix:
                apply_fix_and_push(fix)
    else:
        print("No error log found.")
      
