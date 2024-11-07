from flask import render_template, Blueprint, redirect, request, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from api.sql import Member

# Define the Blueprint for the API
api = Blueprint('api', __name__, template_folder='./templates')

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'api.login'  
login_manager.login_message = "請先登入"  
login_manager.init_app(api)

class User(UserMixin):
    def __init__(self, id, role=None, name=None):
        self.id = id
        self.role = role
        self.name = name

@login_manager.user_loader
def user_loader(user_id):
    user_data = Member.get_role(user_id)  #
    if user_data:
        role, name = user_data[0], user_data[1]
        user = User(id=user_id, role=role, name=name)
        return user
    return None

# Login route
@api.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password'] 
        
        data = Member.get_member(account)  # Fetches (account, password, mid, role, name) 
        if data:
            db_password, user_id, role, name = data[1], data[2], data[3], data[4]
            if db_password == password:  
                user = User(id=user_id, role=role, name=name)
                login_user(user)

                # Redirect based on user role
                if role == 'user':
                    return redirect(url_for('travel_packages.travel_packages'))
                elif role == 'manager':
                    return redirect(url_for('manager.home'))
            else:
                flash('密碼錯誤，請再試一次')
        else:
            flash('無此帳號，請重新確認')

    return render_template('login.html')

# Registration route
@api.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user_account = request.form['account']
        user_password = request.form['password']
        username = request.form['username']
        identity = request.form['identity']

        # Check if the account already exists
        existing_accounts = [account[0] for account in Member.get_all_account()]
        if user_account in existing_accounts:
            flash('帳號已存在，請選擇其他帳號')
            return redirect(url_for('api.register'))
        else:
            # Insert new user into the database
            input_data = {
                'name': username,
                'account': user_account,
                'password': user_password,
                'identity': identity
            }
            Member.create_member(input_data)
            flash('註冊成功，請登入')
            return redirect(url_for('api.login'))

    return render_template('register.html')

# Logout route
@api.route('/logout')
@login_required
def logout():
    logout_user()
    flash('成功登出')
    return redirect(url_for('api.login'))
