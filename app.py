import os
import json
import logging
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Create context processor to inject today's date into all templates
@app.context_processor
def inject_utilities():
    """Add utility functions and values to templates"""
    return {'today': datetime.date.today().strftime('%Y-%m-%d')}


def load_daily_chores_config():
    """Load daily chores configuration from JSON file"""
    try:
        with open('daily_chores_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"daily_chores": [], "streak_bonuses": []}


def sync_daily_chores_from_config():
    """Sync daily chores from config file to database"""
    from models import DailyChore
    config = load_daily_chores_config()

    # Get list of chore names from config
    config_chore_names = set()
    for chore_config in config.get('daily_chores', []):
        config_chore_names.add(chore_config['name'])

        existing_chore = DailyChore.query.filter_by(
            name=chore_config['name']).first()

        if existing_chore:
            # Update existing chore
            existing_chore.description = chore_config.get('description', '')
            existing_chore.base_amount = chore_config['base_amount']
            existing_chore.max_amount = chore_config['max_amount']
            existing_chore.streak_increment = chore_config['streak_increment']
            existing_chore.streak_threshold = chore_config['streak_threshold']
            existing_chore.is_active = True  # Ensure it's active if it's in config
        else:
            # Create new chore
            new_chore = DailyChore(
                name=chore_config['name'],
                description=chore_config.get('description', ''),
                base_amount=chore_config['base_amount'],
                max_amount=chore_config['max_amount'],
                streak_increment=chore_config['streak_increment'],
                streak_threshold=chore_config['streak_threshold'],
                is_active=True)
            db.session.add(new_chore)

    # Remove or deactivate chores that are no longer in config
    db_chores = DailyChore.query.filter_by(is_active=True).all()
    for db_chore in db_chores:
        if db_chore.name not in config_chore_names:
            # Set as inactive instead of deleting to preserve completion history
            db_chore.is_active = False
            logging.info(
                f"Deactivated daily chore '{db_chore.name}' - no longer in config"
            )

    db.session.commit()


def calculate_streak_for_user_chore(user_id, daily_chore_id, completion_date):
    """Calculate the current streak for a user's daily chore"""
    from models import DailyChoreCompletion
    # Get all completions for this user and chore, ordered by date descending
    completions = DailyChoreCompletion.query.filter_by(
        user_id=user_id, daily_chore_id=daily_chore_id).filter(
            DailyChoreCompletion.date <= completion_date).order_by(
                DailyChoreCompletion.date.desc()).all()

    if not completions:
        return 1

    # Check for consecutive days
    streak = 1
    current_date = completion_date

    for completion in completions:
        expected_date = current_date - datetime.timedelta(days=1)
        if completion.date == expected_date:
            streak += 1
            current_date = completion.date
        elif completion.date == current_date:
            # Same day completion (shouldn't happen due to unique constraint)
            continue
        else:
            # Gap in streak
            break

    return streak


def calculate_streak_earnings(daily_chore, streak_count):
    """Calculate earnings based on streak count"""
    config = load_daily_chores_config()

    # Calculate base earnings with streak multiplier
    streak_multiplier = (streak_count - 1) // daily_chore.streak_threshold
    earnings = daily_chore.base_amount + (streak_multiplier *
                                          daily_chore.streak_increment)

    # Cap at maximum amount
    earnings = min(earnings, daily_chore.max_amount)

    # Check for streak bonuses
    bonus = 0.0
    for bonus_config in config.get('streak_bonuses', []):
        if streak_count == bonus_config['days']:
            bonus = bonus_config['bonus']
            break

    return earnings, bonus


# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


# Default hourly rate
DEFAULT_HOURLY_RATE = 10.0

# Import models after db is defined
from models import User, Family, Chore, ChoreCompletion, Goal, BehaviorRecord


# Database initialization
def init_db():
    """Initialize database tables and create initial data if needed."""
    # Create tables if they don't exist
    db.create_all()

    # Check if there are any users in the database
    if User.query.count() == 0:
        # Create a demo family
        demo_family = Family(name="Morris Family",
                             hourly_rate=DEFAULT_HOURLY_RATE)
        db.session.add(demo_family)
        db.session.commit()  # Commit to get the ID

        # Create demo parent user
        parent = User(username="parent",
                      password_hash=generate_password_hash("password"),
                      role="parent",
                      family_id=demo_family.id)
        db.session.add(parent)

        # Create demo child users
        virginia = User(username="Virginia",
                        password_hash=generate_password_hash("password"),
                        role="child",
                        family_id=demo_family.id)
        db.session.add(virginia)

        evelyn = User(username="Evelyn",
                      password_hash=generate_password_hash("password"),
                      role="child",
                      family_id=demo_family.id)
        db.session.add(evelyn)
        db.session.commit()  # Commit to get IDs
        lucy = User(username="Lucy",
                    password_hash=generate_password_hash("password"),
                    role="child",
                    family_id=demo_family.id)
        db.session.add(lucy)
        db.session.commit()
        # Add some goals
        # goal1 = Goal(
        #     family_id=demo_family.id,
        #     user_id=virginia.id,
        #     name="Occulus",
        #     description="Save for the latest game",
        #     amount=400.00,
        #     current_amount=15.00,
        #     is_family_goal=False
        # )
        # db.session.add(goal1)

        # behavior2 = BehaviorRecord(
        #     family_id=demo_family.id,
        #     user_id=noah.id,
        #     date=datetime.date.today(),
        #     description="Cleaned room without being asked",
        #     amount=3.00,
        #     is_positive=True
        # )
        # db.session.add(behavior2)

        # Add some chore completions
        # yesterday = datetime.date.today() - datetime.timedelta(days=1)
        # completion1 = ChoreCompletion(
        #     chore_id=1,
        #     user_id=emma.id,
        #     date=yesterday,
        #     time_spent_minutes=35,
        #     amount_earned=(35/60) * DEFAULT_HOURLY_RATE,
        #     status="completed"
        # )
        # db.session.add(completion1)


# Initialize database
with app.app_context():
    init_db()
    # Sync daily chores from configuration
    sync_daily_chores_from_config()


# Make utility functions available to all templates
@app.context_processor
def inject_utilities():
    """Add utility functions to templates"""
    return {
        'datetime': datetime,
        'now': datetime.datetime.now,
        'today': datetime.date.today,
        'calculate_child_earnings': calculate_child_earnings
    }


# Helper function to calculate earnings
def calculate_child_earnings(child_id):
    """Calculate total earnings for a child from all sources"""
    from models import ChoreCompletion, BehaviorRecord, DailyChoreCompletion, Purchase
    total_earnings = 0

    # Add earnings from regular chores
    completions = ChoreCompletion.query.filter_by(user_id=child_id).all()
    for completion in completions:
        total_earnings += completion.amount_earned

    # Add earnings from daily streak chores
    daily_completions = DailyChoreCompletion.query.filter_by(
        user_id=child_id).all()
    for completion in daily_completions:
        total_earnings += completion.amount_earned
        total_earnings += completion.streak_bonus_earned

    # Add earnings from behavior (positive and negative)
    behaviors = BehaviorRecord.query.filter_by(user_id=child_id).all()
    for behavior in behaviors:
        if behavior.is_positive:
            total_earnings += behavior.amount
        else:
            total_earnings -= behavior.amount

    # Subtract purchases
    purchases = Purchase.query.filter_by(user_id=child_id).all()
    for purchase in purchases:
        total_earnings -= purchase.amount

    return total_earnings


def update_family_goals(family_id):
    """Update current_amount for all family goals based on total family earnings since reset"""
    from models import User, Goal
    # Get all children in the family
    family_children = User.query.filter_by(family_id=family_id,
                                           role="child").all()

    # Calculate total family earnings
    total_family_earnings = 0
    for child in family_children:
        total_family_earnings += calculate_child_earnings(child.id)

    # Update all family goals for this family
    family_goals = Goal.query.filter_by(family_id=family_id,
                                        is_family_goal=True).all()

    for goal in family_goals:
        # Use total earnings minus the reset baseline for this specific goal
        goal.current_amount = max(0, total_family_earnings - goal.reset_amount)

    db.session.commit()


def update_individual_goals(user_id):
    """Update current_amount for individual goals based on child's earnings"""
    from models import Goal
    child_earnings = calculate_child_earnings(user_id)

    individual_goals = Goal.query.filter_by(user_id=user_id,
                                            is_family_goal=False).all()

    for goal in individual_goals:
        goal.current_amount = child_earnings

    db.session.commit()


def cleanup_inactive_daily_chores():
    """Permanently delete inactive daily chores and their completion records"""
    from models import DailyChore, DailyChoreCompletion

    inactive_chores = DailyChore.query.filter_by(is_active=False).all()

    for chore in inactive_chores:
        # Delete all completion records for this chore
        DailyChoreCompletion.query.filter_by(daily_chore_id=chore.id).delete()

        # Delete the chore itself
        db.session.delete(chore)
        logging.info(
            f"Permanently deleted inactive daily chore '{chore.name}' and its completion records"
        )

    db.session.commit()
    return len(inactive_chores)


# Authentication check
def login_required(f):

    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


def parent_required(f):

    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("login"))

        if current_user.role != "parent":
            flash("This action requires parent permissions", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# Routes
@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    # Get current user and family information
    user = current_user
    family = user.family

    # Get the user's role (parent or child)
    is_parent = user.role == "parent"

    # If parent, get all children in the family
    children = []
    if is_parent:
        # Query children in this family
        family_children = User.query.filter_by(family_id=family.id,
                                               role="child").all()

        for child in family_children:
            child_data = {
                "id": child.id,
                "username": child.username,
                "earnings": calculate_child_earnings(child.id),
                "goals": []
            }

            # Get this child's goals
            child_goals = Goal.query.filter_by(family_id=family.id,
                                               user_id=child.id).all()

            # Calculate child's total earnings once
            total_child_earnings = calculate_child_earnings(child.id)

            # Store goals with their progress
            child_goals_data = []
            for goal in child_goals:
                # Use total earnings to calculate progress
                goal_progress = (total_child_earnings /
                                 goal.amount) * 100 if goal.amount > 0 else 0
                # Cap progress at 100%
                capped_progress = min(goal_progress, 100)

                child_goals_data.append({
                    "id":
                    goal.id,
                    "name":
                    goal.name,
                    "progress":
                    capped_progress,
                    "current_amount":
                    total_child_earnings,
                    "amount":
                    goal.amount,
                    "proportion":
                    f"{(goal.amount / total_child_earnings * 100):.1f}%"
                    if total_child_earnings > 0 else "N/A"
                })

            # Sort goals by progress in descending order (highest completion first)
            child_goals_data.sort(key=lambda x: x["progress"], reverse=True)

            # Store sorted goals in child data
            child_data["goals"] = child_goals_data

            children.append(child_data)

    # Get family goals
    family_goals = []
    family_goal_records = Goal.query.filter_by(family_id=family.id,
                                               is_family_goal=True).all()

    # Calculate total family earnings for family goals
    family_children = User.query.filter_by(family_id=family.id,
                                           role="child").all()

    total_family_earnings = 0
    for child in family_children:
        total_family_earnings += calculate_child_earnings(child.id)

    for goal in family_goal_records:
        # Use the stored current_amount directly - don't recalculate if it was manually set/reset
        goal_progress = (goal.current_amount /
                         goal.amount) * 100 if goal.amount > 0 else 0
        family_goals.append({
            "id": goal.id,
            "name": goal.name,
            "progress": goal_progress,
            "current_amount": goal.current_amount,
            "amount": goal.amount
        })

    # Get recent chore completions
    # First get all chores belonging to the family
    family_chores = Chore.query.filter_by(family_id=family.id).all()
    chore_ids = [chore.id for chore in family_chores]

    recent_completions = []
    if chore_ids:  # Only query if there are chores
        completions = ChoreCompletion.query.filter(
            ChoreCompletion.chore_id.in_(chore_ids)).order_by(
                ChoreCompletion.date.desc()).limit(5).all()

        for completion in completions:
            chore = Chore.query.get(completion.chore_id)
            child = User.query.get(completion.user_id)
            if chore and child:
                recent_completions.append({
                    "id":
                    completion.id,
                    "chore_name":
                    chore.name,
                    "child_name":
                    child.username,
                    "date":
                    completion.date.strftime("%Y-%m-%d"),
                    "amount_earned":
                    completion.amount_earned
                })

    # If user is a child, get their specific data
    if not is_parent:
        child_id = user.id
        earnings = calculate_child_earnings(child_id)

        # Get child's goals
        my_goals = []
        child_goals = Goal.query.filter_by(family_id=family.id,
                                           user_id=child_id,
                                           is_family_goal=False).all()

        for goal in child_goals:
            goal_progress = (goal.current_amount /
                             goal.amount) * 100 if goal.amount > 0 else 0
            my_goals.append({
                "id": goal.id,
                "name": goal.name,
                "progress": goal_progress,
                "current_amount": goal.current_amount,
                "amount": goal.amount
            })

        # Get child's assigned chores
        my_chores = []
        child_chores = Chore.query.filter_by(family_id=family.id,
                                             assigned_to=child_id).all()

        for chore in child_chores:
            my_chores.append({
                "id": chore.id,
                "name": chore.name,
                "description": chore.description,
                "estimated_time_minutes": chore.estimated_time_minutes,
                "frequency": chore.frequency
            })

        return render_template("dashboard.html",
                               user=user,
                               family=family,
                               is_parent=is_parent,
                               earnings=earnings,
                               my_goals=my_goals,
                               family_goals=family_goals,
                               my_chores=my_chores,
                               recent_completions=recent_completions)

    return render_template("dashboard.html",
                           user=user,
                           family=family,
                           is_parent=is_parent,
                           children=children,
                           family_goals=family_goals,
                           recent_completions=recent_completions)


@app.route("/chores")
@login_required
def chores():
    user = current_user
    family = user.family
    is_parent = user.role == "parent"

    # Get chores from database
    family_chores = []
    chores_query = Chore.query.filter_by(family_id=family.id).all()

    for chore in chores_query:
        # Get the assigned child's name
        assigned_to_name = "Unassigned"
        if chore.assigned_to:
            assigned_child = User.query.get(chore.assigned_to)
            if assigned_child:
                assigned_to_name = assigned_child.username

        family_chores.append({
            "id": chore.id,
            "name": chore.name,
            "description": chore.description,
            "estimated_time_minutes": chore.estimated_time_minutes,
            "assigned_to": chore.assigned_to,
            "assigned_to_name": assigned_to_name,
            "frequency": chore.frequency,
            "status": chore.status
        })

    # If parent, get list of children for assignment dropdown
    children = []
    if is_parent:
        children_query = User.query.filter_by(family_id=family.id,
                                              role="child").all()
        for child in children_query:
            children.append({"id": child.id, "name": child.username})

    return render_template("chores.html",
                           user=user,
                           family=family,
                           is_parent=is_parent,
                           chores=family_chores,
                           children=children)


@app.route("/chores/add", methods=["POST"])
@parent_required
def add_chore():
    user = current_user
    family_id = user.family_id

    name = request.form.get("name")
    description = request.form.get("description", "")
    estimated_time = request.form.get("estimated_time", 0, type=int)
    assigned_to = request.form.get("assigned_to", "")
    frequency = request.form.get("frequency", "daily")

    if not name:
        flash("Chore name is required", "danger")
        return redirect(url_for("chores"))

    # Create the new chore in the database
    new_chore = Chore(family_id=family_id,
                      name=name,
                      description=description,
                      estimated_time_minutes=estimated_time,
                      assigned_to=assigned_to if assigned_to else None,
                      frequency=frequency,
                      status="active")

    db.session.add(new_chore)
    db.session.commit()

    flash(f"Chore '{name}' added successfully", "success")
    return redirect(url_for("chores"))


@app.route("/chores/<int:chore_id>/edit", methods=["POST"])
@parent_required
def edit_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)
    if chore.family_id != current_user.family_id:
        flash("You don't have permission to edit this chore", "danger")
        return redirect(url_for("chores"))

    chore.name = request.form.get("name", chore.name)
    chore.description = request.form.get("description", chore.description)
    chore.estimated_time_minutes = request.form.get(
        "estimated_time", chore.estimated_time_minutes, type=int)
    chore.assigned_to = request.form.get("assigned_to") or None
    chore.frequency = request.form.get("frequency", chore.frequency)
    chore.status = request.form.get("status", chore.status)

    db.session.commit()
    flash("Chore updated successfully", "success")
    return redirect(url_for("chores"))


