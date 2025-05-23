# 🧠 Automated Data Analysis and Reporting Web Service

This project is a **Flask-based web service** for automated data preprocessing and report generation. It helps users clean, transform, and analyze tabular datasets with task-specific recommendations (regression, classification, clustering), and generate insightful PDF reports.

---

## 🌟 Features

* 📤 Upload tabular datasets (CSV, Excel, JSON, database dumps).
* ⚙️ Flexible, parameterized preprocessing pipeline.
* 💡 Automatic suggestions based on dataset/task type.
* 📄 PDF report generation with metrics and visualizations.
* 🧹 Temporary dataset management with automatic cleanup.

---

## 📁 Project Structure

```
automated-data-analysis/
├── app/                      
│   ├── controllers/         # Core logic and helpers
│   ├── data_exchange/       # Upload/download API blueprint
│   ├── extensions/          # App-wide extensions (e.g., storage manager)
│   ├── main/                # Not specific to any single module logic blueprint
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
python main.py
```

✅ You’re now ready to use the service locally at [http://localhost:5000](http://localhost:5000)!

---

## 📡 REST API Endpoints

| Method | Endpoint                         | Description                                  |
|--------|----------------------------------|----------------------------------------------|
| `GET`  | `/`                              | Application homepage                         |
| `POST` | `/upload`                        | Upload a dataset                             |
| `POST` | `/preprocess/<dataset_id>`       | Apply preprocessing with parameters          |
| `GET`  | `/dataset_info/<dataset_id>`     | Get dataset metadata                         |
| `GET`  | `/download/<dataset_id>`         | Download preprocessed dataset                |
| `GET`  | `/recommendations/<dataset_id>`  | Generate PDF analytical report               |
| `POST` | `/all_stages`                    | Full pipeline: upload → preprocess → report  |

---

## 📝 Key Notes

* 🔁 **Auto cleanup**: Datasets are deleted every 12 hours.
* 🧠 **Stateless**: No DB; all state is in memory/temp files.
* 🔐 **Security**: Uploads are sandboxed; access requires `X-Dataset-Token`.
* 🧾 **Error Handling**: Informative JSON errors.
* 📡 **RESTful API**: JSON in/out (except files and reports).
* 🧱 **Modular**: Clean architecture for easy extension.

---

## ☁️ Deployment on PythonAnywhere

### 1️⃣ Sign Up / Log In

Visit [pythonanywhere.com](https://www.pythonanywhere.com) and create an account or log in.

---

### 2️⃣ Set Up Virtual Environment

Open the **Bash console** from the *Consoles* tab and run:

```bash
mkvirtualenv myflaskenv --python=python3.10
git clone --branch master --single-branch https://github.com/llo3iTiB4iK/automated-data-analysis.git
cd automated-data-analysis
pip install --no-cache-dir -r requirements.txt
```

> ⚠️ If you hit memory errors, re-run `pip install` — installation requires ~500 MB.

---

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

---

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

---

✅ **Deployment Ready!**
Your service is live at:

```
https://<your-username>.pythonanywhere.com
```