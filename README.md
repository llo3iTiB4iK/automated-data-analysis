# Automated Data Analysis and Reporting Web Service

This project is a **web service** for automated data preprocessing and report generation. It helps users clean, transform, and understand their datasets by offering intuitive recommendations based on the task type (regression, classification, clustering).

## 🌐 Features

- Upload tabular datasets (CSV, Excel, JSON, DB).
- Flexible parameterized data preprocessing.
- Automated suggestions based on dataset and task.
- PDF report generation with insights and diagrams.
- Efficient server-side dataset management.

## 📁 Project Structure

```
├── app.py                    # Main Flask application
├── error_handlers.py         # Custom error handlers
├── errors.py                 # Error messages and exceptions
├── requirements.txt          # Python package dependencies
├── fonts/                    # Fonts used in generated reports
├── sample_data/              # Example input datasets
├── services/
│   ├── data_uploading.py     # Handles dataset upload and reading
│   ├── data_processing.py    # Core preprocessing logic
│   ├── data_analysis.py      # Generates PDF recommendations
│   ├── storage_operations.py # Dataset storage/retrieval & cleanup
│   ├── helpers/              # Helper classes to be used in services
├── templates/
│   └── index.html            # Frontend upload interface
```

## ⚙️ Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**

   ```bash
   python app.py
   ```

3. The service will be available at [http://localhost:5000](http://localhost:5000)

## 🚀 API Endpoints

| Method | Endpoint                         | Description                                  |
|--------|----------------------------------|----------------------------------------------|
| GET    | `/`                              | Home page with upload form                   |
| POST   | `/upload`                        | Upload a dataset                             |
| POST   | `/preprocess/<dataset_id>`       | Preprocess a dataset with given parameters   |
| GET    | `/dataset_info/<dataset_id>`     | Get basic dataset info                       |
| GET    | `/download/<dataset_id>`         | Download preprocessed dataset                |
| GET    | `/recommendations/<dataset_id>`  | Get PDF report with recommendations          |
| POST   | `/all_stages`                    | Upload, preprocess, and generate report in one call |

## 📌 Notes

- The server automatically deletes old datasets every 12 hours.
- Data is kept in memory or temporary storage (no database).
- Reports are generated as in-memory PDF files (not saved on disk).