from flask import render_template, Blueprint
from flask_login import login_required, current_user
from api.sql import Analysis

analysis = Blueprint('analysis', __name__, template_folder='../templates')

@analysis.route('/dashboard')
@login_required
def dashboard():
    # 各月的收入和訂單數量
    revenue = []
    order_counts = []
    for month in range(1, 13):
        # 月收入
        monthly_revenue_row = Analysis.month_price(month)
        if monthly_revenue_row:
            revenue.append(monthly_revenue_row[0][1])  # 月收入
        else:
            revenue.append(0)

        # 月訂單數量
        monthly_count_row = Analysis.month_count(month)
        if monthly_count_row:
            order_counts.append(monthly_count_row[0][1])  # 月訂單數量
        else:
            order_counts.append(0)

    # 各類套餐銷量
    category_sales = Analysis.category_sale()
    category_sales_data = [{'value': sale[0], 'name': sale[1]} for sale in category_sales]

    # 會員消費總額排名
    member_sales = Analysis.member_sale()
    member_revenue = [sale[0] for sale in member_sales]  # 消費金額
    member_names = [sale[2] for sale in member_sales]  # 會員名稱

    # 會員訂單數量排名
    member_order_counts = Analysis.member_sale_count()
    order_count_list = [count[0] for count in member_order_counts]  # 訂單數量列表

    return render_template(
        'dashboard.html',
        revenue=revenue,
        dataa=order_counts,
        datab=category_sales_data,
        datac=member_revenue,
        nameList=member_names,
        countList=order_count_list,
        user=current_user.name
    )
