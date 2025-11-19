import os, httpx, json

async def analyze_reports(paths, branch, commit):
    summary = []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                text = f.read()
            summary.append(text[:2000])  # limit length
        except:
            continue

    prompt = f"""
You are a senior performance engineer.
Analyze these reports and give short, actionable suggestions.

Branch: {branch}
Commit: {commit}

Reports:
{json.dumps(summary)}
"""

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        return (
            "OpenAI API key not configured. Here are raw excerpts from the reports:\n\n" +
            "\n\n".join(summary)
        )
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    org = os.getenv("OPENAI_ORG_ID")
    project = os.getenv("OPENAI_PROJECT")
    if org:
        headers["OpenAI-Organization"] = org
    if project:
        headers["OpenAI-Project"] = project
    model = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You analyze performance test reports."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
    except Exception:
        return (
            "AI service unavailable. Here are raw excerpts from the reports:\n\n" +
            "\n\n".join(summary)
        )
