import json

import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import io

matplotlib.use('Agg')
sns.set_style("darkgrid")


def generate_plot_to_bytesio(plot_func: callable) -> io.BytesIO:
    plot_func()
    buf: io.BytesIO = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf


def analyze_data(data: pd.DataFrame, params: dict) -> dict:
    # TODO: add info() та describe()
    print(data.duplicated().any())

    numerical_columns: pd.DataFrame = data.select_dtypes(include='number').columns
    categorical_columns: pd.DataFrame = data.select_dtypes(include='category').columns
    boolean_columns: pd.DataFrame = data.select_dtypes(include='bool').columns
    datetime_columns: pd.DataFrame = data.select_dtypes(include='datetime').columns
    string_columns: pd.DataFrame = data.select_dtypes(include='object').columns

    plot_images: list = []

    if data.isna().values.any():
        counts_df = pd.DataFrame({
            'Missing values': data.isna().sum(),
            'Non-missing values': data.notna().sum()
        }).reset_index().melt(id_vars='index', var_name='Type', value_name='Count')
        plot_images.append(generate_plot_to_bytesio(
            lambda: sns.barplot(counts_df, x='Count', y='index', hue='Type', orient='h').set_title("Missing values by column")
        ))

    for col in numerical_columns:
        plot_images.append(generate_plot_to_bytesio(
            lambda: sns.boxplot(x=data[col]).set_title(f"Distribution of '{col}'")
        ))
        #sns.histplot(data=df, x='numeric_column', hue='category_column', kde=True)+title

    for col in categorical_columns:
        plot_images.append(generate_plot_to_bytesio(
            lambda: sns.countplot(data, x=col, hue=col).set_title(f"Value counts for each category of '{col}'")
        ))
        #sns.countplot(data=df, x="category1", hue="category2")+title
        #sns.barplot(x='category', y='numeric_column', data=df)+title
        #sns.boxplot(x='category', y='numeric_column', data=df)+title

    for col in boolean_columns:
        plot_images.append(generate_plot_to_bytesio(
            lambda: data[col].plot.pie(title=f"Distribution of '{col}' values")
        ))
        #the same as for categorical

    for col in datetime_columns:
        plot_images.append(generate_plot_to_bytesio(
            lambda: sns.histplot(data[col], kde=True).set_title(f"Distribution of '{col}' over time")
        ))
        #sns.lineplot(x='date_column', y='numeric_column', data=df)+title#byDate = df[df.Reason == reason].groupby("Date").count()

    for col in string_columns:
        plot_images.append(generate_plot_to_bytesio(
            lambda: sns.histplot(data[col].dropna().apply(len)).set_title(f"Text length distribution for '{col}'")
        ))

    if len(numerical_columns) > 1:
        plot_images.append(generate_plot_to_bytesio(
            lambda: sns.heatmap(data.corr(numeric_only=True), cmap='coolwarm', annot=True).set_title("Numeric columns correlation heatmap")
        ))
        plot_images.append(generate_plot_to_bytesio(
            lambda: sns.pairplot(data, kind='reg').fig.suptitle("Pairwise relationships of numeric columns")
        ))

    return json.loads(data.describe(include='all').to_json())
