from fpdf import FPDF
from io import BytesIO


def generate_report(analysis_results: dict) -> BytesIO:
    pdf: FPDF = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(100, 5, txt=analysis_results["info"])
    pdf.multi_cell(100, 5, txt=analysis_results["describe"])
    for image_path in analysis_results["plots"]:
        pdf.image(image_path, w=175)
    return BytesIO(pdf.output())
