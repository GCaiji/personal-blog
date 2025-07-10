import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('DB_PORT', 3306))
    MYSQL_USER = os.getenv('DB_USER', 'root')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    MYSQL_DB = os.getenv('DB_NAME', 'blog_db')
    MYSQL_CHARSET = os.getenv('MYSQL_CHARSET', 'utf8mb4')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key') # Change this to a strong, random key in production
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 12))