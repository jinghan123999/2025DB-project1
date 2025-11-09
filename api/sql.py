import os
from typing import Optional
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DBNAME = os.getenv('DB_NAME')
HOST = os.getenv('DB_HOST')
PORT = os.getenv('DB_PORT')

class DB:
    connection_pool = pool.SimpleConnectionPool(
        1, 100,  # 最小和最大連線數
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )

    @staticmethod
    def connect():
        return DB.connection_pool.getconn()

    @staticmethod
    def release(connection):
        DB.connection_pool.putconn(connection)

    @staticmethod
    def execute_input(sql, input):
        if not isinstance(input, (tuple, list)):
            raise TypeError(f"Input should be a tuple or list, got: {type(input).__name__}")
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                connection.commit()
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def execute(sql):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchall(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchone(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchone()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            DB.release(connection)


class Member:
    @staticmethod
    def get_member(account):
        sql = "SELECT account, password, mid, identity, mname FROM member WHERE account = %s"
        return DB.fetchall(sql, (account,))

    @staticmethod
    def get_all_account():
        sql = "SELECT account FROM member"
        return DB.fetchall(sql)

    @staticmethod
    def create_member(input_data):
        sql = 'INSERT INTO member (mname, account, password, identity, email, phone, country) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        DB.execute_input(sql, (
            input_data.get('name'),
            input_data.get('account'),
            input_data.get('password'),
            input_data.get('identity'),
            input_data.get('email'),
            input_data.get('phone'),
            input_data.get('country')
        ))

    @staticmethod
    def delete_product(oid, pid):
        sql = 'DELETE FROM record WHERE oid = %s and pid = %s'
        DB.execute_input(sql, (oid, pid))

    @staticmethod
    def get_order(userid):
        sql = 'SELECT * FROM transaction WHERE mid = %s ORDER BY ordertime DESC'
        return DB.fetchall(sql, (userid,))

    @staticmethod
    def get_role(userid):
        sql = 'SELECT identity, mname FROM member WHERE mid = %s'
        return DB.fetchone(sql, (userid,))


class Cart:
    @staticmethod
    def check(user_id):
        sql = '''SELECT * FROM cart, record 
                 WHERE cart.mid = %s::bigint 
                 AND cart.cno = record.oid::bigint'''
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def get_cart(user_id):
        sql = 'SELECT * FROM cart WHERE mid = %s'
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def add_cart(user_id, time):
        sql = 'INSERT INTO cart (mid, carttime, cno) VALUES (%s, %s, nextval(\'cart_oid_seq\'))'
        DB.execute_input(sql, (user_id, time))

    @staticmethod
    def clear_cart(user_id):
        sql = 'DELETE FROM cart WHERE mid = %s'
        DB.execute_input(sql, (user_id,))


class Product:
    @staticmethod
    def count():
        sql = 'SELECT COUNT(*) FROM product'
        return DB.fetchone(sql)

    @staticmethod
    def get_product(pid):
        sql = 'SELECT * FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_all_product():
        sql = 'SELECT * FROM product'
        return DB.fetchall(sql)

    @staticmethod
    def get_name(pid):
        sql = 'SELECT pname FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO product (pid, pname, price, category, pdesc, mid) VALUES (%s, %s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['pid'], input_data['pname'], input_data['price'], input_data['category'], input_data['pdesc'], input_data['mid']))

    @staticmethod
    def delete_product(pid):
        sql = 'DELETE FROM product WHERE pid = %s'
        DB.execute_input(sql, (pid,))

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE product SET pname = %s, price = %s, category = %s, pdesc = %s WHERE pid = %s'
        DB.execute_input(sql, (input_data['pname'], input_data['price'], input_data['category'], input_data['pdesc'], input_data['pid']))


class Record:
    @staticmethod
    def get_total_money(oid):
        sql = 'SELECT SUM(total) FROM record WHERE oid = %s'
        return DB.fetchone(sql, (oid,))[0]

    @staticmethod
    def check_product(pid, oid):
        sql = 'SELECT * FROM record WHERE pid = %s and oid = %s'
        return DB.fetchone(sql, (pid, oid))

    @staticmethod
    def get_price(pid):
        sql = 'SELECT price FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO record (pid, oid, amount, saleprice, total) VALUES (%s, %s, 1, %s, %s)'
        DB.execute_input(sql, (input_data['pid'], input_data['oid'], input_data['saleprice'], input_data['total']))

    @staticmethod
    def get_record(oid):
        sql = 'SELECT * FROM record WHERE oid = %s'
        return DB.fetchall(sql, (oid,))

    @staticmethod
    def get_amount(oid, pid):
        sql = 'SELECT amount FROM record WHERE oid = %s and pid = %s'
        return DB.fetchone(sql, (oid, pid))[0]

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE record SET amount = %s, total = %s WHERE pid = %s and oid = %s'
        DB.execute_input(sql, (input_data['amount'], input_data['total'], input_data['pid'], input_data['oid']))

    @staticmethod
    def delete_check(pid):
        sql = 'SELECT * FROM record WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_total(oid):
        sql = 'SELECT SUM(total) FROM record WHERE oid = %s'
        return DB.fetchone(sql, (oid,))[0]


