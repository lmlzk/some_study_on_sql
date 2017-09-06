from pymysql import *
from pymongo import *
from redis import *


class MYSQL(object):
    def __init__(self):
        self.con = connect(host='localhost', port=3306,
                           database='stu_info', user='root',
                           password='mysql', charset='utf8')
        self.cur = self.con.cursor()
        self.flag = ["mysql", None]

    def close(self):
        self.cur.close()
        self.con.close()

    def check(self, sid):
        try:
            cur = self.cur
            param = [sid]
            sel_sql = "select name from student where id = %s"
            cur.execute(sel_sql, param)
            res = cur.fetchone()
            if res:
                self.flag[1] = res[0]
        except Exception:
            pass
        finally:
            self.close()
            return self.flag


class MONGO(object):
    def __init__(self):
        self.client = MongoClient(host='localhost', port=27017)
        self.db = self.client.stu_info
        self.col = self.db.student
        self.flag = ["mongo", None]

    def check(self, sid):
        try:
            res = self.col.find_one({"id": sid})
            if res:
                self.flag[1] = res["name"]
        except Exception:
            pass
        finally:
            return self.flag


class REDIS(object):
    def __init__(self):
        self.client = StrictRedis()
        self.flag = ["redis", None]

    def check(self, sid):
        try:
            res = self.client.get(sid)
            if res:
                self.flag[1] = res.decode()
        except Exception:
            pass
        finally:
            return self.flag


class CHECK(object):
    def __init__(self):
        self.msg = ["不在库中", "未找到该学生"]

    def check(self, sid):
        redis = REDIS()
        self.msg = redis.check(sid)
        if self.msg[1]:
            return self.msg
        else:
            mongo = MONGO()
            self.msg = mongo.check(sid)
            if self.msg[1]:
                return self.msg
            else:
                mysql = MYSQL()
                self.msg = mysql.check(sid)
                if self.msg[1]:
                    return self.msg
                else:
                    self.msg = ["不在库中", "未找到该学生"]
                    return self.msg


def main():
    stu_id = input("请输入要查询的id号：")
    check_id = CHECK()
    id_msg = check_id.check(stu_id)
    print(id_msg)


if __name__ == '__main__':
    main()
