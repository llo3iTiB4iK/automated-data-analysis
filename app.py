import pandas as pd
from flask import Flask, request, render_template
from werkzeug.datastructures import FileStorage
import error_handlers as eh
from services.data_processing import process_data
from services.data_analysis import analyze_data

app: Flask = Flask(__name__)
app.register_error_handler(KeyError, eh.missing_parameter)
app.register_error_handler(ValueError, eh.incorrect_parameter)


@app.route("/")
def home() -> str:
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def upload_file() -> dict:
    file: FileStorage = request.files['file']
    params: dict = request.form.to_dict()
    processed_data: pd.DataFrame = process_data(file, params)
    analysis_results: dict = analyze_data(processed_data, params)
    # TODO: add result-based report generation and its' return
    # report_path = generate_report(analysis_results)
    return analysis_results


if __name__ == "__main__":
    app.run(debug=True)
