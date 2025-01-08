import pandas as pd
from services.helpers.dataframe_analyzer import DataFrameAnalyzer
from services.helpers import visualization_helpers as vh, file_operations as fo


def analyze_data(data: pd.DataFrame) -> dict:
    analyzer: DataFrameAnalyzer = DataFrameAnalyzer(data)
    plot_funcs: list = []

    plot_funcs.extend(analyzer.get_overall_dataframe_plots())
    plot_funcs.extend(analyzer.get_single_column_plots())
    plot_funcs.extend(analyzer.get_two_column_plots())

    return {
        "info": analyzer.get_summary(),
        "describe": analyzer.get_description(),
        "plots": [fo.create_temp_file(vh.generate_plot_to_bytesio(func).getvalue(), ".png") for func in plot_funcs]
    }
