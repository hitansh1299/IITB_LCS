#create a basic flask app
import os
from flask import Flask, render_template, redirect, flash, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
UPLOAD_FOLDER = 'C:/Users/hitan/OneDrive/Desktop/MiniProjects/IITB_LCS/src/data_collection/uploads'
ALLOWED_EXTENSIONS = {'xls','xlsx'}
app = Flask(__name__,
            template_folder="./templates",
            static_folder="./static")
app.secret_key = "HITANSH123IITBLCS"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        if 'location' not in request.form:
            print('No location part')
            print(request.form)
            return redirect(request.url)
        else:
            location = request.form['location']
            print(location)

        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            print('bad filename')
            return redirect(request.url)
        print('file valid')
        if file and allowed_file(file.filename):
            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + request.form['location']+ "_" + request.form['type'] + "_" + secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_file(filename=filename)
            print('File saved successfully')
            # return redirect(url_for('download_file', name=filename))
    return render_template('index.html')

@app.route('/download_file/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/listfiles', methods=['GET'])
def list_files():
    data = os.listdir(app.config["UPLOAD_FOLDER"])
    print(data)
    return jsonify(data)

def process_file(filename: str):
    pass

if __name__ == '__main__':
    app.run(debug=True)
