import os
import subprocess
import time
import pymysql as pymysql


def init_database():
    subprocess.run('mysqld --console')  # 启动数据库
    time.sleep(2)
    conn = pymysql.connect(host="localhost", user='root', password='test1234', database='cost_database')
    cursor = conn.cursor()
    print('初始化数据库')
    # cursor.execute('create database if not exists cost_database')
    cursor.execute('drop table if exists cost_table')
    cursor.execute('create table cost_table'
                   '('
                   'id int not null auto_increment primary key, '
                   'level int,'
                   'main_SN varchar(15),'
                   'father varchar(15),'
                   'have_son int,'
                   'SN varchar(15),'
                   'name varchar(60),'
                   'price float'
                   ')')


def updatePrice(main_SN, father_SN):
    conn = pymysql.connect(host="localhost", user='root', password='test1234', database='cost_database')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'select sum(price) from cost_table where main_SN=\'%s\' and father=\'%s\'' % (main_SN, father_SN))
        result = cursor.fetchall()
        price = result[0][0]
        cursor.execute(
            'update cost_table set price= %f where main_SN=\'%s\' and SN=\'%s\'' % (price, main_SN, father_SN))
        conn.commit()
    except:
        print('Error:updatePrice')
        conn.rollback()
    conn.close()


def updateAllPrice():
    """
    从level 3开始到level 0，将每个有子项的重新统计总额，并更新到数据库
    :return:
    """
    level = [3, 2, 1, 0]
    conn = pymysql.connect(host="localhost", user='root', password='test1234', database='cost_database')
    cursor = conn.cursor()
    for lv in level:
        try:
            cursor.execute('select * from cost_table where level=%d and have_son=1' % lv)
            result_mates = cursor.fetchall()
            print(len(result_mates))
            for mate in result_mates:
                main_sn = mate[2]
                if lv == 0:
                    father_sn = main_sn
                else:
                    father_sn = mate[5]
                cursor.execute(
                    'select sum(price) from cost_table where main_SN=\'%s\' and father=\'%s\'' % (main_sn, father_sn))
                result = cursor.fetchall()
                price = result[0][0]
                cursor.execute(
                    'update cost_table set price= %f where main_SN=\'%s\' and SN=\'%s\'' % (price, main_sn, father_sn))
                # updatePrice(main_sn, father_sn)
            conn.commit()
        except:
            print('Error:updateAllPrice')
            conn.rollback()
    conn.close()


def queryData(main_sn, level: int):
    conn = pymysql.connect(host="localhost", user='root', password='test1234', database='cost_database')
    cursor = conn.cursor()
    cursor.execute('select * from cost_table where main_SN=\'%s\' and level=%d' % (main_sn, level))
    return cursor.fetchall()


def queryByLevel(level: int):
    conn = pymysql.connect(host="localhost", user='root', password='test1234', database='cost_database')
    cursor = conn.cursor()
    cursor.execute('select * from cost_table where level=%d' % level)
    return cursor.fetchall()