@app.route("/chores/<int:chore_id>/delete", methods=["POST"])
@parent_required
def delete_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)
    if chore.family_id != current_user.family_id:
        flash("You don't have permission to delete this chore", "danger")
        return redirect(url_for("chores"))

    # Delete any completions for this chore
    ChoreCompletion.query.filter_by(chore_id=chore_id).delete()

    # Delete the chore
    db.session.delete(chore)
    db.session.commit()

    flash("Chore deleted successfully", "success")
    return redirect(url_for("chores"))


@app.route("/chores/<int:chore_id>/complete", methods=["POST"])
@login_required
def complete_chore(chore_id):
    user = current_user
    chore = Chore.query.get_or_404(chore_id)

    if chore.family_id != user.family_id:
        flash("You don't have permission to complete this chore", "danger")
        return redirect(url_for("dashboard"))

    # Check if the user is allowed to complete this chore
    is_parent = user.role == "parent"
    is_assigned = chore.assigned_to == user.id

    if not (is_parent or is_assigned):
        flash("You are not authorized to complete this chore", "danger")
        return redirect(url_for("dashboard"))

    # Get completion details
    time_spent = request.form.get("time_spent",
                                  chore.estimated_time_minutes,
                                  type=int)
    completion_date = request.form.get("completion_date")
    if completion_date:
        try:
            completion_date = datetime.datetime.strptime(
                completion_date, "%Y-%m-%d").date()
        except ValueError:
            completion_date = datetime.date.today()
    else:
        completion_date = datetime.date.today()

    # Get child_id from form - prioritize dropdown selection over hidden input
    child_id_select = request.form.get("child_id_select")
    child_id_hidden = request.form.get("child_id")

    # Determine the actual child_id
    if child_id_select and child_id_select.strip():
        # Use dropdown selection (for unassigned chores or parent overrides)
        child_id = child_id_select
    elif child_id_hidden and child_id_hidden.strip():
        # Use hidden input (for assigned chores)
        child_id = child_id_hidden
    elif chore.assigned_to:
        # Fall back to chore's assigned user
        child_id = chore.assigned_to
    elif not is_parent:
        # Fall back to current user if they're a child
        child_id = user.id
    else:
        flash("No child specified for completion", "danger")
        return redirect(url_for("chores"))

    # Ensure child_id is an integer and validate it's a real user
    try:
        child_id = int(child_id)
        child_user = User.query.get(child_id)
        if not child_user or child_user.family_id != user.family_id or child_user.role != "child":
            flash("Invalid child selection", "danger")
            return redirect(url_for("chores"))
    except (ValueError, TypeError):
        flash("Invalid child selection", "danger")
        return redirect(url_for("chores"))

    # Calculate earnings based on the hourly rate
    family = user.family
    hourly_rate = family.hourly_rate
    amount_earned = round((time_spent / 60) * hourly_rate, 2)

    # Create new completion record
    completion = ChoreCompletion(chore_id=chore.id,
                                 user_id=child_id,
                                 date=completion_date,
                                 time_spent_minutes=time_spent,
                                 amount_earned=amount_earned,
                                 status="completed")

    db.session.add(completion)
    db.session.commit()

    # Update individual goals for the child
    update_individual_goals(child_id)

    # Update family goals with new earnings
    update_family_goals(user.family_id)

    flash(f"Chore completed! Earned ${amount_earned:.2f}", "success")
    return redirect(url_for("dashboard"))


