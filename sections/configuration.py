import openai

def analyze_configuration(text):
    text = text[:10000] if len(text) > 10000 else text
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Linux configuration compliance expert."},
            {"role": "user", "content": f"""
Analyze the following Linux system configuration report and return the 'Configuration Checks' section in this format:

Configuration Checks (Green, Amber, Red)

Overall Status: <Green / Amber / Red>

Findings (200 words): <Evaluate sysctl, SSH settings, PAM, kernel params, cron jobs, auditd, and hardening policies>

Table:
Host: <hostname>
Summary: <Why it's scored that way (~100 words)>
Status: <Green / Amber / Red>

Return plain key:value format. No Markdown or table syntax.

Report:
{text}
"""}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']
