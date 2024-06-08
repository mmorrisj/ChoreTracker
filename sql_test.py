import sqlite3

# Connect to your database
conn = sqlite3.connect('schore_chart.db')
cursor = conn.cursor()

# Query to list all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

# Close the connection
conn.close()