@app.route("/goals")
@login_required
def goals():
    user = current_user
    family = user.family
    is_parent = user.role == "parent"

    # Get individual goals
    individual_goals = []
    individual_goal_records = Goal.query.filter_by(family_id=family.id,
                                                   is_family_goal=False).all()

    for goal in individual_goal_records:
        goal_owner = User.query.get(goal.user_id)
        if goal_owner:
            # Get the child's total earnings
            total_child_earnings = calculate_child_earnings(goal_owner.id)

            # For individual goals, we'll show proportion of total earnings
            # We're using the total child's earnings as the current_amount instead
            # of the specific goal's current_amount
            goal_progress = (total_child_earnings /
                             goal.amount) * 100 if goal.amount > 0 else 0

            # For children, only show their own goals
            if not is_parent and goal.user_id != user.id:
                continue

            goal_data = {
                "id":
                goal.id,
                "name":
                goal.name,
                "description":
                goal.description,
                "amount":
                goal.amount,
                "current_amount":
                total_child_earnings,  # Use total earnings instead of goal-specific amount
                "user_name":
                goal_owner.username,
                "user_id":
                goal_owner.id,
                "progress":
                min(goal_progress, 100),  # Cap at 100%
                "total_earnings":
                total_child_earnings,
                "proportion":
                f"{(goal.amount / total_child_earnings * 100):.1f}%"
                if total_child_earnings > 0 else "N/A"
            }

            individual_goals.append(goal_data)

    # Get family goals
    family_goals = []
    family_goal_records = Goal.query.filter_by(family_id=family.id,
                                               is_family_goal=True).all()

    # Calculate total family earnings (sum of all children's earnings)
    family_children = User.query.filter_by(family_id=family.id,
                                           role="child").all()

    total_family_earnings = 0
    for child in family_children:
        total_family_earnings += calculate_child_earnings(child.id)

    for goal in family_goal_records:
        # Use the stored current_amount directly - don't recalculate if it was manually set/reset
        goal_progress = (goal.current_amount /
                         goal.amount) * 100 if goal.amount > 0 else 0
        goal_data = {
            "id": goal.id,
            "name": goal.name,
            "description": goal.description,
            "amount": goal.amount,
            "current_amount": goal.current_amount,
            "progress": goal_progress
        }
        family_goals.append(goal_data)

    # Commit any family goal current_amount updates
    db.session.commit()

    # If parent, get list of children for goal creation
    children = []
    if is_parent:
        family_children = User.query.filter_by(family_id=family.id,
                                               role="child").all()

        for child in family_children:
            children.append({"id": child.id, "name": child.username})

    return render_template("goals.html",
                           user=user,
                           family=family,
                           is_parent=is_parent,
                           individual_goals=individual_goals,
                           family_goals=family_goals,
                           children=children)


