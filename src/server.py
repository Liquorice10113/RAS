from flask import Flask, render_template, request, jsonify, send_file, Response
from random import random
#from utils import AssetsDB

app = Flask(__name__)

upload_dir = './upload/'

#assetsDB = AssetsDB()


id2name = dict()
name2id = dict()

def genRandomId():
    return str(int(random()*10e6))

@app.route("/<project_id>/upload",methods=['POST'],strict_slashes=False)
def upload(project_id):
    f = request.files['file']
    if f:
        print(f.filename)
        f.save(upload_dir+f.filename)
    return '<script>document;alert("ok")</script>'

@app.route("/")
def index():
    data = {
        "username":"default",
        "projects":[

        ]
    }
    for id in id2name:
        data['projects'] .append({
                    "name":id2name[id],
                    "id":id,
                    "modi":"Just now"
                })

    return render_template("index.html",data=data,width=450*len(data['projects'])+550)

@app.route("/add")
def add():
    name = request.args.get("name")
    if name in name2id:
        return jsonify({"result":"dup"})
    else:
        pid = genRandomId()
        name2id[name] = pid
        id2name[pid] = name
        return jsonify({"result":"ok","pid":pid})

@app.route("/delete")
def del_project():
    id = request.args.get("id")
    if id in id2name:
        name = id2name[id]
        del name2id[name]
        del id2name[id]
    return jsonify({"result":"ok"})

@app.route("/<project_id>")
def project(project_id):
    if project_id in id2name:
        data = {
            "project_name":id2name[project_id],
            "project_id":project_id
        }
        return render_template("system.html",data=data)
    else:
        return Response(response="Not found!",status=404,mimetype='text/html')

@app.route("/<project_id>/delete")
def delete(project_id):
    return project_id

@app.route("/<project_id>/submit")
def submit(project_id):
    return project_id

@app.route("/<project_id>/page")
def page(project_id):
    resp = ''
    if request.args.get('type') =='1':
        return getAssets(project_id)
    elif request.args.get('type') =='2':
        resp = "威胁分析"    
    elif request.args.get('type') =='3':
        resp = "脆弱性识别"
    elif request.args.get('type') =='4':
        resp = "综合风险分析"
    elif request.args.get('type') =='5':
        resp = "风险统计"
    elif request.args.get('type') =='6':
        resp = "不可接受风险处理"
    return resp

def getAssets(project_id):
    #assets = assetsDB.query(pid=project_id)
    asserts = [
        [1,2,3,4,5,6,7,8] for _ in range(80)
        #[1,2,3,4,5,6,7,8]
        ]
    return render_template("assets.html",data=asserts)


app.run(debug=True)