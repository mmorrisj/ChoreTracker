# routes/auth/__init__.py
from flask import Blueprint

ui = Blueprint('ui', __name__)

from routes.ui.completed_timeline_rt import get_completed_chores_timeline
from routes.ui.home_rt import home
from routes.ui.parent_dashboard_rt import parent_dashboard
from routes.ui.settings_rt import settings
from routes.ui.earning_expenses_rt import get_earnings_expenses_deductions