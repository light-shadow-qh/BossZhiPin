import pymysql
from settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DB, KEYWORD
from pypinyin import lazy_pinyin


class Save2Mysql(object):
    def __init__(self):
        self.host = MYSQL_HOST
        self.user = MYSQL_USER
        self.password = MYSQL_PASSWORD
        self.port = MYSQL_PORT
        self.db = MYSQL_DB
        self.table = ''.join(lazy_pinyin(KEYWORD))
        self.connect()

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                database=self.db,
                # charset='utf8'
            )
        except pymysql.MySQLError as e:
            print(e.args)
        else:
            print('链接成功！')
            self.cursor = self.conn.cursor()

    def add_table(self):
        sql = """CREATE TABLE IF NOT EXISTS %s(
        id INT(8) NOT NULL PRIMARY KEY AUTO_INCREMENT,
        job_id INT(8) NOT NULL,
        city_id INT(20) NOT NULL,
        job_name VARCHAR(100),
        job_area VARCHAR(255),
        job_salary VARCHAR(100),
        job_exe VARCHAR(255),
        job_edu VARCHAR(10),
        job_tags VARCHAR(100),
        job_welfare VARCHAR(255),
        contact VARCHAR(100),
        position VARCHAR(100),
        company_name VARCHAR(100),
        company_industry VARCHAR(100),
        company_natural VARCHAR(100),
        company_size VARCHAR(100));
        """ % self.table
        self.cursor.execute(sql)

    def insert(self, data):
        keys = ', '.join(data.keys())
        val_num = ', '.join(['%s'] * len(data.values()))
        sql = """
        INSERT INTO %s(
        %s
        ) VALUES(%s);
        """ % (self.table, keys, val_num)
        try:
            self.cursor.execute(sql, tuple(data.values()))
        except pymysql.MySQLError as e:
            print(e.args)
            self.conn.rollback()
            print("插入失败")
        else:
            print('插入成功')
            self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    pass