@app.route("/goals/add", methods=["POST"])
@parent_required
def add_goal():
    user = current_user
    family_id = user.family_id

    name = request.form.get("name")
    description = request.form.get("description", "")
    amount = request.form.get("amount", 0, type=float)
    goal_type = request.form.get("goal_type")
    user_id = request.form.get(
        "user_id") if goal_type == "individual" else None

    if not name:
        flash("Goal name is required", "danger")
        return redirect(url_for("goals"))

    if amount <= 0:
        flash("Goal amount must be greater than zero", "danger")
        return redirect(url_for("goals"))

    # Create a new goal in the database
    new_goal = Goal(family_id=family_id,
                    user_id=user_id,
                    name=name,
                    description=description,
                    amount=amount,
                    current_amount=0,
                    is_family_goal=(goal_type == "family"))

    # For family goals, set reset baseline to current total earnings so it starts from zero
    if goal_type == "family":
        from models import User
        family_children = User.query.filter_by(family_id=family_id,
                                               role="child").all()

        total_family_earnings = 0
        for child in family_children:
            total_family_earnings += calculate_child_earnings(child.id)

        new_goal.reset_amount = total_family_earnings

    db.session.add(new_goal)
    db.session.commit()

    flash(f"Goal '{name}' added successfully", "success")
    return redirect(url_for("goals"))


@app.route("/goals/<int:goal_id>/edit", methods=["POST"])
@parent_required
def edit_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    # Check if the goal belongs to the user's family
    if goal.family_id != current_user.family_id:
        flash("You don't have permission to edit this goal", "danger")
        return redirect(url_for("goals"))

    goal.name = request.form.get("name", goal.name)
    goal.description = request.form.get("description", goal.description)
    goal.amount = request.form.get("amount", goal.amount, type=float)
    goal.current_amount = request.form.get("current_amount",
                                           goal.current_amount,
                                           type=float)

    # Ensure current amount doesn't exceed the goal amount
    if goal.current_amount > goal.amount:
        goal.current_amount = goal.amount

    db.session.commit()
    flash("Goal updated successfully", "success")
    return redirect(url_for("goals"))


@app.route("/goals/<int:goal_id>/delete", methods=["POST"])
@parent_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    # Check if the goal belongs to the user's family
    if goal.family_id != current_user.family_id:
        flash("You don't have permission to delete this goal", "danger")
        return redirect(url_for("goals"))

    # Delete the goal
    db.session.delete(goal)
    db.session.commit()

    flash("Goal deleted successfully", "success")
    return redirect(url_for("goals"))


