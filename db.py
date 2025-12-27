import psycopg2
import logging
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import pool
from config import Config

# Configure the logging
logging.basicConfig(filename='userDB_errors.txt', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

db_pool = None
# Create a db connection pool 
class DatabaseConnectionPool:
    _instance = None
    def __new__(cls, minconn, maxconn) -> object:
        if cls._instance is None:
            cls._instance = super(DatabaseConnectionPool, cls).__new__(cls)
            cls._instance.init(minconn, maxconn)
        return cls._instance
            
    def init(self, minconn, maxconn):
        global db_pool
        self.ssl_mode = 'require' if Config.DATABASE_URL.startswith('postgres://') else 'disable' 
        print(Config.DATABASE_URL)          
        self.db_pool = pool.SimpleConnectionPool(
            minconn, maxconn,
            dsn=Config.DATABASE_URL, # Dynamically use the database URL from config
        )

    def get_conn(self):
        return self.db_pool.getconn()

    def put_conn(self, conn):
        print("Releasing connection back to pool...")
        self.db_pool.putconn(conn)
        print("Connection released.")

    def close_all(self):
        self.db_pool.closeall()


class LoginCredentials:
    def __init__(self, db_pool ,email, password):
        self.email = email
        self.db_pool = db_pool
        if password:
            self.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8) # hash the password


    def authenticate_user(self, text_password):
        conn = self.db_pool.get_conn()  
        try:
            with conn.cursor() as db_cursor:
                query = "SELECT user_password FROM user_info WHERE user_email = %s"
                db_cursor.execute(query, (self.email,))
                result = db_cursor.fetchone()

                if result and check_password_hash(result[0], text_password): 
                    conn.commit()  # Commit if the authentication is successful
                    return True
                else:
                    conn.rollback()  # Rollback if authentication fails
                    return False
        except Exception as e:
            error = f"Failed to authenticate user with email {self.email}: {str(e)}"
            logging.error(error)
            conn.rollback()  # Rollback on exception
            return False
        finally:
            self.db_pool.put_conn(conn)  

class MyDatabaseClass(LoginCredentials):
    def __init__(self, db_pool, name, password, email, comments):
        super().__init__(db_pool, email, password)
        self.name = name
        self.comments = comments
        self.img_url = None

    # Decorator for the methods
    def with_cursor(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            conn = self.db_pool.get_conn()  # Get a connection from the pool
            try:
                with conn.cursor() as db_cursor:
                    return func(self, db_cursor, *args, **kwargs)
            except Exception as e:
                error = f"Error in method {func.__name__} with args {args} and kwargs {kwargs}: {str(e)}"
                logging.error(error)
                conn.rollback()  # Rollback on exception
                raise
            finally:
                self.db_pool.put_conn(conn)  # Return the connection to the pool
        return wrapper

    @with_cursor
    def register_user(self, db_cursor):
        try:
            if self.check_if_data_exists(self.email):
                return False
            else:
                query = """
                    INSERT INTO user_info (user_name, user_password, user_email, user_comments)
                    VALUES (%s, %s, %s, %s)
                """
                db_cursor.execute(query, (self.name, self.password, self.email, self.comments))
                db_cursor.connection.commit()  # Commit the transaction
                return True
        except Exception as e:
            error = f"Failed to insert user with email {self.email}: {str(e)}"
            logging.error(error)
            db_cursor.connection.rollback()  # Rollback on exception
            return False
        
    @with_cursor
    def check_if_data_exists(self, db_cursor, email):
        try:
            query = "SELECT user_email FROM user_info WHERE user_email = %s"
            db_cursor.execute(query, (email,))
            result = db_cursor.fetchone()
            return result is not None
        except Exception as e:
            error = f"Failed to check if data exists for email {email}: {str(e)}"
            logging.error(error)
            db_cursor.connection.rollback()  # Rollback on exception
            return False
        
    @with_cursor
    def save_img_url_to_db(self, db_cursor, image_url):
        try:
            query = """
                UPDATE user_info 
                SET img_url = %s 
                WHERE user_email = %s
            """
            db_cursor.execute(query, (image_url, self.email))
            db_cursor.connection.commit()
            return True
        except Exception as e:
            error = f"Failed to update img url for {self.email}: {str(e)}"
            logging.error(error)
            db_cursor.connection.rollback()  # Rollback on exception
            return False
        
    @with_cursor
    def get_user_name(self, db_cursor):
        try:
            query = "SELECT user_name FROM user_info WHERE user_email = %s"
            
            db_cursor.execute(query, (self.email,))
            result = db_cursor.fetchone()
            if result:
                return result[0]  # Return the user_name if found
            else:
                return None 
    
        except Exception as e:
            error = f"Failed to update get user_names for {self.email}: {str(e)}"
            logging.error(error)
            db_cursor.connection.rollback()  # Rollback on exception
            return False
        
    @with_cursor
    def get_img_url(self, db_cursor):
        try:
            query = "SELECT img_url FROM user_info WHERE user_email = %s"
            db_cursor.execute(query, (self.email,))
            result = db_cursor.fetchone()
            if result != None:
                return result[0]
            else:
                return None
               
        except Exception as e:
            error = f"Failed to update get user_names for {self.email}: {str(e)}"
            logging.error(error)
            db_cursor.connection.rollback()  # Rollback on exception
            return False
    
            
            
        
        

# Close all the db connections to release back the memory space
def cleanup():
    global db_pool
    if db_pool:
        db_pool.close_all()
        print("Closed all connections")