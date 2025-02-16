import pandas as pd
import os
import uuid
import time
from flask import Flask, request, render_template, send_file, Response
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.datastructures import FileStorage
from typing import BinaryIO
from io import BytesIO
import error_handlers as eh
from services.data_uploading import load_data
from services.data_processing import process_data
from services.data_analysis import analyze_data
from services.report_generation import generate_report

DATASET_STORAGE = "datasets"

app: Flask = Flask(__name__)
app.register_error_handler(KeyError, eh.missing_parameter)
app.register_error_handler(ValueError, eh.incorrect_parameter)
app.register_error_handler(FileNotFoundError, eh.file_not_found)
app.register_error_handler(405, eh.method_not_allowed)


def delete_old_files():
    if not os.path.isdir(DATASET_STORAGE):
        os.mkdir(DATASET_STORAGE)
    for file_path in os.listdir(DATASET_STORAGE):
        full_path = os.path.join(DATASET_STORAGE, file_path)
        if os.path.isfile(full_path) and (time.time() - os.path.getctime(full_path) > 24 * 3600):
            os.remove(full_path)


scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_files, "interval", hours=12)


@app.route("/")
def home() -> str:
    return render_template("index.html")


# @app.route("/analyze", methods=["POST"])
# def upload_file_() -> Response:
#     file: FileStorage = request.files['file']
#     params: dict = request.form.to_dict()
#     processed_data: pd.DataFrame = process_data(file, params)
#     analysis_results: dict = analyze_data(processed_data)
#     pdf_buffer: BinaryIO = generate_report(analysis_results)
#     return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=False, download_name='report.pdf')


@app.route("/upload", methods=["POST"])
def upload_file() -> dict:
    file: FileStorage = request.files['file']
    params: dict = request.form.to_dict()
    data: pd.DataFrame = load_data(file, params)

    data_file_name: str = str(uuid.uuid4())
    data_file_path: str = os.path.join(DATASET_STORAGE, data_file_name)
    if not os.path.isdir(DATASET_STORAGE):
        os.mkdir(DATASET_STORAGE)
    data.to_pickle(data_file_path)
    return {
        "message": "Dataset uploaded successfully",
        "dataset_id": data_file_name,
        "next_step": f"/preprocess/{data_file_name}",
        "metadata": {
            "num_rows": len(data),
            "num_columns": len(data.columns),
            "columns": data.dtypes.astype(str).to_dict()
        }
    }


@app.route("/preprocess/<dataset_id>", methods=["POST"])
def preprocess_dataset(dataset_id: str) -> dict:
    params: dict = request.form.to_dict()
    full_path: str = os.path.join(DATASET_STORAGE, dataset_id)
    if not os.path.exists(full_path):
        raise ValueError(f"Dataset with given ID '{dataset_id}' not found in storage.")
    data: pd.DataFrame = pd.read_pickle(full_path)
    data = process_data(data, params)
    data.to_pickle(full_path)
    return {
        "message": "Dataset preprocessed successfully",
        "next_step": f"/recommendations/{dataset_id}",
        "metadata": {
            "num_rows": len(data),
            "num_columns": len(data.columns),
            "columns": data.dtypes.astype(str).to_dict()
        }
    }


@app.route("/download/<dataset_id>")
def download_dataset(dataset_id: str) -> Response:
    full_path: str = os.path.join(DATASET_STORAGE, dataset_id)
    data: pd.DataFrame = pd.read_pickle(full_path)
    dataset_buffer: BinaryIO = BytesIO()
    data.to_csv(dataset_buffer, index=False)
    dataset_buffer.seek(0)
    return send_file(dataset_buffer, mimetype='text/csv', as_attachment=False, download_name=f'{dataset_id}.csv')


@app.route("/recommendations/<dataset_id>", methods=["POST"])
def get_recommendations(dataset_id: str) -> Response:
    return Response(f"recommendation for {dataset_id} dataset")


if __name__ == "__main__":
    scheduler.start()
    app.run(debug=True, use_reloader=False)
