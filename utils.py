def read_text_from_file(txt_path):
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read()

def sanitize_text(text):
    return (
        text.replace("→", "->")
            .replace("’", "'").replace("‘", "'")
            .replace("“", '"').replace("”", '"')
            .replace("–", "-").replace("—", "-")
    )