@app.route("/goals/<int:goal_id>/reset", methods=["POST"])
@parent_required
def reset_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    # Check if the goal belongs to the user's family
    if goal.family_id != current_user.family_id:
        flash("You don't have permission to reset this goal", "danger")
        return redirect(url_for("goals"))

    if goal.is_family_goal:
        # For family goals, set the reset baseline to current total family earnings
        # This allows each family goal to have independent progress tracking
        from models import User
        family_children = User.query.filter_by(family_id=goal.family_id,
                                               role="child").all()

        total_family_earnings = 0
        for child in family_children:
            total_family_earnings += calculate_child_earnings(child.id)

        goal.reset_amount = total_family_earnings
        goal.current_amount = 0.0

        flash(f"Family goal '{goal.name}' progress has been reset to $0.00",
              "success")
    else:
        # For individual goals, reset normally
        goal.current_amount = 0.0
        flash(f"Goal '{goal.name}' funds have been reset to $0.00", "success")

    db.session.commit()
    return redirect(url_for("goals"))


@app.route("/goals/<int:goal_id>/contribute", methods=["POST"])
@parent_required
def contribute_to_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    # Check if the goal belongs to the user's family
    if goal.family_id != current_user.family_id:
        flash("You don't have permission to contribute to this goal", "danger")
        return redirect(url_for("goals"))

    amount = request.form.get("amount", 0, type=float)
    if amount <= 0:
        flash("Contribution amount must be greater than zero", "danger")
        return redirect(url_for("goals"))

    # For personal goals, add the contribution directly
    if not goal.is_family_goal:
        # Add the contribution amount
        goal.current_amount += amount

        # Check if goal is now complete
        if goal.current_amount >= goal.amount:
            goal.current_amount = goal.amount
            flash(
                f"Congratulations! Goal '{goal.name}' has been fully funded!",
                "success")
        else:
            flash(f"Successfully contributed ${amount:.2f} to '{goal.name}'",
                  "success")

        db.session.commit()
    else:
        # For family goals, we don't manually adjust the amount since it's calculated
        # from the total children's earnings. Instead, just display a message.
        flash(
            f"Family goals are automatically funded based on children's earnings.",
            "info")

    return redirect(url_for("goals"))


@app.route("/goals/<int:goal_id>/apply-reward", methods=["POST"])
@parent_required
def apply_reward(goal_id):
    goal = Goal.query.get_or_404(goal_id)

    # Check if the goal belongs to the user's family
    if goal.family_id != current_user.family_id:
        flash("You don't have permission to apply rewards for this goal",
              "danger")
        return redirect(url_for("goals"))

    # Check if goal is complete
    if goal.current_amount < goal.amount:
        flash("This goal hasn't been fully funded yet", "warning")
        return redirect(url_for("goals"))

    # Create a negative behavior record to deduct the amount
    # This effectively "spends" the money that was saved for the goal
    deduction = BehaviorRecord(family_id=current_user.family_id,
                               user_id=goal.user_id,
                               date=datetime.date.today(),
                               description=f"Reward applied: {goal.name}",
                               amount=goal.amount,
                               is_positive=False)

    db.session.add(deduction)

    # Reset the goal amount to 0
    goal.current_amount = 0

    db.session.commit()
    flash(
        f"Reward for '{goal.name}' has been applied! ${goal.amount:.2f} has been deducted from the child's earnings.",
        "success")
    return redirect(url_for("goals"))


@app.route("/behavior")
@login_required
def behavior():
    user = current_user
    family = user.family
    is_parent = user.role == "parent"

    # Get behavior records from database
    if is_parent:
        # Parents can see all family behavior records
        records_query = BehaviorRecord.query.filter_by(
            family_id=family.id).order_by(BehaviorRecord.date.desc())
    else:
        # Children can only see their own records
        records_query = BehaviorRecord.query.filter_by(
            family_id=family.id,
            user_id=user.id).order_by(BehaviorRecord.date.desc())

    # Build behavior records with user information
    behavior_records = []
    for record in records_query:
        child = User.query.get(record.user_id)
        if child:
            record_data = {
                "id": record.id,
                "description": record.description,
                "amount": record.amount,
                "is_positive": record.is_positive,
                "date": record.date,
                "child_name": child.username,
                "child_id": child.id
            }
            behavior_records.append(record_data)

    # If parent, get list of children for behavior record creation
    children = []
    if is_parent:
        children_query = User.query.filter_by(family_id=family.id,
                                              role="child")
        for child in children_query:
            children.append({"id": child.id, "name": child.username})

    return render_template("behavior.html",
                           user=user,
                           family=family,
                           is_parent=is_parent,
                           behavior_records=behavior_records,
                           children=children)


@app.route("/behavior/add", methods=["POST"])
@parent_required
def add_behavior():
    user = current_user
    family_id = user.family_id

    description = request.form.get("description")
    amount = request.form.get("amount", 0, type=float)
    behavior_type = request.form.get("behavior_type")
    user_id = request.form.get("user_id")
    date_str = request.form.get("date",
                                datetime.datetime.now().strftime("%Y-%m-%d"))

    if not description:
        flash("Behavior description is required", "danger")
        return redirect(url_for("behavior"))

    if amount <= 0:
        flash("Amount must be greater than zero", "danger")
        return redirect(url_for("behavior"))

    if not user_id:
        flash("Child must be selected", "danger")
        return redirect(url_for("behavior"))

    # Convert the date string to a Python date object
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        date_obj = datetime.date.today()

    # Create new behavior record in the database
    child = User.query.get(user_id)
    if not child:
        flash("Selected child not found", "danger")
        return redirect(url_for("behavior"))

    new_record = BehaviorRecord(family_id=family_id,
                                user_id=int(user_id),
                                date=date_obj,
                                description=description,
                                amount=amount,
                                is_positive=(behavior_type == "positive"))

    db.session.add(new_record)
    db.session.commit()

    # Update individual goals for the child
    update_individual_goals(int(user_id))

    # Update family goals with new earnings/deductions
    update_family_goals(family_id)

    action = "awarded to" if behavior_type == "positive" else "deducted from"
    flash(f"${amount:.2f} {action} {child.username} for {description}",
          "success")
    return redirect(url_for("behavior"))


@app.route("/behavior/<int:record_id>/edit", methods=["POST"])
@parent_required
def edit_behavior(record_id):
    record = BehaviorRecord.query.get_or_404(record_id)

    # Ensure the record belongs to the current user's family
    if record.family_id != current_user.family_id:
        flash("You don't have permission to edit this record", "danger")
        return redirect(url_for("behavior"))

    description = request.form.get("description")
    amount = request.form.get("amount", 0, type=float)
    date_str = request.form.get("date")
    behavior_type = request.form.get("behavior_type")

    if description:
        record.description = description

    if amount > 0:
        record.amount = amount

    if date_str:
        try:
            record.date = datetime.datetime.strptime(date_str,
                                                     "%Y-%m-%d").date()
        except ValueError:
            # If date format is invalid, keep the current date
            pass

    record.is_positive = (behavior_type == "positive")

    # Update family goals with changed earnings
    update_family_goals(current_user.family_id)

    db.session.commit()
    flash("Behavior record updated successfully", "success")
    return redirect(url_for("behavior"))


