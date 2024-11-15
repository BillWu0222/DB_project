import os
import random, string
from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user
from api.sql import Package, Destination, Order_List, Records
from werkzeug.utils import secure_filename
import base64

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
        associated_record = Records.check_product(package_id, None)
        
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
        #  base64 編碼
        image_data = row[7]
        if image_data:
            encoded_image = base64.b64encode(image_data).decode('utf-8')
        else:
            encoded_image = None

        package = {
            '套餐編號': row[0],
            '套餐名稱': row[5],
            '開始日期': row[1],
            '結束日期': row[2],
            '價格': row[3],
            '數量': row[4],
            '描述': row[6],
            '圖片': encoded_image  
        }
        package_data.append(package)
    return package_data

@manager.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        pname = request.form.get('pname')
        totalprice = request.form.get('price')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        quantity = request.form.get('quantity')
        description = request.form.get('description')
        image = request.files.get('image')

        if not all([pname, totalprice, start_date, end_date, quantity, description]):
            flash('所有欄位都是必填的，請確認輸入內容。')
            return redirect(url_for('manager.packageManager'))

        image_data = None
        if image:
            image_data = image.read()  

        Package.add_package({
            'pname': pname,
            'totalprice': totalprice,
            'startdate': start_date,
            'enddate': end_date,
            'description': description,
            'quantity': quantity,
            'image': image_data
        })

        return redirect(url_for('manager.packageManager'))

    return render_template('addPackage.html')

@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if current_user.role == 'user':
            flash('無權限')
            return redirect(url_for('index'))

    if request.method == 'POST':
        package_id = request.form.get('package_id')
        pname = request.form.get('pname')
        totalprice = request.form.get('price')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description')
        image = request.files.get('image')

        # 如果有上傳圖片，讀取圖片資料
        image_data = None
        if image and image.filename:
            image_data = image.read()  

        # 更新套餐資料
        Package.update_package({
            'plid': package_id,
            'pname': pname,
            'totalprice': totalprice,
            'startdate': start_date,
            'enddate': end_date,
            'description': description,
            'image': image_data  
        })

        return redirect(url_for('manager.packageManager'))

    # 如果是GET請求，獲取套餐數據並顯示在編輯頁面
    package_id = request.args.get('package_id')
    package = Package.get_package(package_id)
    package_info = {
        '套餐編號': package[0],
        '開始日期': package[1],
        '結束日期': package[2],
        '價格': package[3],
        '套餐名稱': package[5],
        '描述': package[6],
        '圖片': package[7]
    }
    return render_template('editPackage.html', data=package_info)

def generate_package_id():
    while True:
        number = str(random.randrange(10000, 99999))
        en = random.choice(string.ascii_letters)
        package_id = en + number
        if not Package.get_package(package_id):
            return package_id

@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_rows = Order_List.get_admin_order()
        order_data = [
            {
                '訂單編號': row[0],
                '訂購人': row[1],
                '訂單總價': row[2],
                '訂單時間': row[3]
            }
            for row in order_rows
        ]

        order_detail_rows = Order_List.get_all_order_details()
        order_details = [
            {
                '訂單編號': row[0],
                '套餐名稱': row[1],
                '單價': row[2],
                '數量': row[3]
            }
            for row in order_detail_rows
        ]

    return render_template('orderManager.html', orderData=order_data, orderDetail=order_details, user=current_user.name)
