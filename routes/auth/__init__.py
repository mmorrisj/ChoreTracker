# routes/auth/__init__.py
from flask import Blueprint

auth = Blueprint('auth', __name__)

from routes.auth.login_rt import login
from routes.auth.register_rt import register
from routes.auth.manage_users_rt import remove_user, all_users