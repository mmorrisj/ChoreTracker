import logging
from app import app, db
from db_utils import ensure_db_connection, initialize_database

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize database when app starts
with app.app_context():
    try:
        # Check database connection
        if ensure_db_connection():
            # Initialize database tables and sample data if needed
            initialize_database()
            logger.info("Database initialization complete")
        else:
            logger.error("Failed to connect to database. Check your DATABASE_URL environment variable.")
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
