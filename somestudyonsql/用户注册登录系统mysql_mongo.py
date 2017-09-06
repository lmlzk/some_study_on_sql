from pymysql import *
from hashlib import *
from pymongo import *


class MYSQL(object):
    def __init__(self):
        self.con = connect(host='localhost', port=3306,
                           database='python_info', user='root',
                           password='mysql', charset='utf8')
        self.cur = self.con.cursor()
        self.flag = ["mysql", "登录成功", ""]

    def close(self):
        self.cur.close()
        self.con.close()

    def login(self, user_name, sha_pwd):
        try:
            cur = self.cur
            param = [user_name]
            select_sql = 'select upwd from py_users where uname = %s'
            cur.execute(select_sql, param)
            res = cur.fetchone()
            # print(res)
            if res:
                if res[0] != sha_pwd:
                    self.flag[1] = "登录失败"
                    self.flag[2] = "密码错误"
                data_man = DataMan(user_name, sha_pwd)
                data_man.update()
            else:
                self.flag[1] = "登录失败"
                self.flag[2] = "用户不存在"
            # return self.flag
        except Exception as e:
            print(e)
            self.flag[1] = "登录失败"
            self.flag[2] = e
        finally:
            return self.flag


class PYMONGO(object):
    def __init__(self):
        self.client = MongoClient(host='localhost',
                                  port=27017)
        self.db = self.client.python_info
        self.col = self.db.py_users
        self.flag = ["mongo", "登录成功", ""]

    def login(self, user_name, sha_pwd):
        res = self.col.find_one({"name": user_name})
        if res:
            if res["upwd"] != sha_pwd:
                self.flag[1] = "登录失败"
                self.flag[2] = "密码错误"
        else:
            sql = MYSQL()
            self.flag = sql.login(user_name, sha_pwd)
            sql.close()
        return self.flag


class DataMan(object):
    def __init__(self, user_name, sha_pwd):
        self.user_name = user_name
        self.sha_pwd = sha_pwd

    def update(self):
        mongo_update = PYMONGO()
        mongo_update.col.insert_one({"name": self.user_name,
                                     "upwd": self.sha_pwd})


def get_user():
    usr_name = input("请输入用户名：")
    usr_pwd = input("请输入密码：")

    s1 = sha1()
    s1.update(usr_pwd.encode())
    sha_pwd = s1.hexdigest()
    return usr_name, sha_pwd

if __name__ == '__main__':
    user = get_user()
    sql_data = MYSQL()
    # mongo_data = PYMONGO()
    sql_flag = sql_data.login(*user)
    # mongo_flag = mongo_data.login(*user)
    # print(mongo_flag)
    print(sql_flag)

