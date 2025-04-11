import openai

def analyze_performance(text):
    text = text[:10000] if len(text) > 10000 else text
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Linux system performance analyst."},
            {"role": "user", "content": f"""
Analyze the following Linux system report and return the 'Performance and Metrics' section in this format:

Performance and Metrics (Green, Amber, Red)

Overall Status: <Green / Amber / Red>

Findings (200 words): <Detailed performance analysis>

Table:
Host: <IP or name>
Summary: <Why it's scored that way (~100 words)>
Status: <Green / Amber / Red>

Use no Markdown, no pipes, no plus signs — just key:value per line.
Only return one host entry.

Report:
{text}
"""}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']
