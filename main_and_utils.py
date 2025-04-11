import os
import openai
from datetime import datetime, timezone
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from utils import sanitize_text
from sections.performance import analyze_performance
from sections.security import analyze_security
from sections.resource import analyze_resource
from sections.configuration import analyze_configuration
from pdf_utils import render_section_table

openai.api_key = "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"  # Replace with your actual key or load from env


# PDF CLASS WITH LOGO & PAGE SETTINGS

class PDFReport(FPDF):
    def __init__(self, logo_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logo_path = logo_path
        self.skip_logo = True
        self.first_write_on_page = True

    def header(self):
        if not self.skip_logo:
            try:
                self.image(self.logo_path, x=self.w - 50, y=8, w=30)
            except:
                pass
        self.first_write_on_page = True

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def cell(self, *args, **kwargs):
        if self.first_write_on_page:
            self.ln(10)
            self.first_write_on_page = False
        return super().cell(*args, **kwargs)

    def multi_cell(self, *args, **kwargs):
        if self.first_write_on_page:
            self.ln(10)
            self.first_write_on_page = False
        return super().multi_cell(*args, **kwargs)


# FUNCTION TO EXTRACT JUST STATUS FROM GPT OUTPUT
def extract_status(content):
    for line in content.splitlines():
        if "Overall Status" in line or "Overall status" in line:
            return line.split(":")[-1].strip()
    return "N/A"


# OVERALL STATUS TABLE SECTION
def render_overall_summary_table(pdf, status_dict, host):
    pdf.add_page()

    # Headings
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "Healthcheck Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", '', 11)
    pdf.cell(0, 10, "Statement and Stats Across the Whole OS Environment Overall Status", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(3)
    pdf.cell(0, 10, "(Green, Amber, Red)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    # Table headers and values
    headers = ["Hosts", "Performance", "Security", "Resource", "Logs/Errors", "Config", "SOE standard", "Overall status"]
    values = [
        host,
        status_dict.get("Performance", "N/A"),
        status_dict.get("Security", "N/A"),
        status_dict.get("Resource", "N/A"),
        "N/A",
        status_dict.get("Configuration", "N/A"),
        "N/A",
        "",  # Optional calculated overall (Error logs and soe )
    ]

    col_widths = [25] * len(headers)
    row_height = 10

    # Calculate starting X for centering the table
    total_width = sum(col_widths)
    start_x = (pdf.w - total_width) / 2

    # Header row
    pdf.set_xy(start_x, pdf.get_y())
    pdf.set_font("Helvetica", 'B', 10)
    for i, h in enumerate(headers):
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(col_widths[i], row_height, h, border=1, align="C", fill=True)
    pdf.ln(row_height)

    # COLOURS OF THE VALUES
    pdf.set_xy(start_x, pdf.get_y())
    pdf.set_font("Helvetica", '', 10)
    for val in values:
        val_clean = val.lower()
        if val_clean == "green":
            pdf.set_fill_color(200, 255, 200)
        elif val_clean == "amber":
            pdf.set_fill_color(255, 230, 140)
        elif val_clean == "red":
            pdf.set_fill_color(255, 150, 150)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_widths[values.index(val)], row_height, val, border=1, align="C", fill=True)
    pdf.ln(10)


    # EXPLAINATION OF RED AMBER YELLOW GREEN
    pdf.set_font("Helvetica", '', 9)
    pdf.cell(0, 7, "Green = OK, No issues found", ln=True)
    pdf.cell(0, 7, "Yellow = Advisory, attention is required over the coming years", ln=True)
    pdf.cell(0, 7, "Amber = Warning, potential issues that need to be resolved over the next 12 months", ln=True)
    pdf.cell(0, 7, "Red = Critical, urgent attention is required", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", 'B', 9)
    pdf.cell(0, 7, "[ explanation of our benchmark against which these scores are recorded ]", ln=True)


# MAIN PDF GENERATION FUNCTION
def create_pdf_report(base_path, logo_path, logo_path1, output_path):
    performance_txt = os.path.join(base_path, "performance_health_report_10.100.152.164.txt")
    security_txt = os.path.join(base_path, "security_health_report_10.100.152.159.txt")
    resource_txt = os.path.join(base_path, "resource_health_check_10.100.152.164.txt")
    config_txt = os.path.join(base_path, "configuration_report_10.100.152.164.txt")

    def read_file(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    print("🔍 Analyzing each section with GPT...")
    performance = analyze_performance(read_file(performance_txt))
    security = analyze_security(read_file(security_txt))
    resource = analyze_resource(read_file(resource_txt))
    config = analyze_configuration(read_file(config_txt))

    # Extract statuses for overall table
    status_dict = {
        "Performance": extract_status(performance),
        "Security": extract_status(security),
        "Resource": extract_status(resource),
        "Configuration": extract_status(config),
    }

    pdf = PDFReport(logo_path=logo_path)
    pdf.set_auto_page_break(auto=True, margin=15)

    # COVER PAGE
    pdf.add_page()
    pdf.set_font("Helvetica", '', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.set_xy(10, 10)
    pdf.cell(0, 10, "Document Ref: HC/TDS/C0001", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    try:
        pdf.image(logo_path1, x=10, y=20, w=45)
        pdf.image(logo_path, x=pdf.w - 60, y=20, w=45)
    except:
        print("⚠️ Logos not found")

    pdf.ln(50)
    pdf.set_font("Helvetica", 'B', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 20, "LINUX HEALTH CHECK", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(20)
    pdf.set_font("Helvetica", '', 12)
    pdf.cell(0, 10, "Prepared for:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    pdf.cell(0, 10, "By: Jay Patel", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, f"Time Completed: {datetime.now(timezone.utc).strftime('%H:%M GMT')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    pdf.cell(0, 10, "Company: CXReview Limited", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, "1 Acacia Avenue, Luton. LU5 8PR", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 10, "Email: info@icomsol.com | Phone: (123) 456-7890", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.skip_logo = False

    # TABLE OF CONTENTS
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(200, 10, "Table of Contents", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    toc_data = [
        ["Section", "Page"],
        ["Overall Summary", "3"],
        ["Performance and Metrics", "4"],
        ["Security and Compliance", "5"],
        ["Resource Utilization", "6"],
        ["Configuration Checks", "7"]
    ]
    pdf.set_font("Helvetica", '', 12)
    for row in toc_data:
        pdf.cell(95, 10, row[0], border=1, align='L')
        pdf.cell(95, 10, row[1], border=1, align='C')
        pdf.ln(10)

    # OVERALL SUMMARY TABLE
    render_overall_summary_table(pdf, status_dict, host="10.100.152.164") #NEED TO CHANGE THE HOST ACCORDINGLY FOR NOW JUST USING THIS 

    # SECTIONAL PAGES
    render_section_table(pdf, "Performance and Metrics", "Performance and Metrics", performance)
    render_section_table(pdf, "Security and Compliance", "Security and Compliance", security)
    render_section_table(pdf, "Resource Utilization", "Resource Utilization", resource)
    render_section_table(pdf, "Configuration Checks", "Configuration Checks", config)

    pdf.output(output_path)
    print(f"✅ Report generated: {output_path}")


# RUN THE MAIN FUNCTION
if __name__ == '__main__':
    create_pdf_report(
        base_path="C:/Users/karth/Downloads/Healthcheck Reports/",
        logo_path="D:/Icom solutions/my report generator/company_logo.png",
        logo_path1="D:/Icom solutions/my report generator/client_logo.png",
        output_path="D:/Icom solutions/my report generator/summary_report_full.pdf"
    )
