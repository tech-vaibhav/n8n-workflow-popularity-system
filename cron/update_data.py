import requests

BASE_URL = "https://n8n-workflow-popularity-system.onrender.com"

def trigger(endpoint):
    url = f"{BASE_URL}{endpoint}"
    print(f"→ Calling {url}")
    try:
        res = requests.post(url, timeout=60)
        print("Status:", res.status_code)
        print("Response:", res.text)
    except Exception as e:
        print("ERROR:", e)

def main():
    print("===== Running Daily Data Refresh =====")
    trigger("/youtube/save")
    trigger("/forum/save")
    trigger("/google/save")
    print("===== DONE =====")

if __name__ == "__main__":
    main()
