"""Simple AI Firewall: rules first, then a Random Forest model."""
import re
import urllib.parse
from datetime import datetime

import joblib
from flask import Flask, jsonify, render_template_string, request
from features import extract_features

app = Flask(__name__)
model = joblib.load("model.pkl")      # run train_model.py first
LOG_FILE = "firewall.log"

# Step 1: simple rules (signatures)
RULES = {
    "SQL Injection": r"(\bor\b\s+['\"]?1['\"]?\s*=\s*['\"]?1)|union\s+(all\s+)?select|drop\s+table",
    "XSS": r"<script|javascript:|\bon\w+\s*=",
    "Path Traversal": r"\.\./|/etc/passwd",
    "Command Injection": r"cmd\.exe|/bin/(ba)?sh|;\s*rm\s+-rf",
}


def check_request(text):
    decoded = urllib.parse.unquote_plus(text)

    # Step 1: check the rules
    for attack_name, pattern in RULES.items():
        if re.search(pattern, decoded, re.IGNORECASE):
            return {"decision": "BLOCKED", "reason": f"Rule matched: {attack_name}", "score": 1.0}

    # Step 2: ask the ML model
    score = float(model.predict_proba([extract_features(decoded)])[0][1])
    if score >= 0.5:
        return {"decision": "BLOCKED", "reason": "ML model found it suspicious", "score": round(score, 2)}
    return {"decision": "ALLOWED", "reason": "Looks normal", "score": round(score, 2)}


def write_log(text, result):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {result['decision']} | {result['reason']} | {text[:100]}\n")


def read_log(n=10):
    try:
        with open(LOG_FILE, encoding="utf-8") as f:
            return f.read().splitlines()[-n:][::-1]
    except FileNotFoundError:
        return []


PAGE = """
<!doctype html><html><head><title>AI Firewall</title>
<style>
 body{font-family:Arial;max-width:700px;margin:40px auto;padding:0 15px}
 textarea{width:100%;height:80px;padding:8px}
 button{padding:8px 16px;margin-top:8px;cursor:pointer}
 .BLOCKED{color:#c0392b} .ALLOWED{color:#27ae60}
 .box{background:#f4f4f4;padding:12px;border-radius:6px;margin-top:14px}
 small{color:#555}
</style></head><body>
<h2>AI-Enhanced Web Application Firewall</h2>
<p>Type a request or payload and the firewall will check it.</p>
<form method="post">
  <textarea name="payload" placeholder="Example: username=admin' OR '1'='1' --">{{ payload }}</textarea><br>
  <button type="submit">Check request</button>
</form>
{% if result %}
<div class="box"><b class="{{ result.decision }}">{{ result.decision }}</b><br>
 Reason: {{ result.reason }}<br>Attack score: {{ result.score }}</div>
{% endif %}
<h3>Recent requests</h3>
<div class="box"><small>{% for line in logs %}{{ line }}<br>{% else %}No requests yet.{% endfor %}</small></div>
</body></html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    result, payload = None, ""
    if request.method == "POST":
        payload = request.form.get("payload", "")
        result = check_request(payload)
        write_log(payload, result)
    return render_template_string(PAGE, result=result, payload=payload, logs=read_log())


@app.route("/check", methods=["POST"])     # API version: curl -X POST -d "text" /check
def check_api():
    text = request.get_data(as_text=True)
    result = check_request(text)
    write_log(text, result)
    return jsonify(result), (403 if result["decision"] == "BLOCKED" else 200)


if __name__ == "__main__":
    app.run(port=5000)
