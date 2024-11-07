import math
from flask import Blueprint, request, url_for, redirect, flash, render_template
from flask_login import login_required, current_user
from api.sql import Package, Destination, DB, Cart, Records
from datetime import datetime

# Define Blueprint
store = Blueprint('travel_packages', __name__, template_folder='../templates')

@store.route('/', methods=['GET', 'POST'])
@login_required
def travel_packages():
    result = Package.count()  
    count = math.ceil(result / 9)
    flag = 0

    if request.method == 'GET' and current_user.role == 'manager':
        flash('No permission')
        return redirect(url_for('manager.home'))

    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        search = request.values.get('keyword')
        
        package_rows = DB.fetchall('SELECT * FROM package WHERE pname LIKE %s', ('%' + search + '%',))
        package_data = []

        for row in package_rows:
            package = {
                '套餐編號': row[0],
                '套餐名稱': row[5],  
                '開始日期': row[1],  
                '結束日期': row[2],  
                '價格': row[3],     
                '數量': row[4] ,
                '描述': row[6] 
            }
            package_data.append(package)
            total += 1

        if len(package_data) < end:
            end = len(package_data)
            flag = 1

        final_data = package_data[start:end]
        count = math.ceil(total / 9)

        return render_template(
            'travel_packages.html', 
            single=single, 
            keyword=search, 
            package_data=final_data, 
            user=current_user.name, 
            page=page, 
            flag=flag, 
            count=count
        )
    elif 'packageid' in request.args:
        packageid = request.args['packageid']
        package_data = Package.get_package(packageid)
        destination_rows = DB.fetchall(
            'SELECT * FROM destination WHERE dpid = %s', 
            (packageid,)
        )
        if package_data:
            package = {
                '套餐編號': packageid,
                '套餐名稱': package_data[5],  
                '開始日期': package_data[1],   
                '結束日期': package_data[2],  
                '價格': package_data[3],      
                '數量': package_data[4],      
                '描述': package_data[6],     
                '景點列表': []  
            }
            for row in destination_rows:
                destination = {
                    '景點名稱': row[1], 
                    '位置': row[2],    
                    '行程價格': row[3],
                    '描述': row[5] 
                       
                }
                package['景點列表'].append(destination)

            return render_template(
                'destination_detail.html', 
                data=package, 
                user=current_user.name
            )
        else:
            flash("找不到此套餐的詳細資料")
            return redirect(url_for('travel_packages.travel_packages'))
    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        
        package_rows = Package.get_all_packages()
        package_data = []
        for row in package_rows:
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

        if len(package_data) < end:
            end = len(package_data)
            flag = 1

        final_data = package_data[start:end]

        return render_template(
            'travel_packages.html', 
            package_data=final_data, 
            user=current_user.name, 
            page=page, 
            flag=flag, 
            count=count
        )

    else:
        package_rows = Package.get_all_packages()[:9] 
        package_data = []

        for row in package_rows:
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

        return render_template(
            'travel_packages.html', 
            package_data=package_data, 
            user=current_user.name, 
            page=1, 
            flag=flag, 
            count=count
        )

# 會員購物車
@store.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    if request.method == 'GET' and current_user.role == 'manager':
        flash('No permission')
        return redirect(url_for('manager.home'))

    if request.method == 'POST' and "plid" in request.form:
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
            Records.add_product({'pid': plid, 'tno': tno, 'saleprice': package_price})
        else:
            current_amount = Records.get_amount(tno, plid)
            Records.update_product({'amount': current_amount + 1, 'tno': tno, 'pid': plid})

    elif "delete" in request.form:
        plid = int(request.form.get('delete'))
        tno = int(Cart.get_cart(current_user.id)[0])  
        Records.delete_check(plid, tno)

    elif "buy" in request.form:
        change_order()
        return redirect(url_for('store.order'))

     # 這邊點完結帳頁面btn後，要跑去complete.html的頁面！但還沒調整到，所以現在下訂單的功能還是壞的
     
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

# 訂單頁面
@store.route('/order')
@login_required
def order():
    """Displays the order summary page."""
    cart_data = Cart.get_cart(current_user.id)
    if not cart_data:
        flash("No active cart found.")
        return redirect(url_for('travel_packages.cart'))

    tno = cart_data[0]  
    order_items = Records.get_record(tno)
    order_data = [
        {
            '套餐編號': item[1],
            '套餐名稱': Package.get_name(item[1]),
            '開始日期': Package.get_start_date(item[1]),
            '結束日期': Package.get_end_date(item[1]),
            '價格': item[3],
            '數量': item[2],
            '總價': item[2] * item[3] 
        }
        for item in order_items
    ]
    total_cost = Records.get_total(tno)
    return render_template('order.html', data=order_data, total=total_cost, user=current_user.name)
