# database

import zipfile
import json
from werkzeug.utils import secure_filename
import os
from flask import*
from detector.detector import Detector
import pymongo
client = pymongo.MongoClient(
    "mongodb+srv://BenYang:bentest@cluster0.tgv934g.mongodb.net/?retryWrites=true&w=majority")
db = client.base


# backend
UPLOAD_FOLDER = './detector/modules/past_modules'
ALLOWED_EXTENSIONS = set(['txt', 'zip', 'rar'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")  # 之後記得目錄
def index():
    return render_template("index.html")


@app.route("/temp_result")
def temp_result():
    return render_template("temp_rsult.html")


@app.route("/tool")
def tool():
    return render_template("tool.html")


@app.route("/rule")
def rule():
    return render_template("rule.html")


@app.route("/result")
def result():
    return render_template("result.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/temp")  # 丟到database用
def temp():
    preproccessing = request.args.get("preproccessing", "")
    model = request.args.get("model", "")
    other = request.args.get("other", "")

    collection = db.datas
    collection.insert_one({
        "preproccessing": preproccessing,
        "model": model,
        "other": other
    })
    return redirect("/index")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            f = open('./detector/modules/module_id.txt', 'r')
            module_id = f.read()
            f.close()
            f = open('./detector/modules/module_id.txt', 'w')
            temp = int(module_id)
            temp = temp+1
            module_id = str(temp)
            f.write(module_id)
            f.close()
            file.filename = "module_" + module_id + ".zip"
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                   filename))
            print("upload success")
            print(filename)
            path = "./detector/modules/past_modules/" + filename
            with zipfile.ZipFile(path, 'r') as zf:
                zf.extractall(path="./detector/modules/current_modules")
            dirpath = "./detector/modules/current_modules"
            name = os.listdir(dirpath)
            old_name = name[0]
            old_name_dir = "./detector/modules/current_modules/" + old_name
            new_name_dir = "./detector/modules/current_modules/" + "module_" + module_id
            os.rename(old_name_dir, new_name_dir)
            module_id = int(module_id)
       #     score = (Detector.get_score(module_id))
            score = "0.8"
            print(score)
            import shutil
            shutil.rmtree("./detector/modules/current_modules/" +
                          "module_" + str(module_id))
            return render_template("result.html", result=json.dumps(score))
    return render_template('upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route("/history")
def history():
    return render_template("history.html")


if __name__ == "__main__":
    #  app.run(host="0.0.0.0", port = 8000)
    app.run(debug=True)
