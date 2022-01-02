from os import name
import time
from sqlite3.dbapi2 import Connection, connect
from flask import Flask, render_template, request, jsonify, send_file, Response
from random import random
from databaseRAS import *
from utils import *
import json
#from utils import AssetsDB

app = Flask(__name__)

upload_dir = './upload/'

connection = Database()
assetDB = Asset(connection)
vulDB = Vulnerability(connection)
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

def js(s):
    return '''<script>
    {0};
    window.opener = null;
    window.open('', '_self');
    window.close();
    </script>'''.format(s)

def genRandomId():
    return str(int(random()*10e6))

@app.route("/<project_id>/upload",methods=['POST'],strict_slashes=False)
def upload(project_id):
    f = request.files['file']
    table_type = request.args.get("tt")
    if f:
        print(f.filename)
        fformat = f.filename.split('.')[-1]
        if not fformat in ['csv','xlsx']:
            return js("alert('不是表格！')")
        fn = upload_dir+'temp.'+fformat
        f.save(fn)
        data = []
        try:                
            if fformat=='xlsx':
                data = read_excel(fn)
            elif fformat=='csv':
                data = read_csv(fn)
            if table_type == 'asset':
                for row in data:
                    assetDB.insert(project_id,*row)
            elif table_type == 'threat':
                for row in data:
                    threatDB.insert(project_id,*row)
            elif table_type == 'vulnerability':
                for row in data:
                    vulDB.insert(project_id,*row)
        except Exception as e:
            return js("alert('错误:" + str(e) + "')")
        return js("alert('文件读取成功.')")
    else:
        return js("alert('不是表格！')")

@app.route("/")
def show_project():
    data = {
        "username":"default",
        "projects":[]
    }
    for project in projectDB.query_all():
        print(project)
        name = project[0]
        id_ = project[1]
        modi = project[4]
        desc = project[2]
        data['projects'] .append({
                    "name":name,
                    "id":id_,
                    "modi":modi,
                    "desc":desc
                })
        id2name[id_] = name
        name2id[name] = id_

    return render_template("index.html",data=data,width=450*len(data['projects'])+550)

@app.route("/add_proj",methods=['POST'])
def add_proj():
    data = json.loads( request.get_data(as_text=True))
    name = data['name']
    desc = data['desc']
    if name in name2id:
        return jsonify({"result":"dup"})
    else:
        pid = genRandomId()
        name2id[name] = pid
        id2name[pid] = name
        projectDB.insert(name,pid,desc,"",time.ctime(),"")
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

@app.route("/<project_id>/delete_threat_row",methods=['POST'])
def delete_threat_row(project_id):
    data = json.loads( request.get_data(as_text=True))
    try:
        threatDB.delete(data['threat_id'])
    except Exception as e:
        return {"msg":"错误:"+str(e),'result':'failed'}
    return {"msg":"成功",'result':'ok'}

@app.route("/<project_id>/add_asset_row",methods=['POST'])
def add_asset_row(project_id):
    data = json.loads( request.get_data(as_text=True))
    print(data)
    if not data[0]:
        return {"msg":"请输入编号!",'result':'failed'}
    if not data[2]:
        return {"msg":"请输入资产名称!",'result':'failed'}
    if not ( data[6] and data[7] and data[8] ):
        return {"msg":"请输入完整性，可用性和机密性!",'result':'failed'}
    
    try:
        assetDB.insert(project_id,*data)
    except Exception as e:
        return {"msg":"错误:"+str(e),'result':'failed'}
    return {"msg":"成功",'result':'ok'}

@app.route("/<project_id>/add_threat_row",methods=['POST'])
def add_threat_row(project_id):
    data = json.loads( request.get_data(as_text=True))
    print(data)
    if not data[0]:
        return {"msg":"请输入编号!",'result':'failed'}
    if not data[1]:
        return {"msg":"请输入资产编号!",'result':'failed'}
    
    try:
        threatDB.insert(project_id,*data)
    except Exception as e:
        return {"msg":"错误:"+str(e),'result':'failed'}
    return {"msg":"成功",'result':'ok'}

@app.route("/<project_id>/add_vul_row",methods=['POST'])
def add_vul_row(project_id):
    data = json.loads( request.get_data(as_text=True))
    print(data)
    if not data[0]:
        return {"msg":"请输入编号!",'result':'failed'}
    if not data[-1]:
        return {"msg":"请输入所属威胁编号!",'result':'failed'}
    try:
        vulDB.insert(project_id,*data)
    except Exception as e:
        return {"msg":"错误:"+str(e),'result':'failed'}
    return {"msg":"成功",'result':'ok'}

@app.route("/<project_id>/page")
def page(project_id):
    resp = ''
    if request.args.get('type') =='1':
        return getAssets(project_id)
    elif request.args.get('type') =='2':
        return getThreats(project_id)  
    elif request.args.get('type') =='3':
        return getVuls(project_id)  
    elif request.args.get('type') =='4':
        getReport(project_id)
        return render_template('report.html',project_id=project_id)
    elif request.args.get('type') =='5':
        resp = "风险统计"
    elif request.args.get('type') =='6':
        resp = "不可接受风险处理"
    return resp

@app.route("/<project_id>/report")
def report_pdf(project_id):
    return getReport(project_id)

def getAssets(project_id):
    #assets = assetsDB.query(pid=project_id)
    assets = dict()
    assets['project_id'] = project_id
    assets['data'] = []
    for asset in assetDB.query(['project_id',project_id]):
        assets['data'].append(asset[1:])
    return render_template("assets.html",data=assets)

def getThreats(project_id):
    #assets = assetsDB.query(pid=project_id)
    threats = dict()
    threats['project_id'] = project_id
    threats['data'] = []
    for threat in threatDB.query(['project_id',project_id]):
        threats['data'].append(threat[1:])
    return render_template("threats.html",data=threats)

def getVuls(project_id):
    #assets = assetsDB.query(pid=project_id)
    vuls = dict()
    vuls['project_id'] = project_id
    vuls['data'] = []
    for vul in vulDB.query(['project_id',project_id]):
        vuls['data'].append(vul[1:])
    return render_template("vulnerabilities.html",data=vuls)

def getReport(project_id):
    R = Report(assetDB,threatDB,vulDB,project_id)
    data = R.getReport()
    print(data)
    #format_report(data)
    #return send_file("test.pdf",as_attachment=False,mimetype="application/pdf")
    return format_report(data)

app.run(debug=True)