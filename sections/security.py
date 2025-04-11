import openai

def analyze_security(text):
    text = text[:10000] if len(text) > 10000 else text
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Linux system security and compliance analyst."},
            {"role": "user", "content": f"""
Analyze the following Linux health check data and return the 'Security and Compliance' section in this format:

Security and Compliance (Green, Amber, Red)

Overall Status: <Green / Amber / Red>

Findings (200 words): <Detailed analysis of security compliance, patching, user accounts, firewalls, SSH, and other risks>

Table:
Host: <host IP or name>
Summary: <Why it is scored this way (~100 words)>
Status: <Green / Amber / Red>

Use key:value format. Only return one host entry. No markdown or decorations.

Report:
{text}
"""}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']
