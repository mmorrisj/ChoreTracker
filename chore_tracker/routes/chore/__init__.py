# routes/auth/__init__.py
from flask import Blueprint

chore = Blueprint('chore', __name__)

from routes.chore.clear_items_rt import (clear_all_completed_chores,
                                         clear_all_completed_expenses,
                                         clear_all_funds_and_chores,
                                         clear_all_preset_chores,
                                         clear_preset_chore,
                                         clear_all_preset_chores)

from routes.chore.manage_chores_rt import remove_chore, manage_chores,add_preset_chore
from routes.chore.add_amount_rt import add_quick_amount
from routes.chore.manage_spending_rt import manage_spending