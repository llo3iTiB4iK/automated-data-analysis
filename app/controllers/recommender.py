from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif

from .dataframe_report import DataFrameReport
from .models import AnalysisParams
from app.errors import ParameterError#


class Recommender:

    def __init__(self, data: pd.DataFrame, report: DataFrameReport) -> None:
        self.data: pd.DataFrame = data
        self.report: DataFrameReport = report
        self.target_col: Any = None

    def __validate_target_col(self) -> pd.Series:
        if not self.target_col or self.target_col not in self.data.columns:  # todo: maybe refactor with parameter operations
            raise ParameterError("target_col", self.target_col, list(self.data.columns))

        target_series: pd.Series = self.data[self.target_col]
        missing_count: int = target_series.isna().sum()
        if missing_count > 0:
            na_percentage: float = round(missing_count / len(target_series) * 100, 2)
            self.report.add_text(
                f"* Column contains {missing_count} missing values ({na_percentage} % of all). You can consider one of :\n"
                f"    - common methods, such as dropping rows containing NaN values if their share is very small or filling them with median/mean/mode value.\n"
                f"    - special methods (Forward Fill, Backward Fill, filling NaN with exact value or based on other columns etc) if required.")
        else:
            self.report.add_text("* No missing values in target column were found - good sign!")
        return target_series

    def __feature_selection_recs(self, df_metrics: pd.Series, metric_levels: dict, metric_name: str, analysis_task: str) -> None:
        self.report.add_heading("Feature Selection Recommendations:")
        for metric_level, (low_value, high_value) in metric_levels.items():
            level_cols: pd.Series = df_metrics[(abs(df_metrics) >= low_value) & (abs(df_metrics) < high_value)]
            if level_cols.empty:
                self.report.add_text(f"* No {metric_level} meaningful features found based on {metric_name}.")
            else:
                self.report.add_text(f"* {len(level_cols)} {metric_level} meaningful features were found. Consider using them in {analysis_task}:")
                if 3 <= len(level_cols) <= 7:
                    sns.heatmap(pd.DataFrame(level_cols).T, annot=True, cmap="coolwarm", vmin=low_value, vmax=high_value, square=True, cbar=False)
                    self.report.add_plot()
                else:
                    self.report.add_series(level_cols)
                plot_funcs: list = []
                for feature in level_cols.index:
                    if analysis_task == "regression":
                        plot_funcs.append(lambda ax, f=feature: sns.regplot(self.data, x=self.target_col, y=f, line_kws={"color": "orange"}, ax=ax))
                    elif analysis_task == "classification":
                        plot_funcs.append(lambda ax, f=feature: sns.boxplot(self.data, x=f, y=self.target_col, hue=self.target_col, ax=ax))
                self.report.add_subplots(plot_funcs, suptitle=f"Dependency between target column and {metric_level} meaningful features")
        little_metric: pd.Series = df_metrics[abs(df_metrics) < metric_levels["low"][0]]
        if not little_metric.empty:
            self.report.add_text(f"* All the other columns are considered to have little or even no {metric_name} with target column.\n")

    def __feature_engineering_recs(self) -> None:
        self.report.add_heading("Feature Engineering Recommendations:")
        column_types: pd.Series = self.data.drop(columns=[self.target_col]).dtypes
        column_conditions = {
            "bool": (None, "    - Boolean features detected.\n"
                           "* Consider encoding them as 0/1 if needed:"),
            "int": (lambda int_cols: int_cols[(self.data[int_cols].nunique() <= 20) | (self.data[int_cols].nunique() < len(self.data) * 0.1)],
                    "    - These Integer features detected to have a few unique values.\n"
                    "* Consider treating them as categorical (binning):"),
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

    def _regression_recommendations(self) -> None:
        self.report.add_heading(f"Regression Analysis Recommendations for column '{self.target_col}':")
        target_series: pd.Series = self.__validate_target_col()

        if not pd.api.types.is_numeric_dtype(target_series) or pd.api.types.is_bool_dtype(target_series):
            self.report.add_text(f"* Target column '{self.target_col}' is not numeric.\n"
                                 f"* No further reporting can be performed. Consider encoding or converting it.")
            return
        else:
            self.report.add_text(f"* Target column '{self.target_col}' is numeric ({target_series.dtype}).")

        self.report.add_subplots([
            lambda ax: sns.boxplot(x=target_series, ax=ax),
            lambda ax: sns.histplot(target_series, kde=True, ax=ax).lines[0].set_color('crimson')
        ], suptitle=f"'{self.target_col}' values distribution")

        Q1, Q3 = target_series.quantile(0.25), target_series.quantile(0.75)
        IQR: float = Q3 - Q1
        outliers: int = ((target_series < Q1 - 1.5 * IQR) | (target_series > Q3 + 1.5 * IQR)).sum()
        if outliers > 0:
            self.report.add_text(f"* {outliers} potential outliers detected in '{self.target_col}'.\n"
                                 f"* Consider handling them or leave these values as-is if they are important.\n")
        else:
            self.report.add_text("* No potential outliers were detected in target column, which is perfect for building a "
                                 "stable predictive model and indicates good data quality!\n")
        self.report.add_text(f"* If the distribution of '{self.target_col}' is not normal (look at the chart above), consider "
                             f"applying transformations such as log or Box-Cox to make the data more suitable for reporting.\n"
                             f"A transformation can sometimes help stabilize variance and improve the model's performance.")

        correlations: pd.Series = self.data.corr(numeric_only=True)[self.target_col]
        corr_levels: dict = {
            "highly": (0.7, 1.0),
            "moderately": (0.5, 0.7),
            "low": (0.3, 0.5)
        }
        self.__feature_selection_recs(correlations, corr_levels, "correlation", "regression")

        self.__feature_engineering_recs()

        self.report.add_text("\n|====<   Regression reporting preparation completed !   >====|", monospaced=True, style="B")

    def _classification_recommendations(self) -> None:
        self.report.add_heading(f"Classification Recommendations for column '{self.target_col}':")
        target_series: pd.Series = self.__validate_target_col()

        plot: plt.Axes = sns.countplot(x=target_series, hue=target_series)
        if target_series.nunique() > 5:
            plot.set_xticklabels(plot.get_xticklabels(), rotation=90)
        self.report.add_plot("Distribution of classes across target column")
        class_counts: pd.Series = target_series.value_counts(normalize=True)
        min_class, max_class = class_counts.min(), class_counts.max()
        if max_class / min_class > 3:
            self.report.add_text(
                f"* Target column is imbalanced:\n"
                f"    - the most frequent class appears {round(max_class / min_class, 2)}x more often than the least frequent.\n"
                f"    - consider using techniques like oversampling (SMOTE), undersampling, or class weighting in your model.")
        else:
            self.report.add_text("* Target column has a balanced distribution of classes.")

        rare_categories: pd.Index = class_counts[class_counts / len(self.data) < 0.01]
        if not rare_categories.empty:
            self.report.add_text("* Some target classes are very rare (<1% of total data):")
            self.report.add_series(rare_categories)
            self.report.add_text("* Consider:\n"
            "    - grouping rare classes into an 'Other' category (if appropriate)\n"
            "    - collecting more data\n"
            "    - using stratified sampling during training.")

        numeric_cols: list = self.data.select_dtypes("number").columns
        mi_scores: pd.Series = pd.Series(mutual_info_classif(X=self.data[numeric_cols], y=target_series, random_state=42), index=numeric_cols, name=self.target_col)
        mi_levels: dict = {
            "highly": (0.1, 1.0),
            "moderately": (0.05, 0.1),
            "low": (0.01, 0.05)
        }
        self.__feature_selection_recs(mi_scores, mi_levels, "mutual information", "classification")

        self.__feature_engineering_recs()
        self.report.add_text("If exist, categorical columns should be encoded since most algorithms or their implementations require numerical data as input!", monospaced=True, style="B")

        self.report.add_text("\n|====<   Classification preparation completed !   >====|", monospaced=True, style="B")

    def _clusterization_recommendations(self) -> None:
        if not self.target_col:
            self.target_col = "Cluster"
        self.data[self.target_col] = None
        self.report.add_heading(f"Clustering Recommendations for '{self.target_col}':")

        if len(self.data) < 100:
            self.report.add_text(f"* The dataset is quite small ({len(self.data)} rows). Clustering may not be reliable.")
        else:
            self.report.add_text(f"* Considering your dataset size ({len(self.data)} rows), expected number of clusters should not be more "
                                 f"than {int(len(self.data) / 10)}.\n    - Otherwise, clustering algorithms would have low performance.")

        numeric_columns: pd.Index = self.data.select_dtypes('number').columns

        if len(numeric_columns) > 3:
            self.report.add_text(f"\n* The dataset consists of {len(numeric_columns)} numeric columns:\n    - To facilitate clustering "
                                 f"and improve visualization, dimensionality reduction techniques like PCA or t-SNE should be applied.")

        self.report.add_heading("Feature Selection Recommendations:")
        pca: PCA = PCA().fit(self.data[numeric_columns])
        importance = (abs(pca.components_) * pca.explained_variance_ratio_.reshape(-1, 1)).sum(axis=0)
        pca_importance: pd.Series = pd.Series(importance, index=numeric_columns, name="Features").sort_values(ascending=False)
        pca_importance = pca_importance[pca_importance > 0.01 * pca_importance.sum()]
        self.report.add_text(f"* {len(pca_importance)} important features found. Consider using them in clustering:")
        sns.barplot(x=pca_importance.values, y=pca_importance.index, hue=pca_importance.index)
        plt.ylabel("Features")
        self.report.add_plot("Important features weighted PCA score")

        self.report.add_text("\n* Looking at the chart below, make important decisions about preprocessing your data:\n"
                             "    1) whether scaling should be performed, as most clustering algorithms are distance-based;\n"
                             "        - actually, scaling can result in a completely different set of important features.\n"
                             "    2) whether outliers should be handled properly, as they can significantly impact the results;\n"
                             "        - this operation can also significantly impact the feature importance.")

        sns.boxplot(self.data[pca_importance.index], orient='h')
        self.report.add_plot("Important features' distribution")
        if len(pca_importance) < len(importance):
            self.report.add_text("* All the other numeric features have very low PCA score, which means they might not be useful for clustering.")

        self.__feature_engineering_recs()

        self.report.add_text("\n|====<   Clustering reporting preparation completed !   >====|", monospaced=True, style="B")

    def make_recommendations(self, params: AnalysisParams) -> None:
        self.target_col = target_col
        recommenders: dict = {
            'regression': self._regression_recommendations,
            'classification': self._classification_recommendations,
            'clusterization': self._clusterization_recommendations
        }

        return recommenders[params.analysis_task]()
