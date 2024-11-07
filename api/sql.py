from typing import Optional
import psycopg2
from psycopg2 import pool
from flask_login import UserMixin

class DB:
    connection_pool = pool.SimpleConnectionPool(
        1, 100,  
        user='project_19',
        password='t958bp',
        host='140.117.68.66',
        port='5432',
        dbname='project_19'
    )

    @staticmethod
    def connect():
        return DB.connection_pool.getconn()

    @staticmethod
    def release(connection):
        DB.connection_pool.putconn(connection)

    @staticmethod
    def execute_input(sql, input_data):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input_data)
                connection.commit()
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchall(sql, input_data=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input_data)
                return cursor.fetchall()
        finally:
            DB.release(connection)

    @staticmethod
    def fetchone(sql, input_data=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input_data)
                return cursor.fetchone()
        finally:
            DB.release(connection)

class Destination:
    @staticmethod
    def count():
        sql = 'SELECT COUNT(*) FROM destination'
        return DB.fetchone(sql)[0]

    @staticmethod
    def get_destination(destinationid):
        sql = 'SELECT * FROM destination WHERE destinationid = %s'
        return DB.fetchone(sql, (destinationid,))

    @staticmethod
    def get_all_destinations():
        sql = 'SELECT * FROM destination'
        return DB.fetchall(sql)

    @staticmethod
    def add_destination(input_data):
        sql = 'INSERT INTO destination (dname, location, dprice, dpid, desc) VALUES (%s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['dname'], input_data['location'], input_data['dprice'], input_data['dpid'], input_data['desc']))

    @staticmethod
    def delete_destination(destinationid):
        sql = 'DELETE FROM destination WHERE destinationid = %s'
        DB.execute_input(sql, (destinationid,))

    @staticmethod
    def update_destination(input_data):
        sql = 'UPDATE destination SET dname = %s, location = %s, dprice = %s, dpid = %s, desc = %s WHERE destinationid = %s'
        DB.execute_input(sql, (input_data['dname'], input_data['location'], input_data['dprice'], input_data['dpid'], input_data['desc'], input_data['destinationid']))

class Package:
    @staticmethod
    def count():
        sql = 'SELECT COUNT(*) FROM package'
        return DB.fetchone(sql)[0]

    @staticmethod
    def get_package(plid):
        sql = 'SELECT * FROM package WHERE plid = %s'
        return DB.fetchone(sql, (plid,))

    @staticmethod
    def get_all_packages():
        sql = 'SELECT * FROM package'
        return DB.fetchall(sql)
    
    @staticmethod
    def get_name(plid):
        """根據套餐編號獲取套餐名稱。"""
        sql = 'SELECT pname FROM package WHERE plid = %s'
        result = DB.fetchone(sql, (plid,))
        return result[0] if result else None

    @staticmethod
    def add_package(input_data):
        sql = 'INSERT INTO package (pname, price, startdate, enddate, description) VALUES (%s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['pname'], input_data['price'], input_data['startdate'], input_data['enddate'], input_data['description']))

    @staticmethod
    def delete_package(plid):
        sql = 'DELETE FROM package WHERE plid = %s'
        DB.execute_input(sql, (plid,))

    @staticmethod
    def update_package(input_data):
        sql = 'UPDATE package SET pname = %s, price = %s, startdate = %s, enddate = %s, description = %s WHERE plid = %s'
        DB.execute_input(sql, (input_data['pname'], input_data['price'], input_data['startdate'], input_data['enddate'], input_data['description'], input_data['plid']))
    
    @staticmethod
    def get_start_date(plid):
        """根據套餐編號取得開始日期。"""
        sql = 'SELECT startdate FROM package WHERE plid = %s'
        result = DB.fetchone(sql, (plid,))
        return result[0] if result else None
    
    @staticmethod
    def get_end_date(plid):
        """根據套餐編號取得結束日期。"""
        sql = 'SELECT enddate FROM package WHERE plid = %s'
        result = DB.fetchone(sql, (plid,))
        return result[0] if result else None
    
class Member(UserMixin):
    def __init__(self, mid, name, role):
        self.id = mid
        self.name = name
        self.role = role

    @staticmethod
    def get_member(account):
        sql = "SELECT account, password, mid, identity, name FROM member WHERE account = %s"
        return DB.fetchone(sql, (account,))

    @staticmethod
    def get_member_by_id(user_id):
        sql = "SELECT mid, name, identity FROM member WHERE mid = %s"
        result = DB.fetchone(sql, (user_id,))
        if result:
            return Member(mid=result[0], name=result[1], role=result[2])
        return None

    @staticmethod
    def get_all_account():
        sql = "SELECT account FROM member"
        return DB.fetchall(sql)

    @staticmethod
    def create_member(input_data):
        sql = 'INSERT INTO member (name, account, password, identity) VALUES (%s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['name'], input_data['account'], input_data['password'], input_data['identity']))

    @staticmethod
    def get_role(user_id):
        sql = 'SELECT identity, name FROM member WHERE mid = %s'
        return DB.fetchone(sql, (user_id,))
    
