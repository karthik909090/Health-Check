from fpdf.enums import XPos, YPos
from utils import sanitize_text

def render_section_table(pdf, title, section_name, content):
    pdf.add_page()
    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    parts = content.split("Table:")
    main_text = parts[0].strip()
    table_text = parts[1].strip() if len(parts) > 1 else ""

    pdf.set_font("Helvetica", '', 12)
    pdf.multi_cell(0, 10, sanitize_text(main_text))
    pdf.ln(5)

    lines = [line.strip() for line in table_text.split("\n") if ":" in line]
    row_data = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in lines}

    host = row_data.get("Host", "")
    summary = row_data.get("Summary", "")
    status = row_data.get("Status", "")

    col_widths = [50, 110, 30]
    line_height = 8

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(col_widths[0], line_height, "Host", border=1, align="C")
    pdf.cell(col_widths[1], line_height, section_name, border=1, align="C")
    pdf.cell(col_widths[2], line_height, "Status", border=1, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", '', 11)
    summary_lines = pdf.multi_cell(col_widths[1], line_height, summary, border=0, split_only=True)
    row_height = max(len(summary_lines), 1) * line_height

    x_start = pdf.get_x()
    y_start = pdf.get_y()

    pdf.set_xy(x_start, y_start)
    pdf.multi_cell(col_widths[0], row_height, host, border=1, align="L")

    pdf.set_xy(x_start + col_widths[0], y_start)
    pdf.multi_cell(col_widths[1], line_height, summary, border=1, align="L")

    pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
    pdf.multi_cell(col_widths[2], row_height, status, border=1, align="C")

    pdf.set_y(y_start + row_height)
