import math
from flask import Blueprint, request, url_for, redirect, flash, render_template
from flask_login import login_required, current_user
from api.sql import Package, Destination, DB, Cart, Records ,Order_List ,Member,Accommodation
from datetime import datetime

# Define Blueprint
store = Blueprint('travel_packages', __name__, template_folder='../templates')

@store.route('/', methods=['GET', 'POST'])
@login_required
def travel_packages():
    page = int(request.args.get('page', 1))
    start = (page - 1) * 9
    end = page * 9
    keyword = request.args.get('keyword', '').strip()
    flag = 0
    package_data = []

    if request.method == 'GET' and current_user.role == 'manager':
        flash('No permission')
        return redirect(url_for('manager.home'))

    if keyword:
        search_query = f"%{keyword}%"
        package_rows = DB.fetchall(
            'SELECT * FROM package WHERE pname LIKE %s OR description LIKE %s', 
            (search_query, search_query)
        )
    else:
        package_rows = Package.get_all_packages()

    total = len(package_rows)
    count = math.ceil(total / 9)
    final_data = package_rows[start:end]

    for row in final_data:
        package = {
            '套餐編號': row[0],
            '套餐名稱': row[5],
            '開始日期': row[1],
            '結束日期': row[2],
            '價格': row[3],
            '數量': row[4],
            '描述': row[6]
        }
        package_data.append(package)

    if len(package_data) < 9 or (page == count and total % 9 != 0):
        flag = 1

    return render_template(
        'travel_packages.html',
        package_data=package_data,
        user=current_user.name,
        page=page,
        flag=flag,
        count=count,
        keyword=keyword
    )

# 套餐詳細頁面
@store.route('/packages', methods=['GET'])
@login_required
def package_detail():
    packageid = request.args.get('packageid', type=int)
    package_data = Package.get_package(packageid)
    destination_rows = Destination.get_destinations_by_package(packageid)
    accommodation_rows = Accommodation.get_accommodation_by_package(packageid)

    if not package_data:
        flash("找不到此套餐的詳細資料")
        return redirect(url_for('travel_packages.travel_packages'))

    package = {
        '套餐編號': packageid,
        '套餐名稱': package_data[5],
        '開始日期': package_data[1],
        '結束日期': package_data[2],
        '價格': package_data[3],
        '數量': package_data[4],
        '描述': package_data[6],
        '住宿': {
            'accname': accommodation_rows[0][0] if accommodation_rows else None,
            'address': accommodation_rows[0][1] if accommodation_rows else None,
            'days': accommodation_rows[0][2] if accommodation_rows else None,
            'accprice': accommodation_rows[0][3] if accommodation_rows else None,
            'day': 1
        } if accommodation_rows else None,
        'day1_destinations': [],
        'day2_destinations': []
    }

    for row in destination_rows:
        destination = {
            '景點名稱': row[0],
            '位置': row[1],
            '行程價格': row[2],
            '描述': row[3]
        }
        if row[4] == 1:
            package['day1_destinations'].append(destination)
        elif row[4] == 2:
            package['day2_destinations'].append(destination)

    return render_template(
        'destination_detail.html',
        data=package,
        user=current_user.name
    )


# 會員購物車
@store.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    if request.method == 'GET' and current_user.role == 'manager':
        flash('No permission')
        return redirect(url_for('manager.home'))

    if request.method == 'POST':
        if "plid" in request.form:
            cart_data = Cart.get_cart(current_user.id)
            if cart_data is None:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                Cart.add_cart(current_user.id, current_time)
                cart_data = Cart.get_cart(current_user.id)

            tno = int(cart_data[0])
            plid = int(request.form.get('plid'))
            existing_package = Records.check_product(plid, tno)
            package_price = Package.get_package(plid)[3]

            if existing_package is None:
                Records.add_product({
                    'pid': plid,
                    'tno': tno,
                    'saleprice': package_price,
                    'amount': 1,
                    'total': package_price
                })
            else:
                current_amount = Records.get_amount(tno, plid)
                new_amount = current_amount + 1
                new_total = new_amount * package_price
                Records.update_product({
                    'amount': new_amount,
                    'tno': tno,
                    'pid': plid,
                    'total': new_total
                })

        elif "delete" in request.form:
            plid = int(request.form.get('delete'))
            tno = int(Cart.get_cart(current_user.id)[0])
            Records.delete_check(plid, tno)

        elif "buy" in request.form:
            return complete_order()

    package_data = only_cart()
    if not package_data:
        return render_template('empty.html', user=current_user.name)
    else:
        return render_template('cart.html', data=package_data, user=current_user.name)
    
def only_cart():
    """Retrieve all items currently in the user's cart."""
    # Check if the user has a cart
    if not Cart.check(current_user.id):
        return None

    # Get the latest cart for the user
    cart_data = Cart.get_cart(current_user.id)
    if not cart_data:
        return None

    # Get the transaction ID from the cart data
    tno = int(cart_data[0])

    # Retrieve cart items based on transaction ID
    cart_items = Records.get_record(tno)
    return [
        {
            '套餐編號': item[1],
            '套餐名稱': Package.get_name(item[1]),
            '開始日期': Package.get_start_date(item[1]),
            '結束日期': Package.get_end_date(item[1]),
            '價格': item[3],
            '數量': item[2],
            '總價': item[2] * item[3]  # Total for each item (quantity * price)
        }
        for item in cart_items
    ]

def complete_order():
    cart_data = Cart.get_cart(current_user.id)
    tno = cart_data[0] if cart_data else None

    if tno is None:
        flash("Cart not found.")
        return redirect(url_for('travel_packages.cart'))

    total_price = Records.get_total(tno)
    Cart.clear_cart(current_user.id)

    cart_items = Records.get_record(tno)
    if not cart_items:
        flash("No items found in the cart.")
        return redirect(url_for('travel_packages.cart'))

    plid = cart_items[0][1]
    price = cart_items[0][2]

    order_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    time_format = 'yyyy/mm/dd hh24:mi:ss'
    Order_List.add_order({
        'mid': current_user.id,
        'ordertime': order_time,
        'total_price': total_price,
        'format': time_format,
        'plid': plid,
        'price': price,
        'transactionid': tno
    })

    return render_template('complete.html', user=current_user.name)

@store.route('/orderlist')
@login_required
def orderlist():
    user_id = current_user.id

    # 獲取用戶的訂單概要
    data = Order_List.get_user_order(user_id)
    orderlist = []
    for i in data:
        temp = {
            '訂單編號': i[0],
            '訂單總價': i[1],  # 顯示單一訂單的價格
            '訂單時間': i[2]
        }
        orderlist.append(temp)
    
    # 獲取用戶的所有訂單詳細資訊
    orderdetail_row = Order_List.get_user_order_detail(user_id)
    orderdetail = {}
    for j in orderdetail_row:
        order_id = j[0]
        if order_id not in orderdetail:
            orderdetail[order_id] = []
        orderdetail[order_id].append({
            '套餐名稱': j[1],
            '套餐單價': j[2],
            '訂購數量': j[3]
        })

    return render_template('orderlist.html', data=orderlist, detail=orderdetail, user=current_user.name)

