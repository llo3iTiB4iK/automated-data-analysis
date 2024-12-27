from flask import Flask, request
import error_handlers as eh
from services.data_proccessing import process_data

app = Flask(__name__)
app.register_error_handler(KeyError, eh.missing_parameter)
app.register_error_handler(ValueError, eh.incorrect_parameter)


@app.route("/")
def home():
    return '''
        <!doctype html>
        <title>Upload File</title>
        <h1>Upload a file</h1>
        <form action="/analyze" method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <input type="submit" value="Upload">
        </form>
        '''


@app.route("/analyze", methods=["POST"])
def upload_file():
    file = request.files['file']
    filename = file.filename
    params = request.form.to_dict()
    processed_data = process_data(file, filename, params)
    #analysis_results = analyze_data(processed_data, params)
    #report_path = generate_report(analysis_results)
    return processed_data.to_html()


if __name__ == "__main__":
    app.run(debug=True)
