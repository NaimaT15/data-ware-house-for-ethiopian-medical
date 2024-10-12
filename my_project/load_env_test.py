from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv('.env')

# Check if variables are loaded correctly
print(f"DBT_HOST: {os.getenv('DBT_HOST')}")
print(f"DBT_USER: {os.getenv('DBT_USER')}")
print(f"DBT_PASSWORD: {os.getenv('DBT_PASSWORD')}")
print(f"DBT_PORT: {os.getenv('DBT_PORT')}")
print(f"DBT_DBNAME: {os.getenv('DBT_DBNAME')}")
print(f"DBT_SCHEMA: {os.getenv('DBT_SCHEMA')}")