@app.route("/behavior/<int:record_id>/delete", methods=["POST"])
@parent_required
def delete_behavior(record_id):
    record = BehaviorRecord.query.get_or_404(record_id)

    # Ensure the record belongs to the current user's family
    if record.family_id != current_user.family_id:
        flash("You don't have permission to delete this record", "danger")
        return redirect(url_for("behavior"))

    db.session.delete(record)

    # Update family goals after deletion
    update_family_goals(current_user.family_id)

    db.session.commit()
    flash("Behavior record deleted successfully", "success")
    return redirect(url_for("behavior"))


@app.route("/calendar")
@login_required
def calendar():
    user = current_user
    family = user.family
    is_parent = user.role == "parent"

    # Get all children in the family for filtering
    children = []
    family_children = User.query.filter_by(family_id=family.id,
                                           role="child").all()
    for child in family_children:
        children.append({"id": child.id, "name": child.username})

    # Get active chores for the family
    family_chores = []
    chores_query = Chore.query.filter_by(family_id=family.id,
                                         status="active").all()
    for chore in chores_query:
        assigned_to_name = "Unassigned"
        if chore.assigned_to:
            assigned_child = User.query.get(chore.assigned_to)
            if assigned_child:
                assigned_to_name = assigned_child.username

        family_chores.append({
            "id": chore.id,
            "name": chore.name,
            "estimated_time_minutes": chore.estimated_time_minutes,
            "assigned_to": chore.assigned_to,
            "assigned_to_name": assigned_to_name
        })

    return render_template("calendar.html",
                           user=user,
                           family=family,
                           is_parent=is_parent,
                           children=children,
                           chores=family_chores)


@app.route("/api/calendar-events")
@login_required
def calendar_events():
    user = current_user
    family = user.family
    is_parent = user.role == "parent"

    start_date = request.args.get("start")
    end_date = request.args.get("end")

    events = []

    # Add chore completions as events
    completions = ChoreCompletion.query.join(Chore).filter(
        Chore.family_id == family.id).all()

    for completion in completions:
        # For children, only show their own completions
        if not is_parent and completion.user_id != user.id:
            continue

        child = User.query.get(completion.user_id)
        chore = Chore.query.get(completion.chore_id)
        if not child or not chore:
            continue

        events.append({
            "id": completion.id,
            "title": f"{child.username}: {chore.name}",
            "start": completion.date.isoformat(),
            "end": completion.date.isoformat(),
            "allDay": True,
            "color": "#28a745",  # Green for completions
            "extendedProps": {
                "type": "completion",
                "chore_id": chore.id,
                "user_id": child.id,
                "time_spent": completion.time_spent_minutes,
                "amount_earned": completion.amount_earned
            }
        })

    # Add behavior records as events
    behavior_records = BehaviorRecord.query.filter_by(
        family_id=family.id).all()

    for record in behavior_records:
        # For children, only show their own behavior records
        if not is_parent and record.user_id != user.id:
            continue

        child = User.query.get(record.user_id)
        if not child:
            continue

        color = "#17a2b8" if record.is_positive else "#dc3545"  # Blue for positive, red for negative
        prefix = "+" if record.is_positive else "-"

        events.append({
            "id": record.id,
            "title": f"{child.username}: {prefix}${record.amount}",
            "start": record.date.isoformat(),
            "end": record.date.isoformat(),
            "allDay": True,
            "color": color,
            "extendedProps": {
                "type": "behavior",
                "user_id": child.id,
                "description": record.description,
                "amount": record.amount,
                "is_positive": record.is_positive
            }
        })

    return jsonify(events)


@app.route("/settings")
@login_required
def settings():
    user = current_user
    family = user.family
    is_parent = user.role == "parent"

    if not is_parent:
        flash("Only parents can access settings", "warning")
        return redirect(url_for("dashboard"))

    # Get all family members
    family_members = User.query.filter_by(family_id=family.id).all()

    # Separate parents and children
    parents = [member for member in family_members if member.role == "parent"]
    children = [member for member in family_members if member.role == "child"]

    # Get app statistics
    chore_count = Chore.query.filter_by(family_id=family.id).count()
    goal_count = Goal.query.filter_by(family_id=family.id).count()
    completion_count = ChoreCompletion.query.join(Chore).filter(
        Chore.family_id == family.id).count()
    behavior_count = BehaviorRecord.query.filter_by(
        family_id=family.id).count()

    return render_template("settings.html",
                           user=user,
                           family=family,
                           parents=parents,
                           children=children,
                           chore_count=chore_count,
                           goal_count=goal_count,
                           completion_count=completion_count,
                           behavior_count=behavior_count)


@app.route("/settings/update", methods=["POST"])
@parent_required
def update_settings():
    user = current_user
    family = user.family

    family_name = request.form.get("family_name", family.name)
    hourly_rate = request.form.get("hourly_rate",
                                   DEFAULT_HOURLY_RATE,
                                   type=float)

    if hourly_rate <= 0:
        flash("Hourly rate must be greater than zero", "danger")
        return redirect(url_for("settings"))

    family.name = family_name
    family.hourly_rate = hourly_rate

    db.session.commit()
    flash("Settings updated successfully", "success")
    return redirect(url_for("settings"))


@app.route("/settings/family/add", methods=["POST"])
@parent_required
def add_family_member():
    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role",
                            "child")  # Default to child if not specified

    # Validate input
    if not username or not password:
        flash("Username and password are required", "danger")
        return redirect(url_for("settings"))

    # Check if username already exists
    if User.query.filter_by(username=username).first():
        flash(f"Username '{username}' already exists", "danger")
        return redirect(url_for("settings"))

    # Create the new user
    new_user = User(username=username,
                    password_hash=generate_password_hash(password),
                    role=role,
                    family_id=current_user.family_id)
    db.session.add(new_user)
    db.session.commit()

    flash(f"New family member '{username}' added successfully", "success")
    return redirect(url_for("settings"))


