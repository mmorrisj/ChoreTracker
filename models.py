from app import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, Text
import datetime

class User(UserMixin, db.Model):
    """
    Represents a user in the system, which can be either a parent or a child.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'parent' or 'child'
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'))
    
    # Relationships
    family = db.relationship('Family', back_populates='users')
    assigned_chores = db.relationship('Chore', back_populates='assigned_to_user', foreign_keys='Chore.assigned_to')
    chore_completions = db.relationship('ChoreCompletion', back_populates='user')
    goals = db.relationship('Goal', back_populates='user')
    behavior_records = db.relationship('BehaviorRecord', back_populates='user')

class Family(db.Model):
    """
    Represents a family unit containing parents and children.
    """
    __tablename__ = 'families'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hourly_rate = db.Column(db.Float, default=10.0)
    
    # Relationships
    users = db.relationship('User', back_populates='family')
    chores = db.relationship('Chore', back_populates='family')
    goals = db.relationship('Goal', back_populates='family')
    behavior_records = db.relationship('BehaviorRecord', back_populates='family')

class Chore(db.Model):
    """
    Represents a household chore that can be assigned to children.
    """
    __tablename__ = 'chores'
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    estimated_time_minutes = db.Column(db.Integer, default=30)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly, once
    status = db.Column(db.String(20), default='active')  # active, inactive
    
    # Relationships
    family = db.relationship('Family', back_populates='chores')
    assigned_to_user = db.relationship('User', back_populates='assigned_chores', foreign_keys=[assigned_to])
    completions = db.relationship('ChoreCompletion', back_populates='chore')

class ChoreCompletion(db.Model):
    """
    Represents a record of a completed chore.
    """
    __tablename__ = 'chore_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    chore_id = db.Column(db.Integer, db.ForeignKey('chores.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    time_spent_minutes = db.Column(db.Integer, nullable=False)
    amount_earned = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='completed')  # completed, verified
    
    # Relationships
    chore = db.relationship('Chore', back_populates='completions')
    user = db.relationship('User', back_populates='chore_completions')

class Goal(db.Model):
    """
    Represents a savings goal for a child or the family.
    """
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    is_family_goal = db.Column(db.Boolean, default=False)
    reset_amount = db.Column(db.Float, default=0.0)  # Track amount that was reset
    
    # Relationships
    family = db.relationship('Family', back_populates='goals')
    user = db.relationship('User', back_populates='goals')

class BehaviorRecord(db.Model):
    """
    Represents a record of behavioral awards or deductions.
    """
    __tablename__ = 'behavior_records'
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    is_positive = db.Column(db.Boolean, default=True)
    
    # Relationships
    family = db.relationship('Family', back_populates='behavior_records')
    user = db.relationship('User', back_populates='behavior_records')


class Purchase(db.Model):
    """
    Represents a purchase made by a child using their earnings.
    """
    __tablename__ = 'purchases'
    
    id = db.Column(db.Integer, primary_key=True)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'), nullable=True)  # Optional: if linked to a goal
    date = db.Column(db.Date, default=datetime.date.today)
    item_name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    family = db.relationship('Family', foreign_keys=[family_id])
    user = db.relationship('User', foreign_keys=[user_id])
    goal = db.relationship('Goal', foreign_keys=[goal_id])


class DailyChore(db.Model):
    """
    Represents a daily chore configuration from the config file.
    """
    __tablename__ = 'daily_chores'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    base_amount = db.Column(db.Float, nullable=False)
    max_amount = db.Column(db.Float, nullable=False)
    streak_increment = db.Column(db.Float, nullable=False)
    streak_threshold = db.Column(db.Integer, nullable=False, default=5)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    completions = db.relationship('DailyChoreCompletion', back_populates='daily_chore')


class DailyChoreCompletion(db.Model):
    """
    Represents a daily chore completion record.
    """
    __tablename__ = 'daily_chore_completions'
    
    id = db.Column(db.Integer, primary_key=True)
    daily_chore_id = db.Column(db.Integer, db.ForeignKey('daily_chores.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    family_id = db.Column(db.Integer, db.ForeignKey('families.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today, nullable=False)
    amount_earned = db.Column(db.Float, nullable=False)
    current_streak = db.Column(db.Integer, default=1)
    streak_bonus_earned = db.Column(db.Float, default=0.0)
    
    # Relationships
    daily_chore = db.relationship('DailyChore', back_populates='completions')
    user = db.relationship('User', foreign_keys=[user_id])
    family = db.relationship('Family', foreign_keys=[family_id])
    
    # Ensure one completion per user per chore per day
    __table_args__ = (db.UniqueConstraint('daily_chore_id', 'user_id', 'date', name='unique_daily_chore_completion'),)
