"""
Database initialization script for Family Chore Tracker application.
This script creates all necessary tables and initial data.
"""

import os
import datetime
from werkzeug.security import generate_password_hash
from app import app, db
from models import User, Family, Chore, ChoreCompletion, Goal, BehaviorRecord

def init_db():
    """Initialize the database with tables and sample data."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we already have data
        if Family.query.first() is not None:
            print("Database already has data. Skipping initialization.")
            return
        
        # Create a default family
        default_family = Family(
            name="Sample Family",
            hourly_rate=10.0
        )
        db.session.add(default_family)
        db.session.commit()
        
        # Create parent and child accounts
        parent = User(
            username="parent",
            password_hash=generate_password_hash("parentpassword"),
            role="parent",
            family_id=default_family.id
        )
        
        child1 = User(
            username="child1",
            password_hash=generate_password_hash("child1password"),
            role="child",
            family_id=default_family.id
        )
        
        child2 = User(
            username="child2",
            password_hash=generate_password_hash("child2password"),
            role="child",
            family_id=default_family.id
        )
        
        db.session.add_all([parent, child1, child2])
        db.session.commit()
        
        # Create sample chores
        chores = [
            Chore(
                family_id=default_family.id,
                name="Clean Bedroom",
                description="Make bed, vacuum floor, organize desk",
                estimated_time_minutes=30,
                assigned_to=child1.id,
                frequency="daily",
                status="active"
            ),
            Chore(
                family_id=default_family.id,
                name="Wash Dishes",
                description="Wash all dishes in the sink and put away",
                estimated_time_minutes=20,
                assigned_to=child2.id,
                frequency="daily",
                status="active"
            ),
            Chore(
                family_id=default_family.id,
                name="Mow Lawn",
                description="Cut grass in front and back yard",
                estimated_time_minutes=60,
                assigned_to=child1.id,
                frequency="weekly",
                status="active"
            )
        ]
        db.session.add_all(chores)
        db.session.commit()
        
        # Create sample goals
        goals = [
            Goal(
                family_id=default_family.id,
                user_id=child1.id,
                name="New Bicycle",
                description="Saving for a new mountain bike",
                amount=200.00,
                current_amount=50.00,
                is_family_goal=False
            ),
            Goal(
                family_id=default_family.id,
                user_id=child2.id,
                name="Video Game",
                description="Saving for the latest video game",
                amount=60.00,
                current_amount=15.00,
                is_family_goal=False
            ),
            Goal(
                family_id=default_family.id,
                name="Family Vacation",
                description="Saving for a family trip to the beach",
                amount=500.00,
                current_amount=100.00,
                is_family_goal=True
            )
        ]
        db.session.add_all(goals)
        db.session.commit()
        
        # Create sample behavior records
        behavior_records = [
            BehaviorRecord(
                family_id=default_family.id,
                user_id=child1.id,
                date=datetime.date.today() - datetime.timedelta(days=2),
                description="Helped neighbor with yard work",
                amount=5.00,
                is_positive=True
            ),
            BehaviorRecord(
                family_id=default_family.id,
                user_id=child2.id,
                date=datetime.date.today() - datetime.timedelta(days=1),
                description="Did an extra chore without being asked",
                amount=3.00,
                is_positive=True
            )
        ]
        db.session.add_all(behavior_records)
        db.session.commit()
        
        # Record some completed chores
        completions = [
            ChoreCompletion(
                chore_id=chores[0].id,
                user_id=child1.id,
                date=datetime.date.today() - datetime.timedelta(days=1),
                time_spent_minutes=25,
                amount_earned=25 * (default_family.hourly_rate / 60),
                status="completed"
            ),
            ChoreCompletion(
                chore_id=chores[1].id,
                user_id=child2.id,
                date=datetime.date.today() - datetime.timedelta(days=1),
                time_spent_minutes=20,
                amount_earned=20 * (default_family.hourly_rate / 60),
                status="completed"
            )
        ]
        db.session.add_all(completions)
        db.session.commit()
        
        print("Database initialized with sample data!")

if __name__ == "__main__":
    init_db()