@app.route("/settings/family/edit/<int:user_id>", methods=["POST"])
@parent_required
def edit_family_member(user_id):
    # Get the user to edit
    member = User.query.get_or_404(user_id)

    # Ensure the user belongs to the same family
    if member.family_id != current_user.family_id:
        flash("You don't have permission to edit this user", "danger")
        return redirect(url_for("settings"))

    username = request.form.get(f"username_{user_id}")
    new_password = request.form.get(f"password_{user_id}")
    total_earnings = request.form.get(f"total_earnings_{user_id}")

    # Validate input
    if not username:
        flash("Username is required", "danger")
        return redirect(url_for("settings"))

    # Check if username already exists and belongs to another user
    existing_user = User.query.filter_by(username=username).first()
    if existing_user and existing_user.id != user_id:
        flash(f"Username '{username}' already exists", "danger")
        return redirect(url_for("settings"))

    # Update the user
    member.username = username
    if new_password:
        member.password_hash = generate_password_hash(new_password)

    # Handle earnings adjustment for children
    if member.role == 'child' and total_earnings:
        try:
            new_total = float(total_earnings)
            current_total = calculate_child_earnings(member.id)
            adjustment = new_total - current_total

            if abs(
                    adjustment
            ) > 0.01:  # Only create record if there's a meaningful change
                # Create a behavior record to track this parent action
                behavior_record = BehaviorRecord(
                    family_id=current_user.family_id,
                    user_id=member.id,
                    date=datetime.date.today(),
                    description=
                    f"Parent Action: Total earnings set to ${new_total:.2f} (was ${current_total:.2f}) by {current_user.username}",
                    amount=abs(adjustment),
                    is_positive=adjustment > 0)
                db.session.add(behavior_record)

                # Update individual goals for this child
                update_individual_goals(member.id)

                # Update family goals
                update_family_goals(current_user.family_id)

                flash(
                    f"Total earnings set to ${new_total:.2f} for {member.username} (adjustment: ${adjustment:+.2f})",
                    "info")
        except ValueError:
            flash("Invalid earnings amount", "danger")
            return redirect(url_for("settings"))

    db.session.commit()
    flash(f"Family member updated successfully", "success")
    return redirect(url_for("settings"))


@app.route("/settings/family/delete/<int:user_id>", methods=["POST"])
@parent_required
def delete_family_member(user_id):
    from models import Purchase, DailyChoreCompletion

    # Get the user to delete
    member = User.query.get_or_404(user_id)

    # Ensure the user belongs to the same family
    if member.family_id != current_user.family_id:
        flash("You don't have permission to delete this user", "danger")
        return redirect(url_for("settings"))

    # Don't allow deleting the last parent
    if member.role == "parent":
        parent_count = User.query.filter_by(family_id=current_user.family_id,
                                            role="parent").count()
        if parent_count <= 1:
            flash("Cannot delete the last parent account", "danger")
            return redirect(url_for("settings"))

    # Don't allow self-deletion
    if member.id == current_user.id:
        flash("You cannot delete your own account", "danger")
        return redirect(url_for("settings"))

    # Delete related records first to avoid foreign key constraints

    # Delete purchases
    Purchase.query.filter_by(user_id=member.id).delete()

    # Delete daily chore completions
    DailyChoreCompletion.query.filter_by(user_id=member.id).delete()

    # Delete behavior records
    BehaviorRecord.query.filter_by(user_id=member.id).delete()

    # Delete chore completions
    ChoreCompletion.query.filter_by(user_id=member.id).delete()

    # Delete individual goals (not family goals)
    Goal.query.filter_by(user_id=member.id, is_family_goal=False).delete()

    # Unassign any chores assigned to this user
    assigned_chores = Chore.query.filter_by(assigned_to=member.id).all()
    for chore in assigned_chores:
        chore.assigned_to = None

    # Delete the user
    db.session.delete(member)
    db.session.commit()

    # Update family goals after deletion
    update_family_goals(current_user.family_id)

    flash(f"Family member '{member.username}' deleted successfully", "success")
    return redirect(url_for("settings"))


@app.route("/daily-streaks")
@login_required
def daily_streaks():
    """Display daily chore streak tracking page"""
    from models import DailyChore, DailyChoreCompletion
    user = current_user
    family = user.family
    is_parent = user.role == "parent"

    # Get all daily chores
    daily_chores = DailyChore.query.filter_by(is_active=True).all()

    # Get all children in the family
    children = User.query.filter_by(family_id=family.id, role="child").all()

    # Calculate streaks for each child and chore
    streak_data = {}
    today = datetime.date.today()

    for child in children:
        streak_data[child.id] = {}
        for chore in daily_chores:
            # Get the latest completion for this chore by this child
            latest_completion = DailyChoreCompletion.query.filter_by(
                user_id=child.id, daily_chore_id=chore.id).order_by(
                    DailyChoreCompletion.date.desc()).first()

            if latest_completion:
                # Calculate current streak
                streak = calculate_streak_for_user_chore(
                    child.id, chore.id, latest_completion.date)

                # Check if completed today
                completed_today = DailyChoreCompletion.query.filter_by(
                    user_id=child.id, daily_chore_id=chore.id,
                    date=today).first() is not None

                # Calculate current earnings rate
                earnings, bonus = calculate_streak_earnings(chore, streak)

                streak_data[child.id][chore.id] = {
                    'streak': streak,
                    'completed_today': completed_today,
                    'last_completion': latest_completion.date,
                    'current_earnings': earnings,
                    'potential_bonus': bonus,
                    'can_complete': not completed_today
                }
            else:
                # No completions yet
                streak_data[child.id][chore.id] = {
                    'streak': 0,
                    'completed_today': False,
                    'last_completion': None,
                    'current_earnings': chore.base_amount,
                    'potential_bonus': 0.0,
                    'can_complete': True
                }

    # Load streak bonuses configuration
    config = load_daily_chores_config()
    streak_bonuses = config.get('streak_bonuses', [])

    return render_template('daily_streaks.html',
                           daily_chores=daily_chores,
                           children=children,
                           streak_data=streak_data,
                           streak_bonuses=streak_bonuses,
                           is_parent=is_parent,
                           today=today)


