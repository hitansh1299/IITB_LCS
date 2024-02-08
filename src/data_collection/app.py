from flask import Flask, render_template, redirect, flash, request, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from config import UPLOAD_FOLDER, DATABASE, ALLOWED_EXTENSIONS
from flask_cors import cross_origin

app = Flask(__name__,
            template_folder="./templates",
            static_folder="./static/assets/",
            static_url_path='/assets/')

# app = Flask(__name__,
#             template_folder="./templates",
#             static_folder="./static/",
#             static_url_path='/static')

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

        

@app.route('/fileupload', methods=['GET', 'POST'])
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
    

    return render_template('upload_file.html')
    

@app.route('/download_file/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route('/listfiles', methods=['GET'])
def list_files():
    data = os.listdir(app.config["UPLOAD_FOLDER"])
    d = {str(x): f'/download_file/{str(x)}' for x in filter(lambda x: x != 'log.json', data)}
    # print(data)
    return jsonify(d)

@app.route('/viewdata', methods=['GET'])
def view_data():
    # return render_template('viewdata.html')
    return render_template('datatable.html')

@app.route('/getchartingdata', methods=['GET'])
def get_charting_data():
    from api import __get_charting_data__
    req = dict(request.args.lists())
        
    print('Printing request', req)
    data = __get_charting_data__(sensors = req.get('sensors',[]), 
                       start = req.get('start')[0], 
                       end = req.get('end')[0])
    print(data)
    response = jsonify(data)
    return response

@app.route('/plotdata', methods=['GET'])
@app.route('/', methods=['GET'])
def plot_data():       
    # return render_template('plotdata.html')
    return render_template('dashboard.html')

@app.route('/getData/<table>/<raw>', methods=['GET'])
def get_data(table, raw):
    from api import get_data
    return jsonify(get_data(table, raw=raw))

@app.route('/delete/<filename>')
def delete_file(filename):
    from api import delete_file
    print(filename)
    delete_file(filename)
    return redirect(url_for('view_files'))
    
@app.route('/viewfiles', methods=['GET'])
def view_files():
    # return render_template('viewfiles.html')
    return render_template('filetable.html')

if __name__ == '__main__':
    app.run(debug=True)
