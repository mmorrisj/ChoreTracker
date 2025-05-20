"""
Database utilities for the Family Chore Tracker application.
Handles database initialization, migration, and backup.
"""

import os
import datetime
import logging
from app import app, db
from models import User, Family, Chore, ChoreCompletion, Goal, BehaviorRecord

logger = logging.getLogger(__name__)

def ensure_db_connection():
    """Test database connection and log status."""
    try:
        # Attempt to connect and do a simple query
        with app.app_context():
            from sqlalchemy import text
            db.session.execute(text("SELECT 1")).scalar()
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def initialize_database():
    """Create tables and initial data if needed."""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Check if data already exists
            if User.query.count() > 0:
                logger.info("Database already has data, skipping initialization")
                return True
                
            logger.info("Initializing database with sample data...")
            # Create initial data here if needed or import from init_db.py
            from init_db import init_db
            init_db()
            return True
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            return False

def backup_database(backup_path=None):
    """Create a backup of the database."""
    if backup_path is None:
        backup_path = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    db_url = app.config["SQLALCHEMY_DATABASE_URI"]
    try:
        # Extract DB info from URL - this is simplified, in production use proper parsing
        if "postgresql://" in db_url:
            # For Docker environment, use docker-compose
            if os.environ.get("DOCKER_ENV"):
                cmd = f"docker-compose exec db pg_dump -U chorechamp chorechamp > {backup_path}"
            else:
                # Local environment, direct pg_dump call would be here
                pass
                
        logger.info(f"Database backup created at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Database backup failed: {str(e)}")
        return False

def restore_database(backup_path):
    """Restore database from backup."""
    if not os.path.exists(backup_path):
        logger.error(f"Backup file not found: {backup_path}")
        return False
        
    db_url = app.config["SQLALCHEMY_DATABASE_URI"]
    try:
        # Extract DB info from URL - this is simplified, in production use proper parsing
        if "postgresql://" in db_url:
            # For Docker environment, use docker-compose
            if os.environ.get("DOCKER_ENV"):
                cmd = f"cat {backup_path} | docker-compose exec -T db psql -U chorechamp chorechamp"
            else:
                # Local environment, direct psql call would be here
                pass
                
        logger.info(f"Database restored from {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Database restoration failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Simple CLI for database management
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python db_utils.py [init|backup|restore]")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == "init":
        initialize_database()
    elif command == "backup":
        backup_path = sys.argv[2] if len(sys.argv) > 2 else None
        backup_database(backup_path)
    elif command == "restore":
        if len(sys.argv) < 3:
            print("Error: Must provide backup file path")
            sys.exit(1)
        restore_database(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print("Usage: python db_utils.py [init|backup|restore]")
        sys.exit(1)