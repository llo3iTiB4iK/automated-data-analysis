import pandas as pd
from flask import Flask, request
from werkzeug.datastructures import FileStorage
import error_handlers as eh
from services.data_processing import process_data

app: Flask = Flask(__name__)
app.register_error_handler(KeyError, eh.missing_parameter)
app.register_error_handler(ValueError, eh.incorrect_parameter)


@app.route("/")
def home() -> str:
    return '''
        <!doctype html>
        <title>Upload File</title>
        <h1>Аналіз набору даних</h1>
        <form action="/analyze" method="post" enctype="multipart/form-data">
            <label>
                <input type="file" name="file">
                Файл в форматі CSV, XLS/XLSX, JSON або DB (SQLite)
            </label>
            <div>
                <label>
                    <input type="text" name="sep">
                    Роздільник значень, якщо відмінний від коми (для CSV файлів)
                </label>
            </div>
            <div>
                <label>
                    <input type="text" name="thousands">
                    Роздільник тисяч, якщо є (для CSV або EXCEL файлів)
                </label>
            </div>
            <div>
                <label>
                    <input type="text" name="decimal">
                    Символ десяткової крапки, якщо відмінний від крапки (для CSV або EXCEL файлів)
                </label>
            </div>
            <div>
                <label>
                    <input type="text" name="sheet_name">
                    Назва листа, якщо не перший з доступних (для EXCEL файлів)
                </label>
            </div>
            <div>
                <label>
                    <input type="text" name="table_name">
                    Назва таблиці в БД (для DB файлів)
                </label>
            </div>
            <div>
                <label>
                    <input type="radio" name="drop_na" value="" checked>
                    Не видаляти пропущених даних
                </label>
                <label>
                    <input type="radio" name="drop_na" value="rows">
                    Видалити рядки з пропущеними даними
                </label>
                <label>
                    <input type="radio" name="drop_na" value="columns">
                    Видалити стовпці з пропущеними даними
                </label><br>
            </div>
            <div>
                <input type="checkbox" name="drop_duplicates">
                <label for="drop_na">Видалити рядки-дублікати</label>
            </div>
            <input type="submit" value="Upload">
        </form>
        '''


@app.route("/analyze", methods=["POST"])
def upload_file() -> str:
    file: FileStorage = request.files['file']
    params: dict = request.form.to_dict()
    processed_data: pd.DataFrame = process_data(file, params)
    # todo 9: add analysis of preprocessed data
    # analysis_results = analyze_data(processed_data, params)
    # todo 10: add result-based report generation and its' return
    # report_path = generate_report(analysis_results)
    return processed_data.to_html()


if __name__ == "__main__":
    app.run(debug=True)
