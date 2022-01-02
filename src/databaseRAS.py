import sqlite3

class Database:
    def __init__(self, filename="ras.db"):
        """
        初始化数据库，默认文件名 stsql.db
        filename：文件名
        """
        self.filename = filename
        self.db = sqlite3.connect(self.filename, check_same_thread=False)
        self.c = self.db.cursor()

    def close(self):
        """
        关闭数据库
        """
        self.c.close()
        self.db.close()

    def execute(self, sql, param=None):
        """
        执行数据库的增、删、改
        sql：sql语句
        param：数据，可以是list或tuple，亦可是None
        retutn：成功返回True
        """
        try:
            if param is None:
                self.c.execute(sql)
            else:
                if type(param) is list:
                    self.c.executemany(sql, param)
                else:
                    self.c.execute(sql, param)
            count = self.db.total_changes
            self.db.commit()
        except Exception as e:
            raise
            return False, e
        if count > 0:
            return True
        else:
            return False

    def query(self, sql, param=None):
        """
        查询语句
        sql：sql语句
        param：参数,可为None
        retutn：成功返回True
        """
        if param is None:
            self.c.execute(sql)
        else:
            self.c.execute(sql, param)
        return self.c.fetchall()


class Asset:
    def __init__(self,connection):
        self.count = 0
        self.db = connection
        sql = """CREATE TABLE IF NOT EXISTS asset
               (project_id     INT    NOT NULL,                
               asset_id        INT    PRIMARY KEY   NOT NULL,
               asset_type      INT    NOT NULL, 
               asset_name      CHAR(50),
               mgr            CHAR(50), 
               asset_desc      CHAR(200),
               dept           CHAR(50),
               intr           INT NOT NULL,
               aval           INT NOT NULL,
               conf           INT NOT NULL,
               isHW           BOOLEAN, 
               HW_storage     CHAR(50), 
               isSW           BOOLEAN,
               SW_storage     CHAR(50) )"""
        self.db.execute(sql)
    def insert(self, project_id, asset_id, asset_type, \
                     asset_name, mgr, asset_desc, dept, \
                     intr, aval, conf, isHW, HW_storage, isSW, SW_storage):
        sql = '''INSERT INTO asset(project_id, asset_id, asset_type,
               asset_name, mgr, asset_desc, dept,
               intr, aval, conf, isHW, HW_storage, isSW, SW_storage )
               VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}', '{11}', '{12}', '{13}')''' .format(
               project_id, asset_id, asset_type, asset_name, mgr, asset_desc, dept, intr, aval, conf, isHW, HW_storage, isSW, SW_storage)
        self.db.execute(sql);
    def query(self, parm):
        sql = "SELECT * FROM asset WHERE {0} = {1}".format(*parm)
        data = self.db.query(sql);
        self.count = len(data)
        return data
    def delete(self,asset_id):
        sql = '''DELETE FROM asset WHERE asset_id = '{0}' '''.format(asset_id)
        self.db.execute(sql);

class Vulnerability:
    def __init__(self,connection):
        self.count = 0
        self.db = connection
        sql = """CREATE TABLE IF NOT EXISTS  vulnerability
               (project_id       INT NOT NULL,
               vul_id           INT    PRIMARY KEY   NOT NULL,                
               vul_name         CHAR(50)   NOT NULL,
               vul_desc         CHAR(200), 
               vul_level        INT,
               thrt_id          INT)"""
        self.db.execute(sql);

    def insert(self,project_id, vul_id, vul_name, vul_desc, vul_level, thrt_id):
        sql = '''INSERT INTO vulnerability(project_id, vul_id, vul_name, vul_desc, vul_level, thrt_id)
               VALUES ('{0}', '{1}', '{2}', '{3}',  '{4}',  '{5}')'''.format(project_id, vul_id, vul_name, vul_desc, vul_level, thrt_id)
        self.db.execute(sql);

    def query(self, parm):
        sql = "SELECT * FROM vulnerability WHERE {0} = {1}".format(*parm)
        data = self.db.query(sql);
        self.count = len(data)
        return data

    def delete(self, vul_id):
        sql = '''DELETE FROM vulnerability WHERE vul_id = '{0}' '''.format(vul_id)
        self.db.query(sql)

class Threat:
    def __init__(self,connection):
        self.count = 0
        self.db = connection
        sql = """CREATE TABLE IF NOT EXISTS  threat
               (
                project_id       INT NOT NULL,
                thrt_id          INT        PRIMARY KEY   NOT NULL,                
               asset_id          INT        NOT NULL,
               thrt_desc        CHAR(200), 
               thrt_freq        INT)"""
        self.db.execute(sql);

    def insert(self, project_id,  thrt_id, asset_id, thrt_desc, thrt_freq):
        sql = '''INSERT INTO threat( project_id, thrt_id, asset_id, thrt_desc, thrt_freq)
               VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')'''.format( project_id, thrt_id, asset_id, thrt_desc, thrt_freq)
        self.db.execute(sql);
        print("插入数据成功")

    def query(self, parm):
        sql = "SELECT * FROM threat WHERE {0} = {1}".format(*parm)
        data = self.db.query(sql);
        self.count = len(data)
        return data
    def delete(self, thrt_id):
        sql = '''DELETE FROM threat WHERE thrt_id = '{0}' '''.format(thrt_id)
        self.db.query(sql)

class Project:
    def __init__(self,connection):
        self.count = 0
        self.db = connection
        sql = """CREATE TABLE IF NOT EXISTS  project
               (project_name     CHAR(50)    NOT NULL,                
               project_id       INT         PRIMARY KEY   NOT NULL,
               project_desc     CHAR(200),
               project_range    CHAR(50), 
               create_time      INT,
               mgr              CHAR(50))"""
        self.db.execute(sql);

    def insert(self, project_name, project_id, project_desc, project_range, create_time, mgr):
        sql = '''INSERT INTO PROJECT(project_name, project_id, project_desc, project_range, create_time, mgr)
               VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}' )'''.format( project_name, project_id, project_desc, project_range, create_time, mgr)
        self.db.execute(sql);
        print("插入数据成功")

    def query(self, parm):
        sql = "SELECT * FROM project WHERE {0} = {1}".format(*parm)
        return self.db.query(sql);

    def query_all(self):
        sql = "SELECT * FROM project"
        data = self.db.query(sql);
        self.count = len(data)
        return data

    def delete(self,pid):
        sql = '''DELETE FROM project WHERE project_id = '{0}' '''.format(pid)
        self.db.query(sql)
        sql = '''DELETE FROM asset WHERE project_id = '{0}' '''.format(pid)
        self.db.query(sql)
        sql = '''DELETE FROM threat WHERE project_id = '{0}' '''.format(pid)
        self.db.query(sql)
