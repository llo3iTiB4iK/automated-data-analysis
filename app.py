import pandas as pd
from flask import Flask, request, render_template, send_file, Response, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.datastructures import FileStorage
from typing import BinaryIO
from io import BytesIO
import error_handlers as eh
from services.data_uploading import load_data
from services.data_processing import process_data
from services.data_analysis import analyze_data
from services.report_generation import generate_report
from services.storage_operations import delete_old_files, get_from_storage, save_to_storage



app: Flask = Flask(__name__)
app.register_error_handler(KeyError, eh.missing_parameter)
app.register_error_handler(ValueError, eh.incorrect_parameter)
app.register_error_handler(405, eh.method_not_allowed)

scheduler = BackgroundScheduler()



@app.route("/")
def home() -> str:
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file() -> dict:
    # todo: implement size and format limitations
    file: FileStorage = request.files['file']
    params: dict = request.form.to_dict()
    data: pd.DataFrame = load_data(file, params)
    dataset_id: str = save_to_storage(data)
    return {
        "message": "Dataset uploaded successfully",
        "dataset_id": dataset_id,
        "next_step": url_for("preprocess_dataset", dataset_id=dataset_id),
        "metadata": {
            "num_rows": len(data),
            "num_columns": len(data.columns),
            "columns": data.dtypes.astype(str).to_dict()
        }
    }


@app.route("/preprocess/<dataset_id>", methods=["POST"])
def preprocess_dataset(dataset_id: str) -> dict:
    # TODO: decide whether preprocessed dataset should have new ID
    params: dict = request.form.to_dict()
    data: pd.DataFrame = get_from_storage(dataset_id)
    data = process_data(data, params)
    save_to_storage(data, dataset_id)
    return {
        "message": "Dataset preprocessed successfully",
        "dataset_id": dataset_id,
        "next_step": url_for("get_recommendations", dataset_id=dataset_id),
        "metadata": {
            "num_rows": len(data),
            "num_columns": len(data.columns),
            "columns": data.dtypes.astype(str).to_dict()
        }
    }


@app.route("/dataset_info/<dataset_id>")
def get_info(dataset_id: str) -> dict:
    data: pd.DataFrame = get_from_storage(dataset_id)
    return {
        "message": "Dataset found successfully",
        "dataset_id": dataset_id,
        "next_step": url_for("preprocess_dataset", dataset_id=dataset_id),
        "metadata": {
            "num_rows": len(data),
            "num_columns": len(data.columns),
            "columns": data.dtypes.astype(str).to_dict()
        }
    }


@app.route("/download/<dataset_id>")
def download_dataset(dataset_id: str) -> Response:
    data: pd.DataFrame = get_from_storage(dataset_id)
    dataset_buffer: BinaryIO = BytesIO()
    data.to_csv(dataset_buffer, index=False)
    dataset_buffer.seek(0)
    return send_file(dataset_buffer, mimetype='text/csv', as_attachment=False, download_name=f'{dataset_id}.csv')


@app.route("/recommendations/<dataset_id>")
def get_recommendations(dataset_id: str) -> Response:
    data: pd.DataFrame = get_from_storage(dataset_id)
    params: dict = request.form.to_dict()
    # TODO: merge analysis and report-building logic
    analysis_results: dict = analyze_data(data)
    pdf_buffer: BinaryIO = generate_report(analysis_results)
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=False, download_name='report.pdf')


if __name__ == "__main__":
    scheduler.add_job(delete_old_files, "interval", hours=1)
    scheduler.start()
    app.run(debug=True, use_reloader=False)
