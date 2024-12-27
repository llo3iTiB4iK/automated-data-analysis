import pandas as pd


def process_data(file, filename, params):
    extension = filename.split('.')[-1].lower()

    if extension == 'csv':
        data = pd.read_csv(file)
    elif extension in ['xls', 'xlsx']:
        data = pd.read_excel(file)
    elif extension == 'json':
        data = pd.read_json(file)
    else:
        raise ValueError("Unsupported file format. Please upload CSV, Excel, or JSON files.")

    return data
