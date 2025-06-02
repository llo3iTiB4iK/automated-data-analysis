# 🧠 Automated Data Analysis and Reporting Web Service

This project is a **Flask-based web service** for automated data preprocessing and report generation. It helps users clean, transform, and analyze tabular datasets with task-specific recommendations (regression, classification, clustering), and generate insightful PDF reports.

---

## 🚀 Features & Highlights

* 📤 **Upload & Download**: Seamlessly upload and download tabular datasets (CSV, Excel, JSON, etc.).
* ⚙️ **Flexible Preprocessing**: Utilize a flexible, parameterized preprocessing pipeline for data cleaning and transformation.
* 💡 **Smart Suggestions**: Get automatic task-specific recommendations (regression, classification, clustering) based on your dataset type.
* 📄 **Insightful Reporting**: Generate parameterized PDF reports complete with key metrics and visualizations.
* 🧹 **Temporary Data Management**: Datasets are managed temporarily with automatic cleanup every 12 hours.
* 🧠 **Stateless Design**: The service is stateless, operating without a database; all state is handled in memory or via temporary files.
* 🔐 **Secure Uploads**: Uploaded datasets are sandboxed, and access requires an `X-Dataset-Token` for enhanced security.
* ⚠️ **Robust Error Handling**: Features advanced error handling using Werkzeug and custom exceptions for a smooth user experience.
* 📡 **RESTful API**: Interact with the service via a clear RESTful API, primarily using JSON for requests and responses (except file operations).
* 🧱 **Modular Architecture**: Built with a clean, modular structure, making it easy to extend and maintain.
* 🧾 **Self-Documenting API**: The API is self-documented using [`flask-pydantic-spec`](https://pypi.org/project/flask-pydantic-spec/).

---

## 📡 REST API Endpoints

| Method | Endpoint                            | Description                                 |
|--------|-------------------------------------|---------------------------------------------|
| `GET`  | `/`                                 | API Docs links                              |
| `POST` | `/datasets`                         | Upload a dataset                            |
| `GET`  | `/datasets/<dataset_id>`            | Get dataset metadata                        |
| `POST` | `/datasets/<dataset_id>/preprocess` | Apply preprocessing with parameters         |
| `GET`  | `/datasets/<dataset_id>/download`   | Download preprocessed dataset               |
| `GET`  | `/datasets/<dataset_id>/report`     | Generate PDF analytical report              |
| `POST` | `/datasets/full_pipeline`           | Full pipeline: upload → preprocess → report |

---

## 📁 Project Structure

```
automated-data-analysis/
├── app/  
│   ├── controllers/         # Core logic classes
│   ├── data_exchange/       # Upload/download API blueprint
│   ├── extensions/          # App-wide extensions (e.g., storage manager)
│   ├── system/              # Application-level logic blueprint
│   ├── models/              # Pydantic data validation models
│   ├── preprocessing/       # Data transformation blueprint
│   ├── reporting/           # PDF report generation blueprint
│   ├── errors.py            # Custom exception classes
│   ├── handlers.py          # Functions to handle app errors
│   └── __init__.py          # Application factory pattern
├── datasets/                # Temporary dataset storage
├── fonts/                   # Fonts used in PDF reports
├── config.py                # Configuration settings
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
└── README.md
```

---

## ⚙️ Local Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/llo3iTiB4iK/automated-data-analysis.git
cd automated-data-analysis
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
```

Activate it:
* **Windows**:

  ```bash
  venv\Scripts\activate
  ```
* **Linux/macOS**:

  ```bash
  source venv/bin/activate
  ```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```bash
python system.py
```

✅ You’re now ready to use the service locally at [http://localhost:5000](http://localhost:5000)!

-----

## ☁️ Deployment on PythonAnywhere

### 1️⃣ Sign Up / Log In

Visit [pythonanywhere.com](https://www.pythonanywhere.com) and create an account or log in.

-----

### 2️⃣ Set Up Virtual Environment

Open the **Bash console** from the *Consoles* tab and run:

```bash
mkvirtualenv myflaskenv --python=python3.10
git clone --branch master --single-branch https://github.com/llo3iTiB4iK/automated-data-analysis.git
cd automated-data-analysis
pip install --no-cache-dir -r requirements.txt
```

> ⚠️ If you hit memory errors, re-run `pip install` — installation requires ~500 MB.

-----

### 3️⃣ Configure Web App

In the **Web** tab:

* Click **Add a new web app**
* Choose:
  * Domain: `Next >>`
  * Framework: `Manual configuration`
  * Python: `Python 3.10`
  * Manual config: `Next >>`

After creation configure:

* **Source code** && **Working directory**: `automated-data-analysis`
* **WSGI configuration file** - open and replace contents with:
```python
import sys
import os

path = '/home/<your-username>/automated-data-analysis'
if path not in sys.path:
    sys.path.append(path)

os.environ['ENV'] = 'prod'

from main import app as application  # noqa
```
* **Virtualenv**: `myflaskenv`
* **Force HTTPS**: `Enabled`

🔁 Hit **Reload** at the top of the page

-----

### 4️⃣ Add Scheduled Cleanup

In the **Tasks** tab:

* Click **Add a new scheduled task**

* Command:

  ```bash
  workon myflaskenv && cd automated-data-analysis && flask cleanup
  ```

* Set time/frequency as needed

* Optionally add a description

> ℹ️ On free-tier accounts:
>
> * Task runs only once per day
> * You must manually extend expiry in the **Consoles** tab
> * Also extend app lifetime in the **Web** tab ("Run until 3 months from now")

-----

✅ **Deployment Ready!**
Your service is live at:

```
https://<your-username>.pythonanywhere.com
```