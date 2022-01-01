import openpyxl
from openpyxl import load_workbook


def read_excel(fn):
    result = []
    wb = load_workbook(fn)
    ws = wb.active
    for row in ws.values:
        result.append( [ v for v in row ] )
    return result

def read_csv(fn,tag='\t'):
    result = []
    with open(fn,'r') as f:
        for line in f.readlines():
            result.append( line.replace('\n','').split(tag) )
    return result

TEST_FLAG = 0

if __name__ == '__main__' and  TEST_FLAG:
    data = read_excel("test.xlsx")
    print(data)
    data = read_csv('test.csv')
    print(data)