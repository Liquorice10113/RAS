from os import name
import time
from sqlite3.dbapi2 import Connection, connect
from flask import Flask, render_template, request, jsonify, send_file, Response
from random import random
from databaseRAS import *
import json
#from utils import AssetsDB

app = Flask(__name__)

upload_dir = './upload/'

#assetsDB = AssetsDB()

connection = Database()
assetDB = Asset(connection)
ftragilityDB = Fragility(connection)
threatDB = Threat(connection)
projectDB = Project(connection)

id2name = dict()
name2id = dict()
for project in projectDB.query_all():
        name = project[0]
        id_ = project[1]
        modi = project[4]
        id2name[id_] = name
        name2id[name] = id_


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
def show_project():
    data = {
        "username":"default",
        "projects":[

        ]
    }
    for project in projectDB.query_all():
        print(project)
        name = project[0]
        id_ = project[1]
        modi = project[4]
        data['projects'] .append({
                    "name":name,
                    "id":id_,
                    "modi":modi
                })
        id2name[id_] = name
        name2id[name] = id_

    return render_template("index.html",data=data,width=450*len(data['projects'])+550)

@app.route("/add_proj")
def add_proj():
    name = request.args.get("name")
    if name in name2id:
        return jsonify({"result":"dup"})
    else:
        pid = genRandomId()
        name2id[name] = pid
        id2name[pid] = name
        projectDB.insert(name,pid,"","",time.ctime(),"")
        return jsonify({"result":"ok","pid":pid})

@app.route("/del_project")
def del_project():
    id_ = int(request.args.get("id"))
    if id_ in id2name:
        name = id2name[id_]
        del name2id[name]
        del id2name[id_]
        projectDB.delete(id_)
    return jsonify({"result":"ok"})

@app.route("/<project_id>")
def project(project_id):
    project_id = int(project_id)
    if project_id in id2name:
        data = {
            "project_name":id2name[project_id],
            "project_id":project_id
        }
        return render_template("system.html",data=data)
    else:
        return Response(response="Not found!",status=404,mimetype='text/html')

@app.route("/<project_id>/delete_asset_row",methods=['POST'])
def delete_asset_row(project_id):
    data = json.loads( request.get_data(as_text=True))
    try:
        assetDB.delete(data['asset_id'])
    except Exception as e:
        return {"msg":"错误:"+str(e),'result':'failed'}
    return {"msg":"成功",'result':'ok'}

@app.route("/<project_id>/add_asset_row",methods=['POST'])
def add_asset_row(project_id):
    data = json.loads( request.get_data(as_text=True))
    print(data)
    if not data[0]:
        return {"msg":"请输入编号!",'result':'failed'}
    if not ( data[6] and data[7] and data[8] ):
        return {"msg":"请输入完整性，可用性和机密性值!",'result':'failed'}
    
    try:
        assetDB.insert(project_id,*data)
    except Exception as e:
        return {"msg":"错误:"+str(e),'result':'failed'}
    return {"msg":"成功",'result':'ok'}

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
    assets = dict()
    assets['project_id'] = project_id
    assets['data'] = [
        #[1,2,3,4,5,6,7,8,9,10,11,12,13] for _ in range(80)
        #[1,2,3,4,5,6,7,8]
        ]
    for asset in assetDB.query(project_id):
        assets['data'].append(asset[1:])
    
    return render_template("assets.html",data=assets)


app.run(debug=True)