class Cart:
    @staticmethod
    def check(user_id):
        """Check if a cart exists for the given user."""
        sql = 'SELECT COUNT(*) FROM cart WHERE mid = %s'
        result = DB.fetchone(sql, (user_id,))
        return result and result[0] > 0

    @staticmethod
    def get_cart(user_id):
        """Retrieve the latest cart for a user."""
        sql = 'SELECT tno, mid, carttime FROM cart WHERE mid = %s ORDER BY carttime DESC LIMIT 1'
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def add_cart(user_id, cart_time):
        """Create a new cart entry for the user."""
        sql = 'INSERT INTO cart (mid, carttime, tno) VALUES (%s, %s, nextval(\'cart_tno_seq\'))'
        DB.execute_input(sql, (user_id, cart_time))

    @staticmethod
    def clear_cart(user_id):
        """Delete all carts associated with a user."""
        sql = 'DELETE FROM cart WHERE mid = %s'
        DB.execute_input(sql, (user_id,))

    @staticmethod
    def get_tno_by_user_id(user_id):
        """Get the latest transaction number (tno) for a user's cart."""
        sql = 'SELECT tno FROM cart WHERE mid = %s ORDER BY carttime DESC LIMIT 1'
        result = DB.fetchone(sql, (user_id,))
        return result[0] if result else None

class Records:
    @staticmethod
    def check_product(plid, tno):
        """Check if a package is already in the transaction records."""
        sql = 'SELECT * FROM records WHERE plid = %s AND transactionid = %s'
        return DB.fetchone(sql, (plid, tno))

    @staticmethod
    def get_amount(tno, plid):
        """Get the amount of a specific package in a transaction."""
        sql = 'SELECT amount FROM records WHERE transactionid = %s AND plid = %s'
        result = DB.fetchone(sql, (tno, plid))
        return result[0] if result else 0

    @staticmethod
    def add_product(input_data):
        """Add a new product entry to the records."""
        sql = 'INSERT INTO records (plid, transactionid, amount, price) VALUES (%s, %s, %s, %s)'
        DB.execute_input(sql, (
            input_data['pid'],
            input_data['tno'],
            input_data.get('amount', 1),
            input_data['saleprice']
        ))

    @staticmethod
    def update_product(input_data):
        """Update the quantity for a specific product in the records."""
        sql = 'UPDATE records SET amount = %s WHERE plid = %s AND transactionid = %s'
        DB.execute_input(sql, (
            input_data['amount'],
            input_data['pid'],
            input_data['tno']
        ))

    @staticmethod
    def delete_check(plid, tno):
        """Remove a specific product from the records."""
        sql = 'DELETE FROM records WHERE plid = %s AND transactionid = %s'
        DB.execute_input(sql, (plid, tno))

    @staticmethod
    def get_record(transaction_id):
        """Retrieve records based on transaction ID."""
        sql = '''
        SELECT
            transactionid,
            plid,
            amount,
            price,
            amount * price AS total
        FROM
            records
        WHERE
            transactionid = %s
        '''
        return DB.fetchall(sql, (transaction_id,))

    @staticmethod
    def get_total(transaction_id):
        """Calculate the total amount for a transaction."""
        sql = 'SELECT SUM(amount * price) FROM records WHERE transactionid = %s'
        result = DB.fetchone(sql, (transaction_id,))
        return result[0] if result else 0
    
class Order_List:
    @staticmethod
    def add_order(input_data):
        sql = 'INSERT INTO order_list (oid, mid, carttime, price, plid) VALUES (DEFAULT, %s, TO_TIMESTAMP(%s, %s), %s, %s)'
        DB.execute_input(sql, (input_data['mid'], input_data['ordertime'], input_data['format'], input_data['total'], input_data['plid']))

    @staticmethod
    def get_order():
        sql = '''
        SELECT o.oid, m.name, o.price, o.carttime
        FROM order_list o
        NATURAL JOIN member m
        ORDER BY o.carttime DESC
        '''
        return DB.fetchall(sql)

    @staticmethod
    def get_orderdetail():
        sql = '''
        SELECT o.oid, d.dname, r.price, r.amount
        FROM order_list o
        JOIN records r ON o.plid = r.plid
        JOIN destination d ON r.plid = d.destinationid
        '''
        return DB.fetchall(sql)


class Analysis:
    @staticmethod
    def month_price(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), SUM(price) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def month_count(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), COUNT(oid) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def member_sale():
        sql = 'SELECT SUM(price), member.mid, member.name FROM order_list JOIN member ON order_list.mid = member.mid WHERE member.identity = %s GROUP BY member.mid, member.name ORDER BY SUM(price) DESC'
        return DB.fetchall(sql, ('user',))

    @staticmethod
    def member_sale_count():
        sql = 'SELECT COUNT(*), member.mid, member.name FROM order_list JOIN member ON order_list.mid = member.mid WHERE member.identity = %s GROUP BY member.mid, member.name ORDER BY COUNT(*) DESC'
        return DB.fetchall(sql, ('user',))
