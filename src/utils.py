import openpyxl
import os
from jinja2 import Template
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
    font-size:25px;
}

image {
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
    font-size: 30px;
    padding: 1em 0;
    text-align: center;
}
 
table td,table th {
    border: 1px solid #cbcbcb;
    border-width: 0 0 1px 1px;
    font-size: 20px;
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
## <center>风险评估报告 </center>

### 综合风险分析结果如下
| 资产 | 威胁 | 脆弱性 | 风险值 | 风险等级 |
| :----: | :----: | :----: | :----: | :----: |
'''

chart_markdown_template = '''
## <center>风险统计 </center>


系统风险评估共识别出信息安全风险{{risks_len}}个：  

<center>

| 资产 | 威胁  |
| :----: | :----: |
| 极高风险 | {{risks_count[4]}} |
| 高风险 | {{risks_count[3]}} |
| 中风险 | {{risks_count[2]}} |
| 低风险 | {{risks_count[1]}} |
| 极低风险 | {{risks_count[0]}} |  


![pie1](/mnt/c/Users/Derg/Desktop/RAS/src/pie1.png)  

</center>

其中:  

<center>

| 资产 | 威胁  |
| :----: | :----: |
| 不可接受风险 | {{unaccpt}} |
| 可接受风险 | {{accpt}} |  

![pie2](/mnt/c/Users/Derg/Desktop/RAS/src/pie2.png)  

</center>
'''

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

plt.rcParams['figure.figsize'] = (4, 3) # 设置figure_size尺寸
plt.rcParams['image.interpolation'] = 'nearest' # 设置 interpolation style
plt.rcParams['savefig.dpi'] = 120
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'SimHei'

def pie(data,title='风险分布'):
    if title == '是否可接受':
        labels = [ '可接受','不可接受' ]
        fn = 'pie2.png'
    else:
        labels = ['极高风险', '高风险', '中风险', '低风险', '极低风险']
        fn = 'pie1.png'
    X = list(data)
    fig = plt.figure()
    plt.pie(X, labels=labels, autopct='%1.2f%%')  # 画饼图（数据，数据对应的标签，百分数保留两位小数点）
    plt.title(title)
    plt.savefig(fn)

def md2pdf():
    config = pdfkit.configuration(wkhtmltopdf = '/usr/bin/wkhtmltopdf')
    
    input_filename = 'temp.md'
    output_filename = 'temp.pdf'
    
    with open(input_filename, 'r', encoding="utf-8") as f:
        html_text = report_markdown_style + markdown(f.read(), output_format='html5',extensions=['tables'])
    print(html_text)
    pdfkit.from_string(html_text, output_filename, configuration = config)

def format_report(data,title="信息安全"):
    md = str(report_markdown_template)
    #md = md.format(title)
    for row in data:
        row_md =  '|' + ' | '.join(row) + '|\n'
        md += row_md
    with open('temp.md','w') as f:
        f.write(md)
    #os.system("pandoc temp.md --pdf-engine=xelatex -o temp.pdf")
    md2pdf()
    return send_file("temp.pdf",as_attachment=False,mimetype="application/pdf")

def format_chart(data):
    accpt_threshold = 3
    accpt = 0
    unaccpt = 0
    risks_len = len(data)
    risks_count = [ 0 for _ in range(5) ]
    for risk in data:
        risk_rank = int(risk[-1])
        risks_count[risk_rank] += 1
        if risk_rank>accpt_threshold:
            unaccpt += 1
        else:
            accpt += 1
    md = str(chart_markdown_template)
    md =  Template(md).render(risks_len=risks_len,risks_count=risks_count,accpt=accpt,unaccpt=unaccpt)
    with open('temp.md','w') as f:
        f.write(md)
    pie(risks_count)
    pie([accpt,unaccpt],'是否可接受')
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