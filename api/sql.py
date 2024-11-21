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
        sql = '''
        INSERT INTO destination (dname, location, dprice, dpid, "desc", day) 
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        DB.execute_input(sql, (
            input_data['dname'], 
            input_data['location'], 
            input_data['dprice'], 
            input_data['dpid'], 
            input_data['desc'],
            input_data['day']  
        ))

    @staticmethod
    def delete_destination(destinationid):
        sql = 'DELETE FROM destination WHERE destinationid = %s'
        DB.execute_input(sql, (destinationid,))

    @staticmethod
    def update_destination(input_data):
        sql = '''
        UPDATE destination 
        SET dname = %s, location = %s, dprice = %s, dpid = %s, "desc" = %s, day = %s 
        WHERE destinationid = %s
        '''
        DB.execute_input(sql, (
            input_data['dname'], 
            input_data['location'], 
            input_data['dprice'], 
            input_data['dpid'], 
            input_data['desc'], 
            input_data['day'], 
            input_data['destinationid']
        ))

    @staticmethod
    def get_destinations_by_package(packageid):
        """
        Retrieves destinations by package ID, ordered by day.
        """
        sql = '''
        SELECT dname, location, dprice, "desc", day 
        FROM destination 
        WHERE dpid = %s 
        ORDER BY day
        '''
        return DB.fetchall(sql, (packageid,))

class Accommodation:
    @staticmethod
    def count():
        sql = 'SELECT COUNT(*) FROM accommodation'
        return DB.fetchone(sql)[0]

    @staticmethod
    def get_accommodation_by_package(packageid):
        sql = 'SELECT accname, address, days, accprice FROM accommodation WHERE accpid = %s'
        return DB.fetchall(sql, (packageid,))

    @staticmethod
    def get_all_accommodations():
        sql = 'SELECT * FROM accommodation'
        return DB.fetchall(sql)

    @staticmethod
    def add_accommodation(input_data):
        sql = '''
        INSERT INTO accommodation (accname, address, days, accprice, accpid) 
        VALUES (%s, %s, %s, %s, %s)
        '''
        DB.execute_input(sql, (
            input_data['accname'],
            input_data['address'],
            input_data['days'],
            input_data['accprice'],
            input_data['accpid']
        ))

    @staticmethod
    def delete_accommodation(accid):
        sql = 'DELETE FROM accommodation WHERE accid = %s'
        DB.execute_input(sql, (accid,))

    @staticmethod
    def update_accommodation(input_data):
        sql = '''
        UPDATE accommodation 
        SET accname = %s, address = %s, days = %s, accprice = %s, accpid = %s 
        WHERE accid = %s
        '''
        DB.execute_input(sql, (
            input_data['accname'],
            input_data['address'],
            input_data['days'],
            input_data['accprice'],
            input_data['accpid'],
            input_data['accid']
        ))

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
        sql = 'SELECT pname FROM package WHERE plid = %s'
        result = DB.fetchone(sql, (plid,))
        return result[0] if result else None

    @staticmethod
    def add_package(input_data):
        sql = '''
        INSERT INTO package (pname, totalprice, startdate, enddate, description, amount, image) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        DB.execute_input(sql, (
            input_data['pname'],
            input_data['totalprice'],
            input_data['startdate'],
            input_data['enddate'],
            input_data['description'],
            input_data['quantity'],
            psycopg2.Binary(input_data['image']) if input_data['image'] else None  # 將圖片轉為 Binary 格式
        ))
    @staticmethod
    def delete_package(plid):
        sql = 'DELETE FROM package WHERE plid = %s'
        DB.execute_input(sql, (plid,))

    @staticmethod
    def update_package(input_data):
        sql = '''
            UPDATE package 
            SET pname = %s, totalprice = %s, startdate = %s, enddate = %s, description = %s, image = %s
            WHERE plid = %s
        '''
        DB.execute_input(sql, (
            input_data['pname'],
            input_data['totalprice'],
            input_data['startdate'],
            input_data['enddate'],
            input_data['description'],
            input_data['image'],
            input_data['plid']
        ))

    @staticmethod
    def get_start_date(plid):
        sql = 'SELECT startdate FROM package WHERE plid = %s'
        result = DB.fetchone(sql, (plid,))
        return result[0] if result else None

    @staticmethod
    def get_end_date(plid):
        sql = 'SELECT enddate FROM package WHERE plid = %s'
        result = DB.fetchone(sql, (plid,))
        return result[0] if result else None
    
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
    
    @staticmethod
    def get_order(user_id):
        """
        Retrieve all orders made by a specific user.
        """
        sql = '''
        SELECT o.oid, o.carttime, o.total_price, o.mid
        FROM order_list o
        WHERE o.mid = %s
        ORDER BY o.carttime DESC
        '''
        return DB.fetchall(sql, (user_id,))
    
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
        
    staticmethod
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
        print(f"DEBUG: Preparing to add product - {input_data}")
        sql = 'INSERT INTO records (plid, transactionid, amount ,price) VALUES (%s, %s, %s, %s)'
        try:
            DB.execute_input(sql, (
                input_data['pid'],
                input_data['tno'],
                input_data.get('amount', 1),
                input_data['saleprice']
            ))
            print(f"DEBUG: Product added successfully - {input_data}")
        except Exception as e:
            print(f"ERROR: Failed to add product - {input_data}, error: {str(e)}")

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
        """
        Add a new order and insert price and total_price.
        """
        sql = '''
        INSERT INTO order_list (oid, mid, carttime, total_price, price, plid, transactionid)
        VALUES (DEFAULT, %s, TO_TIMESTAMP(%s, %s), %s, %s, %s, %s)
        '''
        DB.execute_input(sql, (
            input_data['mid'],
            input_data['ordertime'],
            input_data['format'],
            input_data['total_price'],  
            input_data['price'],  
            input_data['plid'],
            input_data['transactionid']
        ))

    @staticmethod
    def calculate_total_price(tno):
        """
        Calculate the total price for a given transaction based on records table's price and amount.
        """
        sql = '''
        SELECT SUM(r.price * r.amount) AS total_price
        FROM records r
        WHERE r.transactionid = %s
        '''
        result = DB.fetchone(sql, (tno,))
        return result[0] if result else 0

    @staticmethod
    def get_order():
        """
        Retrieves all orders for the order management page in the admin backend.
        """
        sql = '''
        SELECT o.oid AS 訂單編號, m.name AS 訂購人, o.total_price AS 訂單總價, o.carttime AS 訂單時間
        FROM order_list o
        JOIN member m ON o.mid = m.mid
        ORDER BY o.carttime DESC
        '''
        return DB.fetchall(sql)

    @staticmethod
    def get_user_order(user_id):
        """
        Retrieve orders for a specific user.
        """
        sql = '''
        SELECT oid, total_price, carttime
        FROM order_list
        WHERE mid = %s
        ORDER BY carttime DESC;
        '''
        return DB.fetchall(sql, (user_id,))

    @staticmethod
    def get_order_detail(order_id):
        """
        Retrieve detailed information of each item in a specific order.
        """
        sql = '''
        SELECT o.oid AS 訂單編號,
               p.pname AS 套餐名稱,
               r.price AS 套餐單價,
               r.amount AS 訂購數量
        FROM order_list o
        JOIN records r ON o.transactionid = r.transactionid
        JOIN package p ON r.plid = p.plid
        WHERE o.oid = %s
        ORDER BY p.pname;
        '''
        return DB.fetchall(sql, (order_id,))

    @staticmethod
    def get_user_order_detail(user_id):
        """
        取得特定用戶的所有訂單詳細資訊，包括訂單中的每個套餐項目。
        """
        sql = '''
        SELECT o.oid AS 訂單編號,
               p.pname AS 套餐名稱,
               r.price AS 套餐單價,
               r.amount AS 訂購數量
        FROM order_list o
        JOIN records r ON o.transactionid = r.transactionid
        JOIN package p ON r.plid = p.plid
        WHERE o.mid = %s
        ORDER BY o.oid, p.pname;
        '''
        return DB.fetchall(sql, (user_id,))
    
    @staticmethod
    def get_admin_order():
        # 後台專用的訂單查詢
        sql = '''
        SELECT o.oid AS 訂單編號, m.name AS 訂購人, o.total_price AS 訂單總價, o.carttime AS 訂單時間
        FROM order_list o
        JOIN member m ON o.mid = m.mid
        ORDER BY o.carttime DESC
        '''
        return DB.fetchall(sql)

    @staticmethod
    def get_all_order_details():
        # 後台專用的訂單詳細資訊查詢
        sql = '''
        SELECT o.oid AS 訂單編號,
               p.pname AS 套餐名稱,
               r.price AS 單價,
               r.amount AS 數量
        FROM order_list o
        JOIN records r ON o.transactionid = r.transactionid
        JOIN package p ON r.plid = p.plid
        ORDER BY o.oid, p.pname;
        '''
        return DB.fetchall(sql)
    
