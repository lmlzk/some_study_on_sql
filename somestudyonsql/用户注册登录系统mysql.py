from pymysql import *
from hashlib import *


class MYSQL(object):
    def __init__(self):
        self.__con = connect(host='localhost', port=3306,
                             database='python_info', user='root',
                             password='mysql', charset='utf8')
        self.__cur = self.__con.cursor()

    def get_conn(self):
        return self.__con

    def get_cur(self):
        return self.__cur

    def close(self):
        self.__cur.close()
        self.__con.close()

    def login(self, usr_name, sha_pwd):
        try:
            cur = self.get_cur()
            param = [usr_name]
            select_sql = 'select upwd from py_users where uname = %s'
            cur.execute(select_sql, param)
            res = cur.fetchone()
            if res is None:
                # print('用户名错误，登陆失败')
                return -1
            pwd = res[0]
            if pwd == sha_pwd:
                # 密码正确
                # print('登陆成功')
                return 2
            else:
                # print('密码错误，登陆失败')
                return 1
        except Exception as e:
            print(e)
            return 0
        # finally:
        #     self.close_cursor()

    def regist(self, usr_name, sha_pwd):
        try:
            # conn = self.get_conn()
            cur = self.get_cur()
            params = [usr_name]
            select_sql = 'select upwd from py_users where uname = %s'
            cur.execute(select_sql, params)
            res = cur.fetchone()
            if res is not None:
                # print('用户名已经存在，注册失败')
                return
            insert_params = [usr_name, sha_pwd]
            insert_sql = 'insert into py_users (uname,upwd) values (%s,%s)'
            rescount = cur.execute(insert_sql, insert_params)
            if rescount == 0:
                # conn.rollback()
                print('注册失败')
                return -1
            else:
                print('注册成功')
                # 需要提交事务
                self.get_conn().commit()
                return 1
        except Exception as e:
            print(e)
            return 0
        # finally:
        #     self.close_cursor()


def get_user():
    usr_name = input("请输入用户名：")
    usr_pwd = input("请输入密码：")

    s1 = sha1()
    s1.update(usr_pwd.encode())
    sha_pwd = s1.hexdigest()
    return usr_name, sha_pwd


def print_msg(login_flag):
    if login_flag == 2:
        print("用户登录成功！")
    elif login_flag == 1:
        print("用户密码错误,登录失败！")
    elif login_flag == 0:
        print("出现异常！")
    else:
        print("用户名不存在!")
        while True:
            rgst_flag = input("是否注册新用户(y/yes or n/no):")
            if rgst_flag.lower() in ["yes", "y"]:
                user_sql_data.regist(*user)
                break
            elif rgst_flag.lower() in ["no", "n"]:
                print("Bye ~~")
                break
            else:
                print("请按提示输入！")

if __name__ == '__main__':
    user = get_user()
    user_sql_data = MYSQL()
    login_flag = user_sql_data.login(*user)
    print_msg(login_flag)

    user_sql_data.close()








