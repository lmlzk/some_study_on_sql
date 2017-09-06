from pymysql import *
from hashlib import *
from pymongo import *
from redis import *

def register():
    try:
        # 1. 获取连接对象
        conn = mysql_conn()
        # 2. 获取ｃｕｒｓｏｒ对象
        cur = conn.cursor()
        # 3. 查询的ｓｑｌ语句
        parmas = [uname]
        select_sql = 'select upwd from py_users where uname = %s'
        # 4.执行ｓｑｌ
        cur.execute(select_sql, parmas)
        # 结果是元祖类型
        res = cur.fetchone()
        # 5. 判断查询的结果
        if res is not None:
            # 先完成错误的逻辑判断
            print('用户名已经存在，注册失败')
            return
        # 6. 如果用户名不存在　应该完成插入的操作，如果存在就提示注册失败，已经存在该用户名
        # 用户名一定不存在　需要完成插入数据库的
        # 密码不能存明文
        insert_params = [uname, sha_pwd]
        insert_sql = 'insert into py_users (uname,upwd) values (%s,%s)'
        rescount = cur.execute(insert_sql, insert_params)
        if rescount == 0:
            # conn.rollback()
            print('注册失败')
        else:
            print('注册成功')
            # 需要提交事务
            conn.commit()
    except Exception as e:
        print(e)
    finally:
        close(conn)
# hbase
# kafka
def login():
    try:
        # 1. 获取连接对象
        conn = mysql_conn()
        # 2. 获取ｃｕｒｓｏｒ对象
        cur = conn.cursor()
        # 3. 查询的ｓｑｌ语句
        parmas = [uname]
        select_sql = 'select upwd from py_users where uname = %s'
        # 4.执行ｓｑｌ
        cur.execute(select_sql, parmas)
        # 结果是元祖类型
        res = cur.fetchone()
        # 5. 判断查询的结果
        if res is None:
            # 先完成错误的逻辑判断
            print('用户名错误，登陆失败')
            return
        # 6. 如果用户名存在　应该完成插入的操作，如果存在就提示注册失败，已经存在该用户名
        # 用户名一定存在　需要判断密码是否正确
        # 比较两个密文之间是否相等
        pwd = res[0]
        if pwd == sha_pwd:
            # 密码正确
            print('登陆成功，数据来源与ｍｙｓｑｌ')
            # 待完成　将数据写入ｍｏｎｇｏ
            # col.insert_one({'uname':uname,'upwd':sha_pwd})
            # redis存储数据
            r_client.set(uname,sha_pwd)
        else:
            print('密码错误，登陆失败')
    except Exception as e:
        print(e)
    finally:
        close(conn)


def mysql_conn():
    '''返回连接对象'''
    # host = None, user = None, password = "",
    # database = None, port = 0, unix_socket = None,
    # charset = ''
    return  connect(host='localhost',user='root',password='mysql',database='python_info',port=3306,charset='utf8')


def close(conn):
    '''关闭连接'''
    conn.cursor().close()
    conn.close()

def mongo_login():
    # 在集合中根据用户名查找密码 {uname:name,upwd:pwd}
    res = col.find_one({'uname': uname})
    print(res)
    # 判断结果是否为　Ｎｏｎｅ
    if res is None:
        login()
    else:
        # 判断是否正确　res 是字典类型
        if res['upwd'] == sha_pwd:
            print('登陆成功，数据来源与ｍｏｎｇｏ')
        else:
            print('登陆失败，密码错误，数据来自ｍｏｎｇｏ')

if __name__ == '__main__':
    uname = input('请输入用户名：')
    upwd = input('请输入密码：')
    print(upwd)
    # 对ｕｐｗｄ进行ｓｈａ１加密
    s1 = sha1()
    s1.update(upwd.encode())
    sha_pwd = s1.hexdigest()
    print(sha_pwd)
    # register
    #register()

    # login
    #login()
    # 先到ｍｏｎｇｏ中获取数据判断是否能够完成登陆的操作
    client = MongoClient(host='localhost',port=27017)
    db = client.python
    col = db.py_users

    # 先到ｒｅｄｉｓ中根据用户名获取密码　uname 作为键　ｓｈａ_pwd作为值
    r_client = StrictRedis()
    res = r_client.get(uname)
    # print(res)
    if res is None:
        print('空')
        login()
    else:
        print('非空')
        # python2中不需要转码和解码
        if res.decode() == sha_pwd:
            print('登陆成功，数据来源ｒｅｄｉｓ')
        else:
            print('密码错误，登陆失败，数据来自于ｒｅｄｉｓ')
