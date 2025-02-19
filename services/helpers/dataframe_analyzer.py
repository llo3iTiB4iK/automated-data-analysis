import pandas as pd
import seaborn as sns

sns.set_style("darkgrid")


class DataFrameAnalyzer:

    def __init__(self, df: pd.DataFrame):
        self.df: pd.DataFrame = df
        self.numerical_columns: pd.Index = df.select_dtypes(include='number').columns
        self.categorical_columns: pd.Index = df.select_dtypes(include='category').columns
        self.boolean_columns: pd.Index = df.select_dtypes(include='bool').columns
        self.datetime_columns: pd.Index = df.select_dtypes(include='datetime').columns
        self.string_columns: pd.Index = df.select_dtypes(include='object').columns

    def get_overall_dataframe_plots(self) -> list:
        plot_funcs: list = []

        if self.df.isna().values.any():
            counts_df: pd.DataFrame = pd.DataFrame({
                'Missing values': self.df.isna().sum(),
                'Non-missing values': self.df.notna().sum()
            })
            plot_funcs.append(lambda: counts_df.plot(kind='barh', stacked=True, title="Missing values by column"))

        # if len(self.numerical_columns) > 1:
        #     plot_funcs.append(lambda: sns.heatmap(self.df.corr(numeric_only=True), cmap='coolwarm', annot=True).
        #                       set_title("Numeric columns correlation heatmap"))

        return plot_funcs

    def get_two_column_plots(self) -> list:
        plot_funcs: list = []

        for num_col in self.numerical_columns:
            for cat_col in (self.categorical_columns.tolist() + self.boolean_columns.tolist()):
                plot_funcs.append(lambda nc=num_col, cc=cat_col: sns.histplot(self.df, x=nc, hue=cc, kde=True).
                                  set_title(f"Distribution of '{nc}' by '{cc}'"))
                plot_funcs.append(lambda nc=num_col, cc=cat_col: sns.barplot(self.df, x=cc, y=nc).set_title(
                        f"Comparison of '{nc}' values by '{cc}' categories"))
                plot_funcs.append(lambda nc=num_col, cc=cat_col: sns.boxplot(self.df, x=cc, y=nc).set_title(
                        f"Distribution of '{nc}' values by '{cc}' categories"))

        for cat_col1 in (self.categorical_columns.tolist() + self.boolean_columns.tolist()):
            for cat_col2 in (self.categorical_columns.tolist() + self.boolean_columns.tolist()):
                if cat_col1 != cat_col2:
                    plot_funcs.append(lambda cc1=cat_col1, cc2=cat_col2: sns.countplot(self.df, x=cc1, hue=cc2).
                                      set_title(f"Category distribution of '{cc1}' by '{cc2}'"))

        for datetime_col in self.datetime_columns:
            for num_col in self.numerical_columns:
                plot_funcs.append(lambda dc=datetime_col, nc=num_col: sns.lineplot(self.df, x=dc, y=nc).set_title(
                        f"'{nc}' over time for '{dc}'"))

        return plot_funcs

    def get_summary(self) -> str:
        return f"Data has {len(self.df)} rows; contains {len(self.numerical_columns)} numerical columns, " \
               f"{len(self.categorical_columns)} categorical columns, {len(self.boolean_columns)} boolean columns, " \
               f"{len(self.datetime_columns)} datetime columns and {len(self.string_columns)} string columns.\n" \
               f"Duplicate rows were{'' if self.df.duplicated().any() else ' not'} found.\n" \
               f"Missing values share = {round(self.df.isna().values.sum() / self.df.size * 100, 2)}% ."

    def get_description(self) -> str:
        desc: dict = self.df.describe(include='all').to_dict()
        formatted_str: str = ""

        for column, stats in desc.items():
            formatted_str += f"Statistics for column '{column}' (dtype: {self.df[column].dtype}):\n"
            for stat, value in stats.items():
                if pd.notna(value):
                    formatted_str += f"    {stat}: {value}\n"
            formatted_str += "\n"

        return formatted_str
