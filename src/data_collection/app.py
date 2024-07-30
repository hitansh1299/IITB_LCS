import json
from flask import Flask, render_template, redirect, flash, request, url_for, send_from_directory, jsonify, send_file, Response
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from config import UPLOAD_FOLDER, DATABASE, ALLOWED_EXTENSIONS, HOST, PORT
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


def log(filename: str):
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'log.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'log.json'), 'w', encoding='utf-8') as f:
        data[filename] = request.form
        json.dump(data, f, ensure_ascii=False, indent=4)


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


@app.route('/download_file/<path:name>', methods=['GET'])
def download_file(name):
    print('Downloading file', name)
    # folder = os.path.join(app.config['UPLOAD_FOLDER'], name)
    # print(folder)
    # Print CWD
    print(os.getcwd())
    return send_from_directory(f"{os.getcwd()}/{app.config['UPLOAD_FOLDER']}", name, as_attachment=True)

@app.route('/getchartingdata', methods=['GET'])
def get_charting_data():
    from api import __get_charting_data__
    req = dict(request.args.lists())

    print('Printing request', req)
    data = __get_charting_data__(sensors=req.get('sensors',[]),
                                 start=req.get('start')[0],
                                 end=req.get('end')[0],
                                 pm=req.get('pm'))
    print(data)
    response = jsonify(data)
    return response


@app.route('/plotdata', methods=['GET'])
@app.route('/', methods=['GET'])
def plot_data():
    # return render_template('plotdata.html')
    return render_template('dashboard.html')

@app.route('/analysis', methods=['GET'])
def analysis():
    return render_template('analyse.html')

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
    return render_template('filetable.html')

@app.route('/live/<sensor>/<imei>', methods=['POST'])
@app.route('/live/<sensor>', methods=['POST'])
def live_input(sensor):
    from api import process_live_input
    if sensor == 'grimm':
        from api import process_file
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
            return jsonify({'status': 'success', 'message': 'File uploaded successfully!'})
        return Response(jsonify({'status': 'error', 'message': 'Invalid File Name!'}), status=402)
    data = request.json
    process_live_input(sensor, data)
    return jsonify({'status': 'success', 'message': f'Live data for sensor {sensor} received successfully!'})

@app.route('/getlive/<sensor>', methods=['GET'])
def get_live_data(sensor):
    from api import get_live_data
    return jsonify(get_live_data(sensor))

@app.route('/getregressiondata', methods=['GET'])
def get_regression_data():
    from api import get_regression_data
    return jsonify(get_regression_data())

if __name__ == '__main__':
    from threading import Thread
    from async_threads import fetch_atmos_data
    Thread(target=fetch_atmos_data).start()   
    app.run(debug=False, host=HOST, port=PORT)

