import requests
from pathlib import Path
import os

dest = None
env_path = Path('.env')
if env_path.exists():
    with env_path.open(encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                if k.strip() == 'DEST_EMAIL':
                    dest = v.strip()
                    break

files = {
    "files": open("test_reports/backend_k6.json", "rb"),
    "files2": open("test_reports/lighthouse_report.html", "rb"),
}

data = {
    "branch": "main",
    "commit": "CI Build",
}
if dest:
    data["recipients"] = dest

response = requests.post("http://127.0.0.1:8000/analyze", files=files, data=data)
print(response.text)
