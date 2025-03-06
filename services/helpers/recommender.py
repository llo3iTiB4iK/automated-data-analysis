import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Any
from errors import ParameterError
from services.helpers.dataframe_report import DataFrameReport


class Recommender:

    def __init__(self, data: pd.DataFrame, report: DataFrameReport):
        self.data: pd.DataFrame = data
        self.report: DataFrameReport = report
        self.target_col: Any = None

    def __validate_target_col(self) -> None:
        if not self.target_col or self.target_col not in self.data.columns:
            raise ParameterError("target_col", self.target_col, list(self.data.columns))

    def _regression_recommendations(self) -> None:
        self.__validate_target_col()
        self.report.add_heading(f"Regression Analysis Recommendations for column '{self.target_col}':")
        target_series: pd.Series = self.data[self.target_col]

        if not pd.api.types.is_numeric_dtype(target_series) or pd.api.types.is_bool_dtype(target_series):
            self.report.add_text(f"* Target column '{self.target_col}' is not numeric. "
                                 f"* No further analysis can be performed. Consider encoding or converting it.")
            return
        else:
            self.report.add_text(f"* Target column '{self.target_col}' is numeric ({target_series.dtype}).")

        missing_count: int = target_series.isna().sum()
        if missing_count > 0:
            na_percentage: float = round(missing_count / len(target_series) * 100, 2)
            self.report.add_text(f"* Column contains {missing_count} missing values ({na_percentage} % of all). You can consider one of :\n"
                                 f"    - common methods, such as dropping rows containing NaN values if their share is very small or filling them with median/mean value.\n"
                                 f"    - special methods (Forward Fill, Backward Fill, filling NaN with exact value or based on other columns etc) if required.")
        else:
            self.report.add_text("* No missing values in target column were found - good sign!")

        correlations: pd.Series = self.data.corr(numeric_only=True)[self.target_col].drop(self.target_col)
        corr_levels: dict = {
            "highly": (0.7, 1.0),
            "moderately": (0.5, 0.7),
            "low": (0.3, 0.5)
        }
        for corr_level, (low_value, high_value) in corr_levels.items():
            corr_cols: pd.Series = correlations[(abs(correlations) >= low_value) & (abs(correlations) < high_value)]
            if corr_cols.empty:
                self.report.add_text(f"* No {corr_level} correlated features found.")
            else:
                self.report.add_text(f"* {len(corr_cols)} {corr_level} correlated features were found. Consider using them in regression:")
                if 3 <= len(corr_cols) <= 7:
                    sns.heatmap(pd.DataFrame(corr_cols).T, annot=True, cmap="coolwarm", vmin=low_value, vmax=high_value,
                                square=True, cbar=False)
                    self.report.add_plot()
                else:
                    self.report.add_series(corr_cols)
                cols: int = 3
                rows: int = int(len(corr_cols) / cols) + (1 if len(corr_cols) % cols else 0)
                fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 5 * rows))
                for i, feature in enumerate(corr_cols.index):
                    sns.regplot(self.data, x=self.target_col, y=feature, line_kws={"color": "orange"}, ax=axes.flatten()[i])
                for j in range(len(corr_cols), rows * cols):
                    axes.flatten()[j].set_visible(False)
                plt.tight_layout(pad=1.0)
                fig.suptitle(f"Correlation plot for {corr_level} correlated features", fontsize=16, fontweight='bold', y=1.05)
                self.report.add_plot()

        little_corr: pd.Series = correlations[abs(correlations) < 0.3]
        if not little_corr.empty:
            self.report.add_text("* All the other columns are considered to have little or even no correlation with target column.\n")

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        sns.boxplot(x=target_series, ax=axes[0])
        sns.histplot(target_series, kde=True, ax=axes[1]).lines[0].set_color('crimson')
        if target_series.max() / target_series.min() > 100:
            axes[1].set_yscale('log')
            axes[1].set_title("Y-axis in log scale due to wide value range")
        fig.suptitle(f"'{self.target_col}' values distribution", fontsize=16, fontweight='bold')
        self.report.add_plot()
        Q1, Q3 = target_series.quantile(0.25), target_series.quantile(0.75)
        IQR: float = Q3 - Q1
        outliers: int = ((target_series < Q1 - 1.5 * IQR) | (target_series > Q3 + 1.5 * IQR)).sum()
        if outliers > 0:
            self.report.add_text(f"* {outliers} potential outliers detected in '{self.target_col}'.\n"
                                 f"Consider handling them or leave these values as-is if they are important.\n")
        else:
            self.report.add_text("* No potential outliers were detected in target column, which is perfect for building a "
                                 "stable predictive model and indicates good data quality!\n")
        self.report.add_text(f"* If the distribution of '{self.target_col}' is not normal (look at the chart above), consider "
                             f"applying transformations such as log or Box-Cox to make the data more suitable for analysis.\n"
                             f"A transformation can sometimes help stabilize variance and improve the model's performance.")

        self.report.add_heading("Feature Engineering Recommendations:")
        column_types: pd.Series = self.data.drop(columns=[self.target_col]).dtypes
        column_conditions = {
            "bool": (None, "    - Boolean features detected.\n"
                           "* Consider encoding them as 0/1 if needed:"),
            "int": (lambda int_cols: int_cols[(self.data[int_cols].nunique() <= 20) | (self.data[int_cols].nunique() < len(self.data) * 0.1)],
                    "    - These Integer features detected to have a few unique values.\n"
                    "* Consider treating them as categorical:"),
            "float": (lambda float_cols: float_cols[abs(self.data[float_cols].skew()) > 1],
                      "    - These Float features have high skewness (|skewness| > 1).\n"
                      "* Consider transformations (log, sqrt, or Box-Cox):"),
            "datetime64[ns]": (None, "    - Datetime features detected.\n"
                                     "* Consider extracting useful components like year, month, day, or weekday etc:"),
            "category": (None, "    - Category type features detected.\n"
                               "* Consider encoding methods like One-Hot, Target Encoding, Frequency Encoding, etc."
                               "* If feature has an ordinal relationship, consider using Ordinal Encoding.\n"
                               "* If feature contains rare categories, consider grouping them into an 'Other' category to avoid sparsity.\n"
                               "* If column has missing values, consider filling them with 'Unknown' or mode value:"),
            "object": (None, "    - String type features detected.\n"
                             "* Consider converting them to categorical variables, applying text transformations or removing if not useful:")
        }
        for col_type, (condition, message) in column_conditions.items():
            relevant_columns: pd.Index = column_types[column_types == col_type].index
            if condition is not None:
                relevant_columns = condition(relevant_columns)
            if not relevant_columns.empty:
                self.report.add_text(message)
                self.report.add_series(relevant_columns)

        self.report.add_text("\n|====<   Regression analysis preparation completed !   >====|", monospaced=True)

    def _classification_recommendations(self) -> None:
        self.__validate_target_col()
        # TODO: make recommendations

    def _clusterization_recommendations(self) -> None:
        if not self.target_col:
            self.target_col = "Cluster"
        # TODO: make recommendations

    def make_recommendations(self, analysis_task: str, target_col: str) -> None:
        self.target_col = target_col
        recommenders: dict = {
            'regression': self._regression_recommendations,
            'classification': self._classification_recommendations,
            'clusterization': self._clusterization_recommendations
        }

        if analysis_task not in recommenders:
            raise ParameterError("analysis_task", analysis_task, list(recommenders.keys()))

        return recommenders[analysis_task]()
