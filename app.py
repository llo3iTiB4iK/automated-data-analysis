import pandas as pd
from flask import Flask, request, render_template
from werkzeug.datastructures import FileStorage
import error_handlers as eh
from services.data_processing import process_data

app: Flask = Flask(__name__)
app.register_error_handler(KeyError, eh.missing_parameter)
app.register_error_handler(ValueError, eh.incorrect_parameter)


@app.route("/")
def home() -> str:
    return render_template("index.html")  # TODO: make template have interface for all parameters


@app.route("/analyze", methods=["POST"])
def upload_file() -> str:
    file: FileStorage = request.files['file']
    params: dict = request.form.to_dict()
    processed_data: pd.DataFrame = process_data(file, params)
    # TODO: add analysis of preprocessed data
    # analysis_results = analyze_data(processed_data, params)
    # TODO: add result-based report generation and its' return
    # report_path = generate_report(analysis_results)
    return processed_data.to_html()


if __name__ == "__main__":
    app.run(debug=True)
