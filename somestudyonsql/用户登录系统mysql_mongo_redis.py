from pymysql import *
from hashlib import *
from redis import *


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

    def get_right_pwd(self, user_name):
        res = None
        try:
            cur = self.cur
            param = [user_name]
            select_sql = 'select upwd from py_users where uname = %s'
            cur.execute(select_sql, param)
            pwd = cur.fetchone()
            if pwd:
                res = pwd[0]
        except Exception as e:
            print(e)
        finally:
            return res


class REDIS(object):
    def __init__(self):
        self.client = StrictRedis()
        self.flag = ["redis", "登录成功", ""]

    def login(self, user_name, sha_pwd):
        res = self.client.get(user_name)
        if res:
            if res.decode() != sha_pwd:
                sql_pwd = DataMan(user_name, sha_pwd)
                new_pwd = sql_pwd.get_right_pwd()
                if new_pwd != sha_pwd:
                    self.flag[1] = "登录失败"
                    self.flag[2] = "密码错误"
                else:
                    self.client.set(user_name, new_pwd)
        else:
            sql_sea = DataMan(user_name, sha_pwd)
            self.flag = sql_sea.search()
        return self.flag


class DataMan(object):
    def __init__(self, user_name, sha_pwd):
        self.user_name = user_name
        self.sha_pwd = sha_pwd

    def update(self):
        redis_update = REDIS()
        redis_update.client.set(self.user_name, self.sha_pwd)

    def search(self):
        sql_sea = MYSQL()
        flag = sql_sea.login(self.user_name, self.sha_pwd)
        sql_sea.close()
        return flag

    def get_right_pwd(self):
        sql_pwd = MYSQL()
        new_pwd = sql_pwd.get_right_pwd(self.user_name)
        sql_pwd.close()
        return new_pwd


def get_user():
    usr_name = input("请输入用户名：")
    usr_pwd = input("请输入密码：")

    s1 = sha1()
    s1.update(usr_pwd.encode())
    sha_pwd = s1.hexdigest()
    return usr_name, sha_pwd

if __name__ == '__main__':
    user = get_user()
    # sql_data = MYSQL()
    redis_data = REDIS()
    # sql_flag = sql_data.login(*user)
    redis_flag = redis_data.login(*user)
    print(redis_flag)
    # print(sql_flag)