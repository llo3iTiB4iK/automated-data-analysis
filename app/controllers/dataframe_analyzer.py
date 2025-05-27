import sys
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Callable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif

from app.errors import ColumnNotFound
from app.models import MetadataResponse
from app.models.request.analysis_params import AnalysisParams, AnalysisTask, DocumentTheme
from .dataframe_report import DataFrameReport

sns.set_style("darkgrid")


class DataFrameAnalyzer:

    @dataclass(frozen=True)
    class FeatureSelectionParams:
        metrics: pd.Series
        levels: dict[str, tuple[float, float]]
        name: str
        task: str
        plot_func: Callable[..., plt.Axes]
        plot_feature_wise: bool = True

    def __init__(self, data: pd.DataFrame) -> None:
        self._data = data
        self._report = None
        self._include_visualizations = True

    def __validate_target(self, col: str) -> pd.Series:
        if col not in self._data:
            raise ColumnNotFound([col], list(self._data.columns))
        series = self._data[col]
        missing = series.isna().sum()
        if missing:
            pct = round(missing / len(series) * 100, 2)
            self._report.add_text(
                f"* Target column '{col}' has {missing} missing values ({pct}% of all):\n"
                f"    - if missing values share is not too significant - "
                f"consider removal or using median/mode/mean value for imputation.\n"
                f"    - else - consider special methods of imputation "
                f"(Forward Fill, Backward Fill, using exact value or based on other columns)."
            )
        else:
            self._report.add_text(f"* Target column '{col}' has no missing values.")
        return series

    def __select_features(self, params: FeatureSelectionParams, target: str) -> None:
        self._report.add_heading("Feature Selection Recommendations:")
        significant_features = 0
        for label, (low, high) in params.levels.items():
            group = params.metrics[(params.metrics.abs() >= low) & (params.metrics.abs() < high)]
            if group.empty:
                self._report.add_text(f"* No {label} meaningful features found based on {params.name}.")
                continue
            significant_features += len(group)
            self._report.add_text(f"* {len(group)} {label} meaningful features were found. Consider using them in {params.task}:")
            # Visual summary
            if 3 <= len(group) <= 7 and self._include_visualizations:
                sns.heatmap(pd.DataFrame(group).T, annot=True, square=True, cbar=False, vmin=low, vmax=high, cmap='coolwarm', linewidth=.5)
                self._report.add_plot(title=params.name.title())
            else:
                self._report.add_series(group)
            # Pairwise plots
            if self._include_visualizations:
                if params.plot_feature_wise:
                    plotters = [lambda ax, f=feat: params.plot_func(ax, f) for feat in group.index]
                    self._report.add_subplots(plotters, suptitle=f"Dependency between '{target}' and {label} meaningful features")
                else:
                    params.plot_func(group.index)
                    self._report.add_plot(title=f"{label.title()} meaningful features chart")
        # Note on rest
        rest = params.metrics[params.metrics.abs() < min(l[0] for l in params.levels.values())]
        if significant_features == 0:
            self._report.add_text(
                f"* None of the features show significant relationship with target '{target}'.\n"
                f"- You might want to collect more informative features, engineer new ones, or reassess data quality."
            )
        elif not rest.empty:
            self._report.add_text("* Remaining features have low relevance.")

    def __regression_recs(self, target: str) -> FeatureSelectionParams | None:
        y = self.__validate_target(target)
        if pd.api.types.is_numeric_dtype(y) and not pd.api.types.is_bool_dtype(y):
            self._report.add_text(f"* Target column '{target}' is numeric ({y.dtype}).")
        else:
            self._report.add_text(f"* Target column '{target}' is not numeric.\n"
                                  f"* No further reporting can be performed. Consider encoding or converting it.")
            return

        if self._include_visualizations:
            self._report.add_subplots([
                lambda ax: sns.boxplot(x=y, ax=ax),
                lambda ax: sns.histplot(y, kde=True, ax=ax).lines[0].set_color('crimson')
            ], suptitle=f"'{target}' values distribution")
        # Outliers
        q1, q3 = y.quantile([0.25, 0.75])
        iqr = q3 - q1
        out = ((y < q1 - 1.5 * iqr) | (y > q3 + 1.5 * iqr)).sum()
        if out:
            self._report.add_text(f"* {out} potential outliers detected in '{target}'.\n"
                                 f"* Consider handling them or leave these values as-is if they are important.\n")
        else:
            self._report.add_text("* No potential outliers were detected in target column, which is perfect for building a "
                                 "stable predictive model and indicates good data quality!\n")
        self._report.add_text(f"* If the distribution of '{target}' is not normal (look at the chart above), consider "
                             f"applying transformations such as log or Box-Cox to make the data more suitable for reporting.\n"
                             f"A transformation can sometimes help stabilize variance and improve the model's performance.")
        # Correlation

        def plot_corr(ax: plt.Axes, feature: str) -> plt.Axes:
            sns.regplot(x=y, y=self._data[feature], line_kws={"color": "orange"}, ax=ax)

        return self.FeatureSelectionParams(
            metrics=self._data.corr(numeric_only=True)[target],
            levels={'highly': (0.7, 1.0), 'moderately': (0.5, 0.7), 'low': (0.3, 0.5)},
            name='correlation',
            task='regression',
            plot_func=plot_corr
        )

    def __classification_recs(self, target: str) -> FeatureSelectionParams | None:
        y = self.__validate_target(target)
        if pd.api.types.is_bool_dtype(y) or y.dtype == 'category' or (y.dtype == 'object' and y.nunique(True) <= 10):
            self._report.add_text(f"* Target column '{target}' seems to be discrete ({y.dtype}).")
            y = y.astype('category')
        else:
            self._report.add_text(f"* Target column '{target}' seems to be continuous or containing raw text data.\n"
                                  f"- No classification analysis can be performed.\n* Number of unique values: {y.nunique(True)}.")
            return

        if self._include_visualizations:
            sns.countplot(x=y, hue=y, legend=False)
            self._report.add_plot(f"'{target}' class distribution")
        # Class balance
        counts = y.value_counts(normalize=True)
        min_class, max_class = counts.min(), counts.max()
        if max_class / min_class > 3:
            self._report.add_text(
                f"* Target column is imbalanced:\n"
                f"    - the most frequent class appears {round(max_class / min_class, 2)}x more often than the least frequent.\n"
                f"    - consider using techniques like oversampling (SMOTE), undersampling, or class weighting in your model.")
        else:
            self._report.add_text("* Target column has a balanced distribution of classes.")
        # Rare categories
        rare_categories = counts[counts < 0.01]
        if not rare_categories.empty:
            self._report.add_text("* Some target classes are very rare (<1% of total data):")
            self._report.add_series(rare_categories)
            self._report.add_text("* Consider:\n"
                                 "    - grouping rare classes into an 'Other' category (if appropriate)\n"
                                 "    - collecting more data\n"
                                 "    - using stratified sampling during training.")
        # Mutual info

        def plot_mi(ax: plt.Axes, feature: str) -> plt.Axes:
            sns.boxplot(x=self._data[feature], y=y, hue=y, ax=ax, legend=False)

        nums = self._data.select_dtypes('number')
        if nums.shape[1] == 0:
            return

        valid_idx = pd.concat([nums, y], axis=1).dropna().index

        return self.FeatureSelectionParams(
            metrics=pd.Series(mutual_info_classif(nums.loc[valid_idx], y.loc[valid_idx], random_state=42), index=nums.columns, name=target),
            levels={'highly': (0.1, 1.0), 'moderately': (0.05, 0.1), 'low': (0.01, 0.05)},
            name='mutual information',
            task='classification',
            plot_func=plot_mi
        )

    def __clustering_recs(self, target: str) -> FeatureSelectionParams | None:
        self._data.loc[:, target] = None
        n = len(self._data)
        if n < 100:
            self._report.add_text(f"* Small data ({n} rows): clustering may be unreliable.")
        else:
            self._report.add_text(
                f"* Considering your dataset size ({len(self._data)} rows), expected number of clusters should not be"
                f" more than {n // 10}.\n    - Otherwise, clustering algorithms would have low performance.")
        nums = self._data.select_dtypes('number').dropna()
        if nums.shape[1] > 3:
            self._report.add_text(
                f"\n* The dataset consists of {nums.shape[1]} numeric columns:\n    - To facilitate clustering "
                f"and improve visualization, dimensionality reduction techniques like PCA or t-SNE should be applied."
            )
        if nums.shape[1] == 0:
            return
        # Weighted PCA score
        pca = PCA(random_state=42)
        pca.fit_transform(nums)
        weighted_pca = abs(pca.components_).T.dot(pca.explained_variance_ratio_)
        imp = pd.Series(weighted_pca, index=nums.columns, name=target).sort_values(ascending=False)
        self._report.add_text(
            "\n* In the next section, looking at the feature distribution chart, consider preprocessing decisions:\n"
            "    1) whether scaling should be applied, as most clustering algorithms are distance-based;\n"
            "        - actually, scaling can result in a completely different set of important features.\n"
            "    2) whether outliers should be handled properly, as they can significantly impact the results;\n"
            "        - this operation can also significantly impact the feature importance.")
        return self.FeatureSelectionParams(
            metrics=imp,
            levels={'highly': (0.01 * imp.sum(), imp.sum() + sys.float_info.epsilon)},
            name='weighted PCA score',
            task='clustering',
            plot_func=lambda features: sns.boxplot(self._data[features], orient='h'),
            plot_feature_wise=False
        )

    def __feature_engineering(self, target: str) -> None:
        self._report.add_heading("Feature Engineering Recommendations:")
        dtypes = self._data.drop(columns=[target]).dtypes
        recs_given = False

        strategies = {
            'bool': "Encode boolean features as 0/1 if needed:",
            'int': "Bin or treat small-cardinality integer features (having few unique values) as categorical:",
            'float': "Transform highly skewed (|skewness| > 1) float features (log, sqrt, Box-Cox):",
            'datetime64[ns]': "Extract useful date parts (year, month, day, weekday etc) from datetime features:",
            'category': "Encode category features using One-Hot, Target, Frequency or Ordinal Encoding methods."
                        "Group rare categories to avoid sparsity:",
            'object': "Convert string features to categorical ones, apply text transformations or drop:"
        }
        for dt, msg in strategies.items():
            cols = dtypes[dtypes == dt].index.tolist()
            if not cols:
                continue
            if dt == 'int':
                cols = [c for c in cols if (self._data[c].nunique() <= 20)]
            if dt == 'float':
                cols = [c for c in cols if abs(self._data[c].skew()) > 1]
            if cols:
                recs_given = True
                self._report.add_text(f"* {msg}")
                self._report.add_series(cols)

        if not recs_given:
            self._report.add_text("* All the features seem to be prepared for further analysis.")

    def _basic_stats(self) -> None:
        df = self._data
        self._report.add_heading("Overall dataset summary:")

        # Basic counts
        missing_cells = df.isna().sum().sum()
        counts = {
            'rows': len(df),
            'columns': len(df.columns),
            'numeric': df.select_dtypes('number').shape[1],
            'categorical': df.select_dtypes('category').shape[1],
            'boolean': df.select_dtypes('bool').shape[1],
            'datetime': df.select_dtypes('datetime').shape[1],
            'string': df.select_dtypes('object').shape[1],
            'duplicates': int(df.duplicated().any()),
            'missing_pct': round(missing_cells / df.size * 100, 2),
        }
        summary = f"* Dataset contains {counts['rows']} rows, {counts['columns']} columns\n" \
                  f"({counts['numeric']} numeric, {counts['categorical']} categorical, {counts['boolean']} boolean, " \
                  f"{counts['datetime']} datetime, {counts['string']} string).\n" \
                  f"* Duplicated rows {'found' if counts['duplicates'] else 'not found'}.\n" \
                  f"* Missing values: {counts['missing_pct']}% ."
        self._report.add_text(summary)

        # Data types series
        self._report.add_series(self._data.dtypes, title="Column Types:")

        # Missing value plot
        if missing_cells > 0 and self._include_visualizations:
            missing_df = pd.DataFrame({
                'Missing': df.isna().sum(),
                'Non-missing': df.notna().sum()
            })
            missing_df.plot(kind='barh', stacked=True, title="Missing values by column", xlabel="Count")
            self._report.add_plot()

        # Descriptive statistics
        num_desc = df.describe()

        for col in df.select_dtypes(include='datetime').columns:
            num_desc[col] = num_desc[col].astype('datetime64[s]')

        self._report.add_dataframe(num_desc, title="Numeric Stats:")
        category_columns = df.select_dtypes(include=['object', 'category', 'bool'])
        if not category_columns.empty:
            self._report.add_dataframe(category_columns.describe(), title="Non-numeric Stats:")

    def _task_based_recs(self, analysis_task: AnalysisTask, target_column: str) -> None:
        TASK_RECOMMENDERS: dict[str, Callable[..., None]] = {
            AnalysisTask.REGRESSION: self.__regression_recs,
            AnalysisTask.CLASSIFICATION: self.__classification_recs,
            AnalysisTask.CLUSTERIZATION: self.__clustering_recs
        }
        self._report.add_heading(f"{analysis_task.title()} Recommendations for '{target_column}'")
        selection_params = TASK_RECOMMENDERS[analysis_task](target_column)
        if selection_params:
            self.__select_features(selection_params, target_column)
            self.__feature_engineering(target_column)
        self._report.add_text(f"\n|====<   {analysis_task.title()} preparation completed !   >====|", monospaced=True, style="B")

    def generate_report(self, params: AnalysisParams) -> DataFrameReport:
        with plt.style.context('dark_background') if params.theme == DocumentTheme.DARK else nullcontext():
            self._report = DataFrameReport(dpi=params.dpi, theme=params.theme, show_time=params.show_time)
            self._include_visualizations = params.include_visualizations
            if params.include_basic_stats:
                self._basic_stats()
            self._task_based_recs(params.analysis_task, params.target_col)
            return self._report

    @staticmethod
    def get_metadata(data: pd.DataFrame) -> MetadataResponse:
        return MetadataResponse(
            num_rows=len(data),
            num_columns=len(data.columns),
            columns=data.dtypes.astype(str).to_dict()
        )
