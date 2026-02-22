import requests
import json
import time
import subprocess
import sys
import os

def run_command(command, cwd=None):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print(result.stdout)
    return result

def send_event(message, diff):
    print(f"Sending event: {message}")
    payload = {
        "type": "git_commit",
        "data": {
            "message": message,
            "diff": diff
        },
        "metadata": {
            "repo": "https://github.com/demo/tracecontext-demo",
            "user": "demo-user"
        }
    }
    try:
        response = requests.post("http://localhost:8000/events", json=payload)
        print(f"Orchestrator response: {response.text}")
    except Exception as e:
        print(f"Failed to send event: {e}")

def main():
    # 1. Initialize a demo repo
    if not os.path.exists("demo-v5"):
        os.makedirs("demo-v5")
    
    run_command("git init", cwd="demo-v5")
    
    # 2. Simulate User Action 1: Choosing FastAPI
    print("\n--- Developer Action 1: Choosing Architecture ---")
    commit_msg = "feat: start project with fastapi for high performance"
    diff = """diff --git a/main.py b/main.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/main.py
@@ -0,0 +1,5 @@
+from fastapi import FastAPI
+app = FastAPI()
+
+@app.get("/")
+def read_root(): return {"Hello": "World"}"""
    
    send_event(commit_msg, diff)
    
    print("Waiting for agents to process...")
    time.sleep(5) 
    
    # 3. Simulate User Action 2: Pivoting to Stripe
    print("\n--- Developer Action 2: Changing Payment Provider ---")
    commit_msg = "refactor: switch to stripe from braintree due to latency issues"
    diff = """diff --git a/payments.py b/payments.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/payments.py
@@ -0,0 +1,5 @@
+import stripe
+# ADR: Switched to Stripe because Braintree was too slow in APAC region
+stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_placeholder")
+"""
    
    send_event(commit_msg, diff)
    
    print("Waiting for agents to process...")
    time.sleep(5)
    
    # 4. Search for Context
    print("\n--- Developer Value: Searching Context ---")
    print("Query: 'Why did we choose Stripe?'")
    
    try:
        response = requests.get("http://localhost:8000/context", params={"query": "Stripe"})
        data = response.json()
        print("\nTraceContext Found:")
        for ctx in data.get("context", []):
            print(f"> {ctx}")
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    main()