class TRANSACTION:
    @staticmethod
    def add_order(input_data):
        sql = 'INSERT INTO transaction (oid, mid, ordertime, price) VALUES (DEFAULT, %s, TO_TIMESTAMP(%s, %s), %s)'
        DB.execute_input(sql, (input_data['mid'], input_data['ordertime'], input_data['format'], input_data['total']))

    @staticmethod
    def get_order():
        sql = '''
            SELECT o.oid, m.mname, o.price, o.ordertime, o.stage
            FROM transaction o
            NATURAL JOIN member m
            ORDER BY o.ordertime DESC
        '''
        return DB.fetchall(sql)

    @staticmethod
    def get_orderdetail():
        sql = '''
        SELECT DISTINCT o.oid, p.pname, r.saleprice, r.amount
        FROM transaction o
        JOIN record r ON o.oid = r.oid -- 確保兩者都是 bigint 類型
        JOIN product p ON r.pid = p.pid
        '''
        return DB.fetchall(sql)

    @staticmethod
    def update_stage(oid, stage):
        """Update the order stage/status for a given order id (oid)."""
        sql = 'UPDATE transaction SET stage = %s WHERE oid = %s'
        DB.execute_input(sql, (stage, oid))

class User_List:    
    @staticmethod
    def get_user():
        sql = '''
            SELECT mid, mname, account, identity FROM member ORDER BY mid ASC
        '''
        return DB.fetchall(sql)
    
    @staticmethod
    def delete_user(mid):
        sql = 'DELETE FROM member WHERE mid = %s'
        DB.execute_input(sql, (mid,))
    
    @staticmethod
    def get_user_by_mid(mid):
        sql = 'SELECT mid, mname, account, identity FROM member WHERE mid = %s'
        return DB.fetchone(sql, (mid,))

    @staticmethod
    def update_user(input_data):
        sql = 'UPDATE member SET mname = %s, account = %s, identity = %s WHERE mid = %s'
        DB.execute_input(sql, (input_data['name'], input_data['account'], input_data['identity'], input_data['mid']))


class Review:
    @staticmethod
    def get_review():
        sql = '''
            SELECT DISTINCT r.rno, p.pname, m.mname, r.rating, r.comment, r."DATE"
            FROM review r
            JOIN product p ON r.pid = p.pid
            JOIN member m ON r.mid = m.mid
            ORDER BY r.rno
        '''
        return DB.fetchall(sql)

    @staticmethod
    def delete_review(rno):
        sql = 'DELETE FROM review WHERE rno = %s'
        DB.execute_input(sql, (rno,))

    @staticmethod
    def get_review_by_pid(pid):
        sql = 'SELECT rno, mid, pid, rating, comment, "DATE" FROM review WHERE pid = %s ORDER BY "DATE" DESC'
        return DB.fetchall(sql, (pid,))


class Browse:
    @staticmethod
    def add_browse(mid, pid, broesetime):
        """Insert a browse record. broesetime should be a string or datetime acceptable by PostgreSQL."""
        sql = 'INSERT INTO browse (mid, pid, broesetime) VALUES (%s, %s, %s)'
        DB.execute_input(sql, (mid, pid, broesetime))

class Analysis:
    @staticmethod
    def month_price(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), SUM(price) FROM transaction WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def month_count(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), COUNT(oid) FROM transaction WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def category_sale():
        sql = 'SELECT SUM(total), category FROM product, record WHERE product.pid = record.pid GROUP BY category'
        return DB.fetchall(sql)

    @staticmethod
    def member_sale():
        sql = 'SELECT SUM(price), member.mid, member.mname FROM transaction, member WHERE transaction.mid = member.mid AND member.identity = %s GROUP BY member.mid, member.mname ORDER BY SUM(price) DESC'
        return DB.fetchall(sql, ('user',))

    @staticmethod
    def member_sale_count():
        sql = 'SELECT COUNT(*), member.mid, member.mname FROM transaction, member WHERE transaction.mid = member.mid AND member.identity = %s GROUP BY member.mid, member.mname ORDER BY COUNT(*) DESC'
        return DB.fetchall(sql, ('user',))
