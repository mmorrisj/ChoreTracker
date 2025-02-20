# chore_tracker/routes/__init__.py

from flask import Blueprint

# Create just one blueprint for all routes
routes_bp = Blueprint('main', __name__)

# Import route modules so they attach their routes to routes_bp
# (Import these after defining routes_bp to avoid circular imports)
from chore_tracker.routes import add_amount_rt
from chore_tracker.routes import clear_items_rt
from chore_tracker.routes import complete_chore_rt
from chore_tracker.routes import completed_timeline_rt
from chore_tracker.routes import earning_expenses_rt
from chore_tracker.routes import home_rt
from chore_tracker.routes import login_rt
from chore_tracker.routes import manage_chores_rt
from chore_tracker.routes import manage_spending_rt
from chore_tracker.routes import manage_users_rt
from chore_tracker.routes import parent_dashboard_rt
from chore_tracker.routes import register_rt
from chore_tracker.routes import settings_rt
