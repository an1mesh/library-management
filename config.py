import os
# from dotenv import load_dotenv

# load_dotenv('./env')

class Config:
    DATABASE_URI = (f'postgresql://{os.environ.get('DATABASE_USERNAME','db_username')}:{os.environ.get('DATABASE_PASSWORD','db_password')}@{os.environ.get('HOST','db_host')}:6000/{os.environ.get('DATABASE_NAME','db_name')}')
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_kEY','default_secret_key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY','default_jwt_secret_key')
    print('This is the secret key', SECRET_KEY, 'This is the jwt_secret_key' ,JWT_SECRET_KEY,'This is databse uri',DATABASE_URI)