class Analysis:
    @staticmethod
    def month_price(month):
        """
        查詢每月的總營收，以 `carttime` 欄位的月份作為條件
        """
        sql = '''
        SELECT EXTRACT(MONTH FROM carttime) AS month, COALESCE(SUM(total_price), 0) AS revenue
        FROM order_list
        WHERE EXTRACT(MONTH FROM carttime) = %s
        GROUP BY month
        '''
        return DB.fetchall(sql, (month,))

    @staticmethod
    def month_count(month):
        """
        查詢每月的訂單數量，以 `carttime` 欄位的月份作為條件
        """
        sql = '''
        SELECT EXTRACT(MONTH FROM carttime) AS month, COUNT(oid) AS order_count
        FROM order_list
        WHERE EXTRACT(MONTH FROM carttime) = %s
        GROUP BY month
        '''
        return DB.fetchall(sql, (month,))

    @staticmethod
    def category_sale():
        """
        查詢不同套餐的銷售數量，按照每個套餐的 `pname` 分組
        """
        sql = '''
        SELECT SUM(r.amount) AS sales, p.pname AS package_name
        FROM records r
        JOIN package p ON r.plid = p.plid
        GROUP BY p.pname
        ORDER BY sales DESC
        '''
        return DB.fetchall(sql)

    @staticmethod
    def member_sale():
        """
        查詢每位會員的總消費金額，以會員的 `mid` 和 `name` 分組並排序
        """
        sql = '''
        SELECT COALESCE(SUM(o.total_price), 0) AS total_spent, m.mid, m.name
        FROM order_list o
        JOIN member m ON o.mid = m.mid
        GROUP BY m.mid, m.name
        ORDER BY total_spent DESC
        '''
        return DB.fetchall(sql)

    @staticmethod
    def member_sale_count():
        """
        查詢每位會員的訂單數量，以會員的 `mid` 和 `name` 分組並排序
        """
        sql = '''
        SELECT COUNT(o.oid) AS order_count, m.mid, m.name
        FROM order_list o
        JOIN member m ON o.mid = m.mid
        GROUP BY m.mid, m.name
        ORDER BY order_count DESC
        '''
        return DB.fetchall(sql)