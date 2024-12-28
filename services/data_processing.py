import pandas as pd
from werkzeug.datastructures.file_storage import FileStorage
from errors import ParameterError

drop_na_values: list = ['rows', 'columns']


def process_data(file: FileStorage, params: dict) -> pd.DataFrame:
    # Determine file extension
    extension: str = file.filename.split('.')[-1].lower()

    # Read data based on file extension
    data: pd.DataFrame
    # todo 1: add db reading
    if extension == 'csv':
        data = pd.read_csv(file.stream)
    elif extension in ['xls', 'xlsx']:
        data = pd.read_excel(file.stream)
    elif extension == 'json':
        data = pd.read_json(file.stream)
    else:
        raise ValueError("Unsupported file format. Please upload CSV, Excel, or JSON files.")

    # Drop missing values on demand
    drop_na: str = params.get('drop_na')
    if drop_na:
        if drop_na in drop_na_values:
            data.dropna(axis=params.get('drop_na'), inplace=True)
        else:
            raise ParameterError('drop_na', drop_na, drop_na_values)

    # Fill missing values on demand
    # todo 2: add filling NaN values

    # Drop outliers on demand
    # todo 3: add dropping outliers

    # Drop duplicates on demand
    # todo 4: add dropping duplicates

    # Convert data types on demand
    # todo 5: add type conversion

    # Convert text data on demand
    # todo 6: add text data conversion

    # Process categorical variables on demand
    # todo 7: add categorical variables processing
    # Using the "one-hot encoding" or "label encoding" method to convert categorical variables into numeric formats.
    # Об'єднання рідких категорій або категорій, які мають мало спостережень, у одну категорію.

    # Scale numeric data on demand
    # todo 8: add numeric data scaling

    return data
