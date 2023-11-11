from flask import Flask, render_template, redirect, flash, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import os

UPLOAD_FOLDER = 'C:/Users/hitan/OneDrive/Desktop/MiniProjects/IITB_LCS/src/data_collection/uploads'
DATABASE = 'C:/Users/hitan/OneDrive/Desktop/MiniProjects/IITB_LCS/Data/database.db'
ALLOWED_EXTENSIONS = {'xls', 'xlsx', 'csv', 'txt'}

app = Flask(__name__,
            template_folder="./templates",
            static_folder="./static")
app.secret_key = "HITANSH123IITBLCS"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATABASE'] = DATABASE
# app.config['JSON_SORT_KEYS'] = False
app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)
app.json.sort_keys = False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_filename(params, filename):
    filename = request.form['type'] + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + \
                request.form['location'] + "_" + \
                "_" + secure_filename(filename)
    return filename

import json
def log(filename: str):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'log.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'log.json'), 'w', encoding='utf-8') as f:
        data[filename] = request.form
        json.dump(data,f, ensure_ascii=False, indent=4)

        

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    from api import process_file
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            print('bad filename')
            return redirect(request.url)
        print('file valid')
        if file and allowed_file(file.filename):
            filename = generate_filename(request.form, file.filename)
            log(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_file(path=app.config['UPLOAD_FOLDER'], filename=filename)
            print('File saved successfully')
            # return redirect(url_for('download_file', name=filename))
    return render_template('index.html')

@app.route('/download_file/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/listfiles', methods=['GET'])
def list_files():
    data = os.listdir(app.config["UPLOAD_FOLDER"])
    d = {str(x): f'/download_file/{str(x)}' for x in data}
    # print(data)
    return jsonify(d)

@app.route('/viewdata', methods=['GET'])
def view_data():
    return render_template('viewdata.html')

@app.route('/getData/<table>', methods=['GET'])
def getData(table):
    from api import get_data
    return jsonify(get_data(table))


@app.route('/viewfiles', methods=['GET'])
def view_files():
    return render_template('viewfiles.html')

if __name__ == '__main__':
    app.run(debug=True)
