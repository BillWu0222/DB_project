from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from api.sql import Package, Destination, Order_List, Records
import random, string

manager = Blueprint('manager', __name__, template_folder='../templates')

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.packageManager'))

@manager.route('/packageManager', methods=['GET', 'POST'])
@login_required
def packageManager():
    if request.method == 'GET':
        if current_user.role == 'user':
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        package_id = request.values.get('delete')
        associated_record = Records.check_product(package_id, None)  # 檢查是否有相關紀錄
        
        if associated_record:
            flash('無法刪除，該套餐存在相關紀錄')
        else:
            Package.delete_package(package_id)
            flash('成功刪除套餐')
    
    elif 'edit' in request.values:
        package_id = request.values.get('edit')
        return redirect(url_for('manager.edit', package_id=package_id))
    
    package_data = load_packages()
    return render_template('packageManager.html', package_data=package_data, user=current_user.name)

def load_packages():
    package_rows = Package.get_all_packages()
    package_data = []
    for row in package_rows:
        package = {
            '套餐編號': row[0],
            '套餐名稱': row[5],
            '開始日期': row[1],
            '結束日期': row[2],
            '價格': row[3],
            '數量': row[5],
            '描述': row[6]
        }
        package_data.append(package)
    return package_data

@manager.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        # 生成隨機的套餐編號
        package_id = ""
        while True:
            number = str(random.randrange(10000, 99999))
            en = random.choice(string.ascii_letters)
            package_id = en + number
            if not Package.get_package(package_id):
                break

        pname = request.values.get('pname')
        price = request.values.get('price')
        start_date = request.values.get('start_date')
        end_date = request.values.get('end_date')
        quantity = request.values.get('quantity')
        description = request.values.get('description')

        # 驗證必填欄位
        if not all([pname, price, start_date, end_date, quantity, description]):
            flash('所有欄位都是必填的，請確認輸入內容。')
            return redirect(url_for('manager.packageManager'))

        # 新增套餐
        Package.add_package({
            'pname': pname,
            'price': price,
            'startdate': start_date,
            'enddate': end_date,
            'description': description,
            'quantity': quantity
        })

        return redirect(url_for('manager.packageManager'))

    return render_template('addPackage.html')

@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    # 檢查使用者角色是否為 'user'，如果是，則無權限進入此頁面
    if request.method == 'GET':
        if current_user.role == 'user':
            flash('無權限')
            return redirect(url_for('index'))

    if request.method == 'POST':
        # 從表單中獲取更新的套餐數據
        package_id = request.values.get('package_id')
        pname = request.values.get('pname')
        price = request.values.get('price')
        start_date = request.values.get('start_date')
        end_date = request.values.get('end_date')
        description = request.values.get('description')

        # 更新套餐資料
        Package.update_package({
            'plid': package_id,
            'pname': pname,
            'totalprice': price,
            'startdate': start_date,
            'enddate': end_date,
            'description': description
        })

        return redirect(url_for('manager.packageManager'))

    else:
        # 如果是 GET 請求，從 URL 參數中獲取 package_id，並從資料庫中讀取對應的套餐資料
        package_id = request.args.get('package_id')
        package = Package.get_package(package_id)

  
        package_info = {
            '套餐編號': package[0], 
            '開始日期': package[1], 
            '結束日期': package[2],  
            '價格': package[3],      
            '套餐名稱': package[5],  
            '描述': package[6]       
        }
    
        return render_template('editPackage.html', data=package_info)

@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    """Admin view to manage and view all orders and their details."""
    if request.method == 'POST':
        pass  # Here you can add logic for POST requests if necessary, e.g., order status updates
    else:
        # Retrieve all orders for the admin view
        order_rows = Order_List.get_admin_order()
        order_data = []
        
        # Process each order row to build order summaries
        for row in order_rows:
            # Calculate total price if not already provided
            total_price = row[2] if row[2] is not None else Order_List.calculate_total_price(row[0])
            order = {
                '訂單編號': row[0],
                '訂購人': row[1],
                '訂單總價': total_price,
                '訂單時間': row[3]
            }
            order_data.append(order)
        
        # Retrieve detailed information for all orders for admin
        order_detail_rows = Order_List.get_all_order_details()
        order_details = []
        
        # Process each order detail row
        for row in order_detail_rows:
            order_detail = {
                '訂單編號': row[0],
                '套餐名稱': row[1],
                '單價': row[2],
                '數量': row[3]
            }
            order_details.append(order_detail)

    # Render the orderManager template with both the order summary and details
    return render_template('orderManager.html', orderData=order_data, orderDetail=order_details, user=current_user.name)
