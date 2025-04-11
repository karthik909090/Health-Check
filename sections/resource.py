import openai

def analyze_resource(text):
    text = text[:10000] if len(text) > 10000 else text
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Linux system resource utilization expert."},
            {"role": "user", "content": f"""
Analyze the following Linux system data and return the 'Resource Utilization' section in this format:

Resource Utilization (Green, Amber, Red)

Overall Status: <Green / Amber / Red>

Findings (200 words): <Detailed usage and issues for CPU, RAM, disk, swap, I/O, load avg>

Table:
Host: <hostname>
Summary: <Why it's scored that way (~100 words)>
Status: <Green / Amber / Red>

Return plain key:value text, no formatting.

Report:
{text}
"""}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']
