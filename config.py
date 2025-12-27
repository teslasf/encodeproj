import os
from urllib.parse import urlparse, urlunparse

def load_env_file_bc_dotenv_doesnt_work(filepath='local_project.env'):
    try:
        with open(filepath) as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    except FileNotFoundError:
        print(f"Warning: {filepath} file not found. Skipping environment loading.")
    

# Load .env file early so that os.getenv() can retrieve values
load_env_file_bc_dotenv_doesnt_work()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

    # Local database URL for development/testing
    LOCAL_DATABASE_URL = 'postgresql://postgres:postresql.2024@localhost:5432/user_db'

    # Default to the DATABASE_URL from the environment (used in production/server)
    DATABASE_URL = os.getenv('DATABASE_URL', LOCAL_DATABASE_URL)

    # Parse the URL to modify its parameters
    parsed_url = urlparse(DATABASE_URL)
    query_params = parsed_url.query

    if os.getenv('FLASK_ENV') == 'production':
        query_params = 'sslmode=require'
    else:
        query_params = 'sslmode=disable'

    # Reconstruct the URL with updated query parameters
    DATABASE_URL = urlunparse(parsed_url._replace(query=query_params))
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')   
