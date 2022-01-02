import openpyxl
import os
from flask import Flask, render_template, request, jsonify, send_file, Response
from openpyxl import load_workbook

from markdown import markdown
import pdfkit

report_markdown_style = '''<meta charset="UTF-8">
<style type="text/css">
html {
    font-family: sans-serif;
    -ms-text-size-adjust: 100%;
    -webkit-text-size-adjust: 100%;
}

table {
    border-collapse: collapse;
    border-spacing: 0;
}
 
td,th {
    padding: 0;
}
 
table {
    border-collapse: collapse;
    border-spacing: 0;
    empty-cells: show;
    border: 1px solid #cbcbcb;
}
 
table caption {
    color: #000;
    font: italic 85%/1 arial,sans-serif;
    padding: 1em 0;
    text-align: center;
}
 
table td,table th {
    border-left: 1px solid #cbcbcb;
    border-width: 0 0 0 1px;
    font-size: inherit;
    margin: 0;
    overflow: visible;
    padding: .5em 1em;
}
 
table thead {
    background-color: #e0e0e0;
    color: #000;
    text-align: left;
    vertical-align: bottom;
}
 
table td {
    background-color: transparent;
}
h1 {
    font-size: 60px;
    
}
</style>
'''


#<div style="page-break-after: always;"></div>
report_markdown_template = '''
# <center>{0}</center>

## <center>风险评估报告 </center>

### 风险分析结果如下
| 资产 | 威胁 | 脆弱性 | 风险值 | 风险等级 |
| :----: | :----: | :----: | :----: | :----: |
'''

def md2pdf():
    path_wk = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe' #安装位置
    config = pdfkit.configuration(wkhtmltopdf = '/usr/bin/wkhtmltopdf')
    
    input_filename = 'temp.md'
    output_filename = 'temp.pdf'
    
    with open(input_filename, 'r', encoding="utf-8") as f:
        html_text = report_markdown_style + markdown(f.read(), output_format='html5',extensions=['tables'])
    print(html_text)
    pdfkit.from_string(html_text, output_filename, configuration = config)

def format_report(data,title="信息安全"):
    md = str(report_markdown_template)
    md = md.format(title)
    for row in data:
        row_md =  '|' + ' | '.join(row) + '|\n'
        md += row_md
    with open('temp.md','w') as f:
        f.write(md)
    #os.system("pandoc temp.md --pdf-engine=xelatex -o temp.pdf")
    md2pdf()
    return send_file("temp.pdf",as_attachment=False,mimetype="application/pdf")

def read_excel(fn):
    result = []
    wb = load_workbook(fn)
    ws = wb.active
    for row in ws.values:
        result.append( [ v for v in row ] )
    return result[1:]

def read_csv(fn,tag='\t'):
    result = []
    with open(fn,'r') as f:
        for line in f.readlines():
            result.append( line.replace('\n','').split(tag) )
    return result[1:]

secEventProbMat = secLossProbMat = riskMat = [ [i*j for i in range(5)] for j in range(5) ]
def secEventRanks(v):
    if v<=5: return 1
    elif v<=11: return 2
    elif v<=16: return 3
    elif v<=21: return 4
    elif v<=25: return 5

def secLossRanks(v):
    if v<=5: return 1
    elif v<=10: return 2
    elif v<=15: return 3
    elif v<=20: return 4
    elif v<=25: return 5

def riskRanks(v):
    if v<=5: return 1
    elif v<=10: return 2
    elif v<=15: return 3
    elif v<=20: return 4
    elif v<=25: return 5

class Report():
    def __init__(self,aDB,tDB,vDB,project_id) -> None:
        self.assetsDB = aDB
        self.vulDB = vDB
        self.thretsDB = tDB
        self.pid = project_id
    def getReport(self):
        results = []
        for asset in self.assetsDB.query(('project_id',self.pid)):
            assertID = asset[1]
            assetName = asset[3]
            intr = int(asset[7])
            aval = int(asset[8])
            conf = int(asset[9])
            threats = self.thretsDB.query(('asset_id',assertID))
            for threat in threats:
                thrt_id = threat[1]
                thrt_freq = int(threat[4])
                thrt_desc = threat[3]
                vuls = self.vulDB.query(('thrt_id',thrt_id))
                for vul in vuls:
                    vul_id = vul[1]
                    vul_name = vul[2]
                    vul_level = int(vul[4])
                    result = self.caculateRisk( ((intr,conf,aval),vul_level,thrt_freq) )
                    result = [ "{0}:{1}".format(assertID, assetName), "{0}:{1}".format(thrt_id, thrt_desc), "{0}:{1}".format(vul_id,vul_name), str(result[0]), str(result[1]) ]
                    results.append(result)
        return results

    def caculateRisk(self,entry):
        '''
            entry: (i,a,c),(vul_name, vul_level),(thrt_name,thrt_freq)
        '''
        ((i,a,c),vul_level,thrt_freq) = entry
        value = int((c+i+a)/3)
        loss = secEventProbMat[value][vul_level]
        loss_rank = secLossRanks(loss)
        prob = secEventProbMat[thrt_freq][vul_level]
        prob_rank = secEventRanks(prob)
        risk = riskMat[loss_rank][prob_rank]
        risk_rank = riskRanks(risk)
        return risk,risk_rank

def report(data):
    pass

TEST_FLAG = 0

if __name__ == '__main__' and  TEST_FLAG:
    data = read_excel("test.xlsx")
    print(data)
    data = read_csv('test.csv')
    print(data)