import pandas as pd
from services.helpers.dataframe_analyzer import DataFrameAnalyzer
from services.helpers import visualization_helpers as vh


def analyze_data(data: pd.DataFrame) -> dict:
    analyzer: DataFrameAnalyzer = DataFrameAnalyzer(data)
    plot_funcs: list = []

    plot_funcs.extend(analyzer.get_overall_dataframe_plots())

    #асоціація, регресія, класифікація, кластеризація

    return {
        "info": analyzer.get_summary(),
        "describe": analyzer.get_description(),
        "plots": [vh.generate_plot_to_bytesio(func) for func in plot_funcs]
    }
