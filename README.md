# Automated Data Analysis and Reporting Web Service

This project is a **web service** for automated data preprocessing and report generation. It helps users clean, transform, and understand their datasets by offering intuitive recommendations based on the task type (regression, classification, clustering).

---

## 🌐 Deployment Steps (PythonAnywhere)

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
  /home/your_username/your_project_folder/app.py
  ```

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

2. If a default `app.py` file was created during web app setup, **delete it**:
   - Navigate to `/home/your_username/your_project_folder/app.py`
   - Click the 🗑️ icon or open the file and use the **Delete file** option

3. **Upload your project files** to the project directory:
   - Either drag and drop a `.zip` archive and unzip it in place
   - **OR** upload the files individually via the interface

4. **Make sure there's enough free disk space**:
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

You’re done when you do **not** see:
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
- Repeat the previous action for **"Working directory"**
- Hit **Reload** at the top of the page
- In the **"Virtualenv"** section, enter:
  ```
  /home/your_username/.virtualenvs/your_venv_name
  ```

---


### 9. Create a scheduled task for automatic cleanup

To automatically delete old datasets from the server storage, create a **scheduled task** on PythonAnywhere:

1. Go to the **"Tasks"** tab on [PythonAnywhere](https://www.pythonanywhere.com/user/your_username/schedule/)

2. Click **"Add a new scheduled task"**

3. In the **Command** field, enter:

   ```bash
   python3 /home/your_username/your_project_folder/cleaner.py
   ```

4. Set the frequency (**"daily"** only available for free-tier accounts), depending on your needs

5. Click **"Create"**

> 🔁 **For free-tier accounts**:  
> - You’ll need to **manually extend the expiry date** of your scheduled task each time it gets close to expiring.  
> - Also go to the **"Web"** tab and set the web app to **"Run until 3 months from now"** to avoid early suspension.

---

✅ Your service should now be up and running!