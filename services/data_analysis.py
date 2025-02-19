import pandas as pd
from services.helpers.dataframe_analyzer import DataFrameAnalyzer
from services.helpers import visualization_helpers as vh
from fpdf import FPDF
from io import BytesIO

# todo: refactor module
def get_data_report(data: pd.DataFrame, params: dict) -> BytesIO:
    pdf: FPDF = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(100, 5, txt=analysis_results["info"])
    pdf.multi_cell(100, 5, txt=analysis_results["describe"])
    for image_path in analysis_results["plots"]:
        pdf.image(image_path, w=175)
    return BytesIO(pdf.output())


def analyze_data(data: pd.DataFrame) -> dict:
    analyzer: DataFrameAnalyzer = DataFrameAnalyzer(data)
    plot_funcs: list = []

    plot_funcs.extend(analyzer.get_overall_dataframe_plots())

    return {
        "info": analyzer.get_summary(),
        "describe": analyzer.get_description(),
        "plots": [vh.generate_plot_to_bytesio(func) for func in plot_funcs]
    }