@app.route("/daily-chores/<int:chore_id>/complete", methods=["POST"])
@login_required
def complete_daily_chore(chore_id):
    """Complete a daily chore and record streak"""
    from models import DailyChore, DailyChoreCompletion
    user = current_user
    is_parent = user.role == "parent"

    # Get the daily chore
    daily_chore = DailyChore.query.get_or_404(chore_id)

    # Get completion date and child
    completion_date_str = request.form.get("completion_date")
    child_id = request.form.get("child_id")

    if completion_date_str:
        try:
            completion_date = datetime.datetime.strptime(
                completion_date_str, "%Y-%m-%d").date()
        except ValueError:
            completion_date = datetime.date.today()
    else:
        completion_date = datetime.date.today()

    # Determine which child is completing the chore
    if is_parent and child_id:
        child = User.query.get_or_404(child_id)
        if child.family_id != user.family_id:
            flash("Invalid child selection", "danger")
            return redirect(url_for("daily_streaks"))
    else:
        child = user

    # Check if already completed today
    existing_completion = DailyChoreCompletion.query.filter_by(
        daily_chore_id=chore_id, user_id=child.id,
        date=completion_date).first()

    if existing_completion:
        flash(
            f"'{daily_chore.name}' has already been completed today for {child.username}",
            "warning")
        return redirect(url_for("daily_streaks"))

    # Calculate current streak
    streak = calculate_streak_for_user_chore(child.id, chore_id,
                                             completion_date)

    # Calculate earnings
    earnings, bonus = calculate_streak_earnings(daily_chore, streak)

    # Create completion record
    completion = DailyChoreCompletion(daily_chore_id=chore_id,
                                      user_id=child.id,
                                      family_id=child.family_id,
                                      date=completion_date,
                                      amount_earned=earnings,
                                      current_streak=streak,
                                      streak_bonus_earned=bonus)

    db.session.add(completion)
    db.session.commit()

    # Update individual goals for the child
    update_individual_goals(child.id)

    # Update family goals with new earnings
    update_family_goals(child.family_id)

    # Create success message
    message = f"'{daily_chore.name}' completed! Earned ${earnings:.2f}"
    if bonus > 0:
        message += f" + ${bonus:.2f} streak bonus"
    message += f" (Streak: {streak} days)"

    flash(message, "success")
    return redirect(url_for("daily_streaks"))


@app.route("/purchases")
@login_required
def purchases():
    user = current_user
    family = user.family
    is_parent = user.role == "parent"

    # Get all family children for parent view
    children = []
    if is_parent:
        children = User.query.filter_by(family_id=family.id,
                                        role="child").all()

    # Import Purchase model
    from models import Purchase

    # Get purchases for the family
    if is_parent:
        purchases = Purchase.query.filter_by(family_id=family.id).order_by(
            Purchase.date.desc()).all()
    else:
        purchases = Purchase.query.filter_by(family_id=family.id,
                                             user_id=user.id).order_by(
                                                 Purchase.date.desc()).all()

    # Get individual goals for purchase linking
    individual_goals = Goal.query.filter_by(family_id=family.id,
                                            is_family_goal=False).all()

    return render_template("purchases.html",
                           user=user,
                           family=family,
                           is_parent=is_parent,
                           children=children,
                           purchases=purchases,
                           individual_goals=individual_goals)


@app.route("/purchases/add", methods=["POST"])
@parent_required
def add_purchase():
    from models import Purchase
    user = current_user
    family_id = user.family_id

    item_name = request.form.get("item_name")
    amount = request.form.get("amount", 0, type=float)
    user_id = request.form.get("user_id")
    purchase_date = request.form.get("purchase_date")
    description = request.form.get("description", "")

    if not item_name:
        flash("Item name is required", "danger")
        return redirect(url_for("purchases"))

    if amount <= 0:
        flash("Amount must be greater than zero", "danger")
        return redirect(url_for("purchases"))

    if not user_id:
        flash("Child must be selected", "danger")
        return redirect(url_for("purchases"))

    # Convert date string to date object
    try:
        date_obj = datetime.datetime.strptime(purchase_date, "%Y-%m-%d").date()
    except ValueError:
        date_obj = datetime.date.today()

    # Verify child belongs to family
    child = User.query.get(user_id)
    if not child or child.family_id != family_id or child.role != "child":
        flash("Invalid child selection", "danger")
        return redirect(url_for("purchases"))

    # Create purchase record
    purchase = Purchase(family_id=family_id,
                        user_id=int(user_id),
                        date=date_obj,
                        item_name=item_name,
                        amount=amount,
                        description=description)

    db.session.add(purchase)
    db.session.commit()

    # Update individual goals for the child
    update_individual_goals(int(user_id))

    # Update family goals
    update_family_goals(family_id)

    flash(
        f"Purchase '{item_name}' recorded for {child.username} - ${amount:.2f}",
        "success")
    return redirect(url_for("purchases"))


@app.route("/daily-chores/cleanup", methods=["POST"])
@parent_required
def cleanup_daily_chores():
    """Clean up inactive daily chores"""
    deleted_count = cleanup_inactive_daily_chores()

    if deleted_count > 0:
        flash(f"Cleaned up {deleted_count} inactive daily chore(s)", "success")
    else:
        flash("No inactive daily chores to clean up", "info")

    return redirect(url_for("daily_streaks"))


@app.route("/goals/<int:goal_id>/purchase", methods=["POST"])
@parent_required
def purchase_goal(goal_id):
    from models import Purchase
    goal = Goal.query.get_or_404(goal_id)

    # Check if goal belongs to user's family
    if goal.family_id != current_user.family_id:
        flash("You don't have permission to purchase this goal", "danger")
        return redirect(url_for("goals"))

    # Only individual goals can be purchased
    if goal.is_family_goal:
        flash("Family goals cannot be purchased directly", "danger")
        return redirect(url_for("goals"))

    # Check if child has enough funds
    child_earnings = calculate_child_earnings(goal.user_id)
    if child_earnings < goal.amount:
        flash(
            f"Insufficient funds. {goal.user.username} has ${child_earnings:.2f} but needs ${goal.amount:.2f}",
            "danger")
        return redirect(url_for("goals"))

    # Create purchase record for the goal
    purchase = Purchase(family_id=goal.family_id,
                        user_id=goal.user_id,
                        goal_id=goal.id,
                        date=datetime.date.today(),
                        item_name=goal.name,
                        amount=goal.amount,
                        description=f"Goal purchase: {goal.description}"
                        if goal.description else f"Goal purchase: {goal.name}")

    db.session.add(purchase)

    # Mark goal as completed by resetting it
    goal.current_amount = 0.0

    db.session.commit()

    # Update individual goals for the child
    update_individual_goals(goal.user_id)

    # Update family goals
    update_family_goals(goal.family_id)

    flash(
        f"Goal '{goal.name}' purchased for {goal.user.username}! ${goal.amount:.2f} deducted.",
        "success")
    return redirect(url_for("goals"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
