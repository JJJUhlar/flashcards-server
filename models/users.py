import jwt
from datetime import datetime, timedelta
import bcrypt
from database import connection_pool
import os

from flask import request, abort


def authenticate_token(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization').split()[1]
        if not token:
            abort(401)
        try:
            payload = jwt.decode(token, os.environ.get('SECRET_KEY'), algorithms=['HS256'])
            username = payload['username']
        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
            abort(401, "Token is invalid or expired. Please log in again.")

        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__ + "_wrapper"
    return wrapper


def generate_auth_token(username):
    expiration = datetime.utcnow() + timedelta(minutes=int(10))
    payload = {
        'username': username,
        'exp': expiration
    }

    token = jwt.encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256')

    return token


def add_user(username, password, email):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = connection_pool.getconn()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (str(username), hashed_password, str(email)))
    except Exception as e:
        print('ERROR adding user to database')
        print(e)
    finally:
        conn.commit()
        cursor.close()
        connection_pool.putconn(conn)

    return {"message": "created user"}

def get_user_id(username):
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))  
        row = cursor.fetchone()
        user_id = int(row[0]) if row else 1
    except Exception as e:
        print('ERROR getting user id from database')
        print(e)
    finally:
        cursor.close()
        connection_pool.putconn(conn)
    return user_id

def check_password(username, password):
    conn = connection_pool.getconn()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))  
        row = cursor.fetchone()
        hashed_password = row[0] if row else None

        is_password_valid = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')) if hashed_password else False
    finally:
        cursor.close()
        connection_pool.putconn(conn)

    return is_password_valid


    
    