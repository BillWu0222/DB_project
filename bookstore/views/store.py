import math
from flask import Blueprint, request, url_for, redirect, flash, render_template
from flask_login import login_required, current_user
from api.sql import Package, Destination, DB, Cart, Records ,Order_List ,Member,Accommodation
from datetime import datetime
import base64

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
        # base64 編碼圖片欄位
        image_data = base64.b64encode(row[7]).decode('utf-8') if row[7] else None
        package = {
            '套餐編號': row[0],
            '套餐名稱': row[5],
            '開始日期': row[1],
            '結束日期': row[2],
            '價格': row[3],
            '數量': row[4],
            '描述': row[6],
            '圖片': image_data  # 使用 base64 編碼後的圖片
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

    # 如果套餐包含圖片，則轉換圖片為 base64 格式
    image_data = package_data[7]  
    image_base64 = base64.b64encode(image_data).decode('utf-8') if image_data else None

    # 套餐詳細資訊
    package = {
        '套餐編號': packageid,
        '套餐名稱': package_data[5],
        '開始日期': package_data[1],
        '結束日期': package_data[2],
        '價格': package_data[3],
        '數量': package_data[4],
        '描述': package_data[6],
        '圖片': image_base64,  
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

    # 行程資訊
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
   
    if not Cart.check(current_user.id):
        return None

    cart_data = Cart.get_cart(current_user.id)
    if not cart_data:
        return None

    tno = int(cart_data[0])
    cart_items = Records.get_record(tno)
    return [
        {
            '套餐編號': item[1],
            '套餐名稱': Package.get_name(item[1]),
            '開始日期': Package.get_start_date(item[1]),
            '結束日期': Package.get_end_date(item[1]),
            '價格': item[3],
            '數量': item[2],
            '總價': item[2] * item[3]  
        }
        for item in cart_items
    ]

def complete_order():
    try:
        # Step 1: Retrieve cart data
        cart_data = Cart.get_cart(current_user.id)
        print(f"DEBUG: Retrieved cart data - user_id: {current_user.id}, cart_data: {cart_data}")
        tno = cart_data[0] if cart_data else None

        if tno is None:
            flash("購物車不存在或已清空，請重新選擇商品。")
            print("ERROR: No cart found or cart is empty.")
            return redirect(url_for('travel_packages.cart'))

        # Step 2: Calculate total price
        total_price = Records.get_total(tno)
        print(f"DEBUG: Calculated total price - transaction_id: {tno}, total_price: {total_price}")
        if total_price is None or total_price == 0:
            flash("無法計算訂單總價，請重新嘗試。")
            print("ERROR: Failed to calculate total price or total is 0.")
            return redirect(url_for('travel_packages.cart'))

        # Step 3: Retrieve cart items
        cart_items = Records.get_record(tno)
        print(f"DEBUG: Retrieved cart items - transaction_id: {tno}, cart_items: {cart_items}")
        if not cart_items:
            flash("購物車中沒有商品，請先添加商品。")
            print("ERROR: No items found in cart.")
            return redirect(url_for('travel_packages.cart'))

        # Step 4: Add order to database
        plid = cart_items[0][1]  # 第一個商品的 plid
        price = cart_items[0][3]  # 第一個商品的價格

        order_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        time_format = 'yyyy/mm/dd hh24:mi:ss'
        print(f"DEBUG: Preparing to add order - user_id: {current_user.id}, order_time: {order_time}, total_price: {total_price}")

        try:
            Order_List.add_order({
                'mid': current_user.id,
                'ordertime': order_time,
                'total_price': total_price,
                'format': time_format,
                'plid': plid,
                'price': price,
                'transactionid': tno
            })
            print(f"DEBUG: Order added successfully - transaction_id: {tno}, total_price: {total_price}")
        except Exception as e:
            print(f"ERROR: Failed to add order - transaction_id: {tno}, error: {str(e)}")
            flash("下單過程中出現錯誤，請稍後再試。")
            return redirect(url_for('travel_packages.cart'))

        # Step 5: Clear cart from database
        try:
            Cart.clear_cart(current_user.id)
            print(f"DEBUG: Cleared cart for user_id: {current_user.id}")
        except Exception as e:
            print(f"ERROR: Failed to clear cart for user_id: {current_user.id}, error: {str(e)}")
            flash("清空購物車時發生錯誤，請聯繫客服。")
            return redirect(url_for('travel_packages.cart'))

        # Step 6: Redirect to the complete page
        flash("下單完成！")
        return render_template('complete.html', user=current_user.name)

    except Exception as e:
        print(f"ERROR: Exception in complete_order - user_id: {current_user.id}, error: {str(e)}")
        flash(f"下單過程中出現錯誤: {str(e)}")
        return redirect(url_for('travel_packages.cart'))


@store.route('/orderlist')
@login_required
def orderlist():
    user_id = current_user.id

    # 獲取訂單
    data = Order_List.get_user_order(user_id)
    orderlist = []
    for i in data:
        temp = {
            '訂單編號': i[0],
            '訂單總價': i[1],  
            '訂單時間': i[2]
        }
        orderlist.append(temp)
    
    # 訂單詳細資訊
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