import os
import json
import logging
import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# In-memory data storage
data = {
    "families": {},
    "users": {},
    "chores": {},
    "goals": {},
    "behavior_records": {},
    "chore_completions": {}
}

# Default hourly rate
DEFAULT_HOURLY_RATE = 10.0

# Helper functions for data management
def save_data():
    # In a real app, this would save to a database
    # Here we're just keeping everything in memory
    pass

def load_data():
    # In a real app, this would load from a database
    # Here we're just initializing with some demo data if empty
    if not data["users"]:
        # Create a demo parent account
        data["users"]["parent1"] = {
            "id": "parent1",
            "username": "parent",
            "password_hash": generate_password_hash("password"),
            "role": "parent",
            "family_id": "family1"
        }
        
        # Create demo children accounts
        data["users"]["child1"] = {
            "id": "child1",
            "username": "emma",
            "password_hash": generate_password_hash("password"),
            "role": "child",
            "family_id": "family1"
        }
        
        data["users"]["child2"] = {
            "id": "child2",
            "username": "noah",
            "password_hash": generate_password_hash("password"),
            "role": "child",
            "family_id": "family1"
        }
        
        # Create a demo family
        data["families"]["family1"] = {
            "id": "family1",
            "name": "Smith Family",
            "hourly_rate": DEFAULT_HOURLY_RATE,
            "parent_ids": ["parent1"],
            "child_ids": ["child1", "child2"]
        }
        
        # Add some default chores
        data["chores"]["chore1"] = {
            "id": "chore1",
            "family_id": "family1",
            "name": "Wash dishes",
            "description": "Wash all dishes and put them away",
            "estimated_time_minutes": 30,
            "assigned_to": "child1",
            "frequency": "daily",
            "status": "active"
        }
        
        data["chores"]["chore2"] = {
            "id": "chore2",
            "family_id": "family1",
            "name": "Vacuum living room",
            "description": "Vacuum the entire living room",
            "estimated_time_minutes": 20,
            "assigned_to": "child2",
            "frequency": "weekly",
            "status": "active"
        }
        
        data["chores"]["chore3"] = {
            "id": "chore3",
            "family_id": "family1",
            "name": "Take out trash",
            "description": "Empty all trash bins and take to curb",
            "estimated_time_minutes": 15,
            "assigned_to": "child1",
            "frequency": "weekly",
            "status": "active"
        }
        
        # Add some goals
        data["goals"]["goal1"] = {
            "id": "goal1",
            "family_id": "family1",
            "user_id": "child1",
            "name": "New video game",
            "description": "Save for the latest game",
            "amount": 60.00,
            "current_amount": 15.00,
            "is_family_goal": False
        }
        
        data["goals"]["goal2"] = {
            "id": "goal2",
            "family_id": "family1",
            "user_id": "child2",
            "name": "Lego set",
            "description": "Save for the new space Lego set",
            "amount": 100.00,
            "current_amount": 25.00,
            "is_family_goal": False
        }
        
        data["goals"]["goal3"] = {
            "id": "goal3",
            "family_id": "family1",
            "user_id": None,
            "name": "Family movie night",
            "description": "Everyone contributes to a special movie night with pizza",
            "amount": 50.00,
            "current_amount": 20.00,
            "is_family_goal": True
        }
        
        # Add some behavior records
        data["behavior_records"]["behavior1"] = {
            "id": "behavior1",
            "family_id": "family1",
            "user_id": "child1",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "description": "Helped sibling with homework",
            "amount": 5.00,
            "is_positive": True
        }
        
        data["behavior_records"]["behavior2"] = {
            "id": "behavior2",
            "family_id": "family1",
            "user_id": "child2",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "description": "Cleaned room without being asked",
            "amount": 3.00,
            "is_positive": True
        }
        
        # Add some chore completions
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        data["chore_completions"]["completion1"] = {
            "id": "completion1",
            "chore_id": "chore1",
            "user_id": "child1",
            "date": yesterday,
            "time_spent_minutes": 35,
            "amount_earned": (35/60) * DEFAULT_HOURLY_RATE,
            "status": "completed"
        }
        
        data["chore_completions"]["completion2"] = {
            "id": "completion2",
            "chore_id": "chore3",
            "user_id": "child1",
            "date": yesterday,
            "time_spent_minutes": 20,
            "amount_earned": (20/60) * DEFAULT_HOURLY_RATE,
            "status": "completed"
        }

