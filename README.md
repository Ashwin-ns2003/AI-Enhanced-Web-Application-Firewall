# AI-Enhanced Web Application Firewall (Simple Version)

A small web application firewall that checks incoming web requests and blocks malicious ones, using **simple rules** plus a **Random Forest machine learning model**. It has a web page where you can type any request and see whether it is allowed or blocked.

## Problem
Normal firewalls use fixed rules, and attackers can slip past them with small changes. This project adds a machine learning model that learns what attacks *look like*, so it can catch suspicious requests that no rule matches.

## How it works
```
Request  -->  Step 1: Rules (regex)  --match-->  BLOCKED
                   |
               no match
                   v
          Step 2: Random Forest model --score >= 0.5--> BLOCKED
                   |
               otherwise
                   v
                ALLOWED
```
1. **Rules:** four simple patterns catch common attacks: SQL injection, XSS, path traversal and command injection
2. **Features:** each request is turned into 5 numbers: length, number of special characters, special-character ratio, number of digits, and number of suspicious words (like `select`, `script`, `passwd`)
3. **Model:** a Random Forest looks at those numbers and gives an attack score from 0 to 1
4. **Logging:** every decision is saved to `firewall.log` and shown on the page

## Attacks detected
| Attack | Example |
|---|---|
| SQL Injection | `username=admin' OR '1'='1' --` |
| Cross-Site Scripting (XSS) | `<script>alert(1)</script>` |
| Path Traversal | `../../etc/passwd` |
| Command Injection | `cmd.exe /c whoami` |

## Tools
Python, Flask, Scikit-learn (Random Forest), Pandas, Joblib, Regex

## Project files
```
data/payloads.csv   labelled examples (normal = 0, attack = 1)
features.py         turns a request into numbers
train_model.py      trains the model and saves model.pkl
app.py              the Flask web app and firewall logic
```

## How to run
```bash
pip install -r requirements.txt
python train_model.py     # trains the model and creates model.pkl
python app.py             # starts the app
```
Open **http://127.0.0.1:5000**, type a request and click **Check request**.

You can also use the API:
```bash
curl -X POST http://127.0.0.1:5000/check -d "username=admin' OR '1'='1' --"
```

## Results
The model was trained on 89 labelled examples (46 normal, 43 attacks) and tested on 23 held-out examples:

| Class | Precision | Recall | F1 |
|---|---|---|---|
| Normal | 0.86 | 1.00 | 0.92 |
| Attack | 1.00 | 0.82 | 0.90 |

Overall accuracy: **91%** on the test set.

**Important:** the dataset is small and was written by hand, and the test set is only 23 examples, so these numbers are only a rough guide. They show the idea works, not how it would perform on real traffic.

## Limitations and future work
- Train on a real traffic dataset (for example CSIC 2010) instead of a small hand-written one
- Add more features, such as entropy of the request or counts of specific symbols
- Turn it into a reverse proxy that sits in front of a real website
- Add a login page, a dashboard and rate limiting
