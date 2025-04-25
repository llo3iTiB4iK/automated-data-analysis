# Automated Data Analysis and Reporting Web Service

This project is a **web service** for automated data preprocessing and report generation. It helps users clean, transform, and understand datasets by offering intuitive recommendations based on the task type (regression, classification, clustering).

## 🌐 Features

- Upload tabular datasets (CSV, Excel, JSON, DB).
- Flexible parameterized data preprocessing.
- Automated suggestions based on dataset and task.
- PDF report generation with insights and diagrams.
- Efficient server-side dataset management.

## 📁 Project Structure

```
automated-data-analysis/
├── app/                      
│   ├── controllers/         # Request handlers and route logic
│   ├── data_exchange/       # Data upload/download blueprint
│   ├── errors/              # Custom error classes and handlers
│   ├── extensions/          # Custom extensions
│   ├── main/                # Main blueprint
│   ├── models/              # Pydantic form data models
│   ├── preprocessing/       # Data preprocessing blueprint
│   ├── reporting/           # Report generation blueprint
│   ├── templates/           # HTML templates
│   │   └── index.html       # Application main page
│   └── __init__.py          # Application factory
├── datasets/                # Temporary dataset storage (created on runtime)
├── fonts/                   # Fonts for PDF reports
├── sample_data/             # Example datasets
├── config.py                # Application configuration
├── main.py                  # Application entry point
├── README.md
└── requirements.txt         # Dependencies
```

## ⚙️Local Setup Instructions

### 1. Clone the Project Repository

First, clone the project from GitHub:

```bash
git clone https://github.com/llo3iTiB4iK/automated-data-analysis.git
cd automated-data-analysis
```

### 2. Create and Activate a Virtual Environment

Create a virtual environment to isolate your dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

- On **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- On **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

With the virtual environment active, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

After installing the dependencies, you can start the application:

```bash
python main.py
```

This will start the Flask development server. By default, the app will be available at [http://localhost:5000](http://localhost:5000)

---

✅ **Local Setup Complete!**  
The application is now running locally and ready to process datasets!

## 🚀 API Endpoints

| Method | Endpoint                         | Description                                 |
|--------|----------------------------------|---------------------------------------------|
| `GET`  | `/`                              | Application home page                       |
| `POST` | `/upload`                        | Upload a dataset                            |
| `POST` | `/preprocess/<dataset_id>`       | Preprocess dataset with parameters          |
| `GET`  | `/dataset_info/<dataset_id>`     | Get dataset metadata                        |
| `GET`  | `/download/<dataset_id>`         | Download preprocessed dataset               |
| `GET`  | `/recommendations/<dataset_id>`  | Generate PDF report                         |
| `POST` | `/all_stages`                    | Full pipeline: upload → preprocess → report |

## 📌 Key Notes

- **Automatic cleanup:** Old datasets are deleted every 12 hours.
- **Stateless design:** No database used; data stored in memory/temp files.
- **Security:** Uploaded files are isolated in temporary storage.
- **Privacy:** Dataset access requires `X-Dataset-Token` header (provided once on upload).
- **Error handling:** JSON-formatted informative error messages returned.
- **REST API:** JSON requests/responses for all endpoints except file upload/download and recommendation report.
- **Scalability:** Modular architecture allows easy component replacement.

## 🌐 Deployment Guide (PythonAnywhere)

Follow these steps to deploy the service on [PythonAnywhere](https://www.pythonanywhere.com/):

### 1. Create an account / Log in

Go to [pythonanywhere.com](https://www.pythonanywhere.com/) and **sign up** or **log in**.

---

### 2. Create a new Flask app

- Go to the **"Web"** tab
- Click **"Add a new web app"**
- Choose:
  - **Flask** as the framework
  - **Python 3.10** as the interpreter
- When asked for the path to your app, set it to:
  ```bash
  /home/your_username/your_project_folder/main.py
  ```
- Proceed to app creation

---

### 3. Create a virtual environment

- Go to the **"Consoles"** tab
- Open a **Bash console**
- Create a virtual environment:
  ```bash
  mkvirtualenv your_venv_name --python=python3.10
  ```

---

### 4. Activate the virtual environment

If it's not activated automatically, run:
```bash
workon your_venv_name
```

---

### 5. Upload project files and check available disk space

1. Go to the `Files` tab on [PythonAnywhere](https://www.pythonanywhere.com/).

2. If a default `main.py` file was created during web app setup, **delete it**:
   - Navigate to `/home/your_username/your_project_folder/main.py`
   - Click the 🗑️ icon or open the file and use the **Delete file** option

3. **Upload your project files** to the project directory:
   - Either drag and drop a `.zip` archive and unzip it in place
   - **OR** upload the files individually via the interface

4. Set `ENV` variable to `"prod"` in `config.py` file.

5. **Make sure there's enough free disk space (~450 MB)**:
   - In a Bash console, run:
     ```bash
     df -h
     ```
   - **OR** check the top of the `Files` page for something like:
     ```
     Disk usage: 120 MB of 512 MB used
     ```

---

### 6. Navigate to your project folder

```bash
cd your_project_folder
```

---

### 7. Install dependencies (with retry if needed)

Due to limited disk space, installation may fail the first time. Follow these steps:

1. Try installing:
   ```bash
   pip install -r requirements.txt
   ```

2. If you get a `Disk quota exceeded` error, clean the cache:
   ```bash
   rm -rf ~/.cache/*
   ```

3. **Repeat steps 1–2** until no errors occur.

You’re done when you do **NOT** see:
```bash
ERROR: Could not install packages due to an OSError: [Errno 122] Disk quota exceeded
```

---

### 8. Configure web app to use your virtual environment

- Go back to the **"Web"** tab
- In **"Source code"**, point to your app folder:
  ```
  /home/your_username/your_project_folder
  ```
- Repeat the action for **"Working directory"**
- In the **"Virtualenv"** section, enter:
  ```
  /home/your_username/.virtualenvs/your_venv_name
  ```
- Hit **Reload** at the top of the page

---

### 9. Create a scheduled task for automatic cleanup

To automatically delete old datasets from the server storage, create a **scheduled task** on PythonAnywhere:

1. Go to the **"Tasks"** tab on [PythonAnywhere](https://www.pythonanywhere.com/user/your_username/schedule/)

2. Click **"Add a new scheduled task"**

3. In the **Command** field, enter:

   ```bash
   cd /home/your_username/your_project_folder && source /home/your_username/.virtualenvs/your_venv_name/bin/activate && flask cleanup
   ```

4. Set the frequency depending on your needs

5. Click **"Create"**

> 🔁 **For free-tier accounts**:
> - You cannot choose the frequency of your scheduler task - it is run daily
> - You’ll need to **manually extend the expiry date** of your scheduled task each time it gets close to expiring.  
> - Also go to the **"Web"** tab and set the web app to **"Run until 3 months from now"** to avoid early suspension.

---

✅ **Deployment Complete!**  
Your service should now be up and running!