# Load data at startup
load_data()

# Make data available to all templates
@app.context_processor
def inject_data():
    return {'data': data}

# Helper function to calculate earnings
def calculate_child_earnings(child_id):
    total_earnings = 0
    
    # Add earnings from chores
    for completion_id, completion in data["chore_completions"].items():
        if completion["user_id"] == child_id:
            total_earnings += completion["amount_earned"]
    
    # Add earnings from behavior (positive and negative)
    for behavior_id, behavior in data["behavior_records"].items():
        if behavior["user_id"] == child_id:
            if behavior["is_positive"]:
                total_earnings += behavior["amount"]
            else:
                total_earnings -= behavior["amount"]
    
    return total_earnings

# Authentication check
def login_required(f):
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def parent_required(f):
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page", "warning")
            return redirect(url_for("login"))
        
        user = data["users"].get(session["user_id"])
        if not user or user["role"] != "parent":
            flash("This action requires parent permissions", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = None
        for user_id, user_data in data["users"].items():
            if user_data["username"] == username:
                user = user_data
                break
        
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")
    
    return render_template("login.html", data=data)

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out successfully", "success")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = data["users"].get(session["user_id"])
    family = data["families"].get(user["family_id"])
    
    # Get the user's role (parent or child)
    is_parent = user["role"] == "parent"
    
    # If parent, get all children in the family
    children = []
    if is_parent:
        for child_id in family["child_ids"]:
            child = data["users"].get(child_id)
            if child:
                child_data = {
                    "id": child["id"],
                    "username": child["username"],
                    "earnings": calculate_child_earnings(child["id"]),
                    "goals": []
                }
                
                # Get this child's goals
                for goal_id, goal in data["goals"].items():
                    if goal["family_id"] == family["id"] and goal["user_id"] == child["id"]:
                        goal_progress = (goal["current_amount"] / goal["amount"]) * 100
                        child_data["goals"].append({
                            "id": goal["id"],
                            "name": goal["name"],
                            "progress": goal_progress,
                            "current_amount": goal["current_amount"],
                            "amount": goal["amount"]
                        })
                
                children.append(child_data)
    
    # Get family goals
    family_goals = []
    for goal_id, goal in data["goals"].items():
        if goal["family_id"] == family["id"] and goal["is_family_goal"]:
            goal_progress = (goal["current_amount"] / goal["amount"]) * 100
            family_goals.append({
                "id": goal["id"],
                "name": goal["name"],
                "progress": goal_progress,
                "current_amount": goal["current_amount"],
                "amount": goal["amount"]
            })
    
    # Get recent chore completions
    recent_completions = []
    for completion_id, completion in data["chore_completions"].items():
        chore = data["chores"].get(completion["chore_id"])
        if chore and chore["family_id"] == family["id"]:
            child = data["users"].get(completion["user_id"])
            if child:
                recent_completions.append({
                    "id": completion["id"],
                    "chore_name": chore["name"],
                    "child_name": child["username"],
                    "date": completion["date"],
                    "amount_earned": completion["amount_earned"]
                })
    
    # Sort completions by date (most recent first)
    recent_completions.sort(key=lambda x: x["date"], reverse=True)
    recent_completions = recent_completions[:5]  # Limit to 5 most recent
    
    # If user is a child, get their specific data
    if not is_parent:
        child_id = user["id"]
        earnings = calculate_child_earnings(child_id)
        
        # Get child's goals
        my_goals = []
        for goal_id, goal in data["goals"].items():
            if goal["family_id"] == family["id"] and goal["user_id"] == child_id:
                goal_progress = (goal["current_amount"] / goal["amount"]) * 100
                my_goals.append({
                    "id": goal["id"],
                    "name": goal["name"],
                    "progress": goal_progress,
                    "current_amount": goal["current_amount"],
                    "amount": goal["amount"]
                })
        
        # Get child's assigned chores
        my_chores = []
        for chore_id, chore in data["chores"].items():
            if chore["family_id"] == family["id"] and chore["assigned_to"] == child_id:
                my_chores.append({
                    "id": chore["id"],
                    "name": chore["name"],
                    "description": chore["description"],
                    "estimated_time_minutes": chore["estimated_time_minutes"]
                })
        
        return render_template(
            "dashboard.html", 
            user=user,
            family=family,
            is_parent=is_parent,
            earnings=earnings,
            my_goals=my_goals,
            family_goals=family_goals,
            my_chores=my_chores,
            recent_completions=recent_completions
        )
    
    return render_template(
        "dashboard.html", 
        user=user,
        family=family,
        is_parent=is_parent,
        children=children,
        family_goals=family_goals,
        recent_completions=recent_completions
    )

@app.route("/chores")
@login_required
def chores():
    user = data["users"].get(session["user_id"])
    family = data["families"].get(user["family_id"])
    is_parent = user["role"] == "parent"
    
    family_chores = []
    for chore_id, chore in data["chores"].items():
        if chore["family_id"] == family["id"]:
            # Get the assigned child's name
            assigned_to_name = "Unassigned"
            if chore["assigned_to"]:
                assigned_child = data["users"].get(chore["assigned_to"])
                if assigned_child:
                    assigned_to_name = assigned_child["username"]
            
            family_chores.append({
                "id": chore["id"],
                "name": chore["name"],
                "description": chore["description"],
                "estimated_time_minutes": chore["estimated_time_minutes"],
                "assigned_to": chore["assigned_to"],
                "assigned_to_name": assigned_to_name,
                "frequency": chore["frequency"],
                "status": chore["status"]
            })
    
    # If parent, get list of children for assignment dropdown
    children = []
    if is_parent:
        for child_id in family["child_ids"]:
            child = data["users"].get(child_id)
            if child:
                children.append({
                    "id": child["id"],
                    "name": child["username"]
                })
    
    return render_template(
        "chores.html",
        user=user,
        family=family,
        is_parent=is_parent,
        chores=family_chores,
        children=children
    )

@app.route("/chores/add", methods=["POST"])
@parent_required
def add_chore():
    user = data["users"].get(session["user_id"])
    family_id = user["family_id"]
    
    name = request.form.get("name")
    description = request.form.get("description", "")
    estimated_time = request.form.get("estimated_time", 0, type=int)
    assigned_to = request.form.get("assigned_to", "")
    frequency = request.form.get("frequency", "daily")
    
    if not name:
        flash("Chore name is required", "danger")
        return redirect(url_for("chores"))
    
    # Generate a unique ID
    chore_id = f"chore{len(data['chores']) + 1}"
    
    # Create the new chore
    data["chores"][chore_id] = {
        "id": chore_id,
        "family_id": family_id,
        "name": name,
        "description": description,
        "estimated_time_minutes": estimated_time,
        "assigned_to": assigned_to if assigned_to else None,
        "frequency": frequency,
        "status": "active"
    }
    
    flash(f"Chore '{name}' added successfully", "success")
    save_data()
    return redirect(url_for("chores"))

@app.route("/chores/<chore_id>/edit", methods=["POST"])
@parent_required
def edit_chore(chore_id):
    chore = data["chores"].get(chore_id)
    if not chore:
        flash("Chore not found", "danger")
        return redirect(url_for("chores"))
    
    chore["name"] = request.form.get("name", chore["name"])
    chore["description"] = request.form.get("description", chore["description"])
    chore["estimated_time_minutes"] = request.form.get("estimated_time", chore["estimated_time_minutes"], type=int)
    chore["assigned_to"] = request.form.get("assigned_to", chore["assigned_to"])
    chore["frequency"] = request.form.get("frequency", chore["frequency"])
    chore["status"] = request.form.get("status", chore["status"])
    
    flash("Chore updated successfully", "success")
    save_data()
    return redirect(url_for("chores"))

@app.route("/chores/<chore_id>/delete", methods=["POST"])
@parent_required
def delete_chore(chore_id):
    if chore_id in data["chores"]:
        del data["chores"][chore_id]
        flash("Chore deleted successfully", "success")
        save_data()
    else:
        flash("Chore not found", "danger")
    
    return redirect(url_for("chores"))

@app.route("/chores/<chore_id>/complete", methods=["POST"])
@login_required
def complete_chore(chore_id):
    user = data["users"].get(session["user_id"])
    chore = data["chores"].get(chore_id)
    
    if not chore:
        flash("Chore not found", "danger")
        return redirect(url_for("dashboard"))
    
    # Check if the user is allowed to complete this chore
    is_parent = user["role"] == "parent"
    is_assigned = chore["assigned_to"] == user["id"]
    
    if not (is_parent or is_assigned):
        flash("You are not authorized to complete this chore", "danger")
        return redirect(url_for("dashboard"))
    
    # Get completion details
    time_spent = request.form.get("time_spent", chore["estimated_time_minutes"], type=int)
    completion_date = request.form.get("completion_date", datetime.datetime.now().strftime("%Y-%m-%d"))
    child_id = request.form.get("child_id", user["id"] if not is_parent else chore["assigned_to"])
    
    # Calculate earnings based on the hourly rate
    family = data["families"].get(user["family_id"])
    hourly_rate = family.get("hourly_rate", DEFAULT_HOURLY_RATE)
    amount_earned = (time_spent / 60) * hourly_rate
    
    # Generate a unique ID for the completion
    completion_id = f"completion{len(data['chore_completions']) + 1}"
    
    # Record the completion
    data["chore_completions"][completion_id] = {
        "id": completion_id,
        "chore_id": chore_id,
        "user_id": child_id,
        "date": completion_date,
        "time_spent_minutes": time_spent,
        "amount_earned": amount_earned,
        "status": "completed"
    }
    
    flash(f"Chore completed! Earned ${amount_earned:.2f}", "success")
    save_data()
    return redirect(url_for("dashboard"))

@app.route("/goals")
@login_required
def goals():
    user = data["users"].get(session["user_id"])
    family = data["families"].get(user["family_id"])
    is_parent = user["role"] == "parent"
    
    # Get individual goals
    individual_goals = []
    for goal_id, goal in data["goals"].items():
        if goal["family_id"] == family["id"] and not goal["is_family_goal"]:
            user_data = data["users"].get(goal["user_id"])
            if user_data:
                goal_data = {
                    "id": goal["id"],
                    "name": goal["name"],
                    "description": goal["description"],
                    "amount": goal["amount"],
                    "current_amount": goal["current_amount"],
                    "user_name": user_data["username"],
                    "user_id": user_data["id"],
                    "progress": (goal["current_amount"] / goal["amount"]) * 100
                }
                
                # For children, only show their own goals
                if not is_parent and goal["user_id"] != user["id"]:
                    continue
                    
                individual_goals.append(goal_data)
    
    # Get family goals
    family_goals = []
    for goal_id, goal in data["goals"].items():
        if goal["family_id"] == family["id"] and goal["is_family_goal"]:
            goal_data = {
                "id": goal["id"],
                "name": goal["name"],
                "description": goal["description"],
                "amount": goal["amount"],
                "current_amount": goal["current_amount"],
                "progress": (goal["current_amount"] / goal["amount"]) * 100
            }
            family_goals.append(goal_data)
    
    # If parent, get list of children for goal creation
    children = []
    if is_parent:
        for child_id in family["child_ids"]:
            child = data["users"].get(child_id)
            if child:
                children.append({
                    "id": child["id"],
                    "name": child["username"]
                })
    
    return render_template(
        "goals.html",
        user=user,
        family=family,
        is_parent=is_parent,
        individual_goals=individual_goals,
        family_goals=family_goals,
        children=children
    )

@app.route("/goals/add", methods=["POST"])
@parent_required
def add_goal():
    user = data["users"].get(session["user_id"])
    family_id = user["family_id"]
    
    name = request.form.get("name")
    description = request.form.get("description", "")
    amount = request.form.get("amount", 0, type=float)
    goal_type = request.form.get("goal_type")
    user_id = request.form.get("user_id") if goal_type == "individual" else None
    
    if not name:
        flash("Goal name is required", "danger")
        return redirect(url_for("goals"))
    
    if amount <= 0:
        flash("Goal amount must be greater than zero", "danger")
        return redirect(url_for("goals"))
    
    # Generate a unique ID
    goal_id = f"goal{len(data['goals']) + 1}"
    
    # Create the new goal
    data["goals"][goal_id] = {
        "id": goal_id,
        "family_id": family_id,
        "user_id": user_id,
        "name": name,
        "description": description,
        "amount": amount,
        "current_amount": 0,
        "is_family_goal": goal_type == "family"
    }
    
    flash(f"Goal '{name}' added successfully", "success")
    save_data()
    return redirect(url_for("goals"))

@app.route("/goals/<goal_id>/edit", methods=["POST"])
@parent_required
def edit_goal(goal_id):
    goal = data["goals"].get(goal_id)
    if not goal:
        flash("Goal not found", "danger")
        return redirect(url_for("goals"))
    
    goal["name"] = request.form.get("name", goal["name"])
    goal["description"] = request.form.get("description", goal["description"])
    goal["amount"] = request.form.get("amount", goal["amount"], type=float)
    goal["current_amount"] = request.form.get("current_amount", goal["current_amount"], type=float)
    
    # Ensure current amount doesn't exceed the goal amount
    if goal["current_amount"] > goal["amount"]:
        goal["current_amount"] = goal["amount"]
    
    flash("Goal updated successfully", "success")
    save_data()
    return redirect(url_for("goals"))

@app.route("/goals/<goal_id>/delete", methods=["POST"])
@parent_required
def delete_goal(goal_id):
    if goal_id in data["goals"]:
        del data["goals"][goal_id]
        flash("Goal deleted successfully", "success")
        save_data()
    else:
        flash("Goal not found", "danger")
    
    return redirect(url_for("goals"))

@app.route("/goals/<goal_id>/contribute", methods=["POST"])
@parent_required
def contribute_to_goal(goal_id):
    goal = data["goals"].get(goal_id)
    if not goal:
        flash("Goal not found", "danger")
        return redirect(url_for("goals"))
    
    amount = request.form.get("amount", 0, type=float)
    if amount <= 0:
        flash("Contribution amount must be greater than zero", "danger")
        return redirect(url_for("goals"))
    
    goal["current_amount"] += amount
    
    # Check if goal is now complete
    if goal["current_amount"] >= goal["amount"]:
        goal["current_amount"] = goal["amount"]
        flash(f"Congratulations! Goal '{goal['name']}' has been fully funded!", "success")
    else:
        flash(f"Successfully contributed ${amount:.2f} to '{goal['name']}'", "success")
    
    save_data()
    return redirect(url_for("goals"))

@app.route("/behavior")
@login_required
def behavior():
    user = data["users"].get(session["user_id"])
    family = data["families"].get(user["family_id"])
    is_parent = user["role"] == "parent"
    
    # Get behavior records
    behavior_records = []
    for record_id, record in data["behavior_records"].items():
        if record["family_id"] == family["id"]:
            child = data["users"].get(record["user_id"])
            if child:
                # For children, only show their own records
                if not is_parent and record["user_id"] != user["id"]:
                    continue
                    
                record_data = {
                    "id": record["id"],
                    "description": record["description"],
                    "amount": record["amount"],
                    "is_positive": record["is_positive"],
                    "date": record["date"],
                    "child_name": child["username"],
                    "child_id": child["id"]
                }
                behavior_records.append(record_data)
    
    # Sort records by date (most recent first)
    behavior_records.sort(key=lambda x: x["date"], reverse=True)
    
    # If parent, get list of children for behavior record creation
    children = []
    if is_parent:
        for child_id in family["child_ids"]:
            child = data["users"].get(child_id)
            if child:
                children.append({
                    "id": child["id"],
                    "name": child["username"]
                })
    
    return render_template(
        "behavior.html",
        user=user,
        family=family,
        is_parent=is_parent,
        behavior_records=behavior_records,
        children=children
    )

@app.route("/behavior/add", methods=["POST"])
@parent_required
def add_behavior():
    user = data["users"].get(session["user_id"])
    family_id = user["family_id"]
    
    description = request.form.get("description")
    amount = request.form.get("amount", 0, type=float)
    behavior_type = request.form.get("behavior_type")
    user_id = request.form.get("user_id")
    date = request.form.get("date", datetime.datetime.now().strftime("%Y-%m-%d"))
    
    if not description:
        flash("Behavior description is required", "danger")
        return redirect(url_for("behavior"))
    
    if amount <= 0:
        flash("Amount must be greater than zero", "danger")
        return redirect(url_for("behavior"))
    
    if not user_id:
        flash("Child must be selected", "danger")
        return redirect(url_for("behavior"))
    
    # Generate a unique ID
    record_id = f"behavior{len(data['behavior_records']) + 1}"
    
    # Create the new behavior record
    data["behavior_records"][record_id] = {
        "id": record_id,
        "family_id": family_id,
        "user_id": user_id,
        "date": date,
        "description": description,
        "amount": amount,
        "is_positive": behavior_type == "positive"
    }
    
    child = data["users"].get(user_id)
    action = "awarded to" if behavior_type == "positive" else "deducted from"
    flash(f"${amount:.2f} {action} {child['username']} for {description}", "success")
    save_data()
    return redirect(url_for("behavior"))

@app.route("/behavior/<record_id>/edit", methods=["POST"])
@parent_required
def edit_behavior(record_id):
    record = data["behavior_records"].get(record_id)
    if not record:
        flash("Behavior record not found", "danger")
        return redirect(url_for("behavior"))
    
    record["description"] = request.form.get("description", record["description"])
    record["amount"] = request.form.get("amount", record["amount"], type=float)
    record["date"] = request.form.get("date", record["date"])
    record["is_positive"] = request.form.get("behavior_type") == "positive"
    
    flash("Behavior record updated successfully", "success")
    save_data()
    return redirect(url_for("behavior"))

@app.route("/behavior/<record_id>/delete", methods=["POST"])
@parent_required
def delete_behavior(record_id):
    if record_id in data["behavior_records"]:
        del data["behavior_records"][record_id]
        flash("Behavior record deleted successfully", "success")
        save_data()
    else:
        flash("Behavior record not found", "danger")
    
    return redirect(url_for("behavior"))

@app.route("/calendar")
@login_required
def calendar():
    user = data["users"].get(session["user_id"])
    family = data["families"].get(user["family_id"])
    is_parent = user["role"] == "parent"
    
    # Get all children in the family for filtering
    children = []
    for child_id in family["child_ids"]:
        child = data["users"].get(child_id)
        if child:
            children.append({
                "id": child["id"],
                "name": child["username"]
            })
    
    return render_template(
        "calendar.html",
        user=user,
        family=family,
        is_parent=is_parent,
        children=children
    )

@app.route("/api/calendar-events")
@login_required
def calendar_events():
    user = data["users"].get(session["user_id"])
    family = data["families"].get(user["family_id"])
    is_parent = user["role"] == "parent"
    
    start_date = request.args.get("start")
    end_date = request.args.get("end")
    
    events = []
    
    # Add chore completions as events
    for completion_id, completion in data["chore_completions"].items():
        chore = data["chores"].get(completion["chore_id"])
        if not chore or chore["family_id"] != family["id"]:
            continue
        
        # For children, only show their own completions
        if not is_parent and completion["user_id"] != user["id"]:
            continue
            
        child = data["users"].get(completion["user_id"])
        if not child:
            continue
            
        events.append({
            "id": completion["id"],
            "title": f"{child['username']}: {chore['name']}",
            "start": completion["date"],
            "end": completion["date"],
            "allDay": True,
            "color": "#28a745",  # Green for completions
            "extendedProps": {
                "type": "completion",
                "chore_id": chore["id"],
                "user_id": child["id"],
                "time_spent": completion["time_spent_minutes"],
                "amount_earned": completion["amount_earned"]
            }
        })
    
    # Add behavior records as events
    for record_id, record in data["behavior_records"].items():
        if record["family_id"] != family["id"]:
            continue
        
        # For children, only show their own behavior records
        if not is_parent and record["user_id"] != user["id"]:
            continue
            
        child = data["users"].get(record["user_id"])
        if not child:
            continue
            
        color = "#17a2b8" if record["is_positive"] else "#dc3545"  # Blue for positive, red for negative
        prefix = "+" if record["is_positive"] else "-"
        
        events.append({
            "id": record["id"],
            "title": f"{child['username']}: {prefix}${record['amount']}",
            "start": record["date"],
            "end": record["date"],
            "allDay": True,
            "color": color,
            "extendedProps": {
                "type": "behavior",
                "user_id": child["id"],
                "description": record["description"],
                "amount": record["amount"],
                "is_positive": record["is_positive"]
            }
        })
    
    return jsonify(events)

@app.route("/settings")
@login_required
def settings():
    user = data["users"].get(session["user_id"])
    family = data["families"].get(user["family_id"])
    is_parent = user["role"] == "parent"
    
    if not is_parent:
        flash("Only parents can access settings", "warning")
        return redirect(url_for("dashboard"))
    
    return render_template(
        "settings.html",
        user=user,
        family=family
    )

@app.route("/settings/update", methods=["POST"])
@parent_required
def update_settings():
    user = data["users"].get(session["user_id"])
    family = data["families"].get(user["family_id"])
    
    family_name = request.form.get("family_name", family["name"])
    hourly_rate = request.form.get("hourly_rate", DEFAULT_HOURLY_RATE, type=float)
    
    if hourly_rate <= 0:
        flash("Hourly rate must be greater than zero", "danger")
        return redirect(url_for("settings"))
    
    family["name"] = family_name
    family["hourly_rate"] = hourly_rate
    
    flash("Settings updated successfully", "success")
    save_data()
    return redirect(url_for("settings"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
