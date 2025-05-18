from app import data

# This file is mostly for documentation purposes since we're using
# in-memory storage rather than a database. In a real application,
# we would define SQLAlchemy models here.

class User:
    """
    Represents a user in the system, which can be either a parent or a child.
    
    Attributes:
        id (str): Unique identifier for the user
        username (str): Username for login
        password_hash (str): Hashed password for security
        role (str): Either 'parent' or 'child'
        family_id (str): ID of the family the user belongs to
    """
    pass

class Family:
    """
    Represents a family unit containing parents and children.
    
    Attributes:
        id (str): Unique identifier for the family
        name (str): Family name
        hourly_rate (float): Default hourly rate for chore compensation
        parent_ids (list): List of parent user IDs
        child_ids (list): List of child user IDs
    """
    pass

class Chore:
    """
    Represents a household chore that can be assigned to children.
    
    Attributes:
        id (str): Unique identifier for the chore
        family_id (str): ID of the family the chore belongs to
        name (str): Name of the chore
        description (str): Detailed description of the chore
        estimated_time_minutes (int): Estimated time to complete in minutes
        assigned_to (str): ID of the child assigned to the chore
        frequency (str): How often the chore should be done (daily, weekly, etc.)
        status (str): Current status of the chore (active, inactive)
    """
    pass

class ChoreCompletion:
    """
    Represents a record of a completed chore.
    
    Attributes:
        id (str): Unique identifier for the completion record
        chore_id (str): ID of the completed chore
        user_id (str): ID of the child who completed the chore
        date (str): Date when the chore was completed
        time_spent_minutes (int): Actual time spent in minutes
        amount_earned (float): Money earned for completing the chore
        status (str): Status of the completion (completed, verified)
    """
    pass

class Goal:
    """
    Represents a savings goal for a child or the family.
    
    Attributes:
        id (str): Unique identifier for the goal
        family_id (str): ID of the family the goal belongs to
        user_id (str): ID of the child if it's an individual goal, None if family goal
        name (str): Name of the goal
        description (str): Detailed description of the goal
        amount (float): Total amount needed to reach the goal
        current_amount (float): Current amount saved toward the goal
        is_family_goal (bool): Whether this is a family goal or individual goal
    """
    pass

class BehaviorRecord:
    """
    Represents a record of behavioral awards or deductions.
    
    Attributes:
        id (str): Unique identifier for the behavior record
        family_id (str): ID of the family the record belongs to
        user_id (str): ID of the child to whom the behavior applies
        date (str): Date when the behavior occurred
        description (str): Description of the behavior
        amount (float): Amount awarded or deducted
        is_positive (bool): Whether this is a positive (award) or negative (deduction)
    """
    pass
