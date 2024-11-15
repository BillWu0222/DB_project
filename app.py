import os
import base64  
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from api.api import api  
from api.sql import Member 
from bookstore.views.store import store as travel_packages 
from backstage.views.analysis import analysis
from backstage.views.manager import manager

app = Flask(__name__)
app.secret_key = 'Your Key'  

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

login_manager = LoginManager()
login_manager.init_app(app)

# Set login_manager's user_loader
@login_manager.user_loader
def load_user(user_id):
    return Member.get_member_by_id(user_id) 

# Register Blueprints
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(travel_packages, url_prefix='/packages')  
app.register_blueprint(analysis, url_prefix='/backstage')
app.register_blueprint(manager, url_prefix='/backstage')

def b64encode(value):
    """Encodes a binary image to base64."""
    return base64.b64encode(value).decode('utf-8')
app.jinja_env.filters['b64encode'] = b64encode

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Run app
if __name__ == '__main__':
    app.debug = True
    app.run()
