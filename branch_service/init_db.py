import pymysql
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def create_database():
    """Create the database if it doesn't exist"""
    # Get database URL from environment or use default
    db_url = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost:3306/branch_service_db'
    
    # Parse the database URL
    parsed = urlparse(db_url.replace('mysql+pymysql://', 'mysql://'))
    
    # Extract connection details
    username = parsed.username or 'root'
    password = parsed.password or ''
    host = parsed.hostname or 'localhost'
    port = parsed.port or 3306
    database = parsed.path.lstrip('/')
    
    print(f"Connecting to MySQL server at {host}:{port}...")
    
    try:
        # Connect to MySQL server without specifying a database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=username,
            password=password
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Database '{database}' created successfully (or already exists)")
        
        cursor.close()
        connection.close()
        
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"✗ Error connecting to MySQL server: {e}")
        print("\nPlease ensure:")
        print("  1. MySQL server is running")
        print("  2. Connection credentials are correct")
        print("  3. You have permission to create databases")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = create_database()
    if not success:
        exit(1)
