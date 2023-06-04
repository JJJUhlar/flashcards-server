import unittest
from app import app
import psycopg2
import bcrypt
from flask import Flask, jsonify
from flask.testing import FlaskClient
from unittest.mock import patch
import os
from config.testing_config import TestingConfig


class MyTestCase(unittest.TestCase):
    def setUp(self):
        print('setting up')

        app.config.from_object(TestingConfig)

        self.app = app.test_client()
        self.app.testing = True

        self.connection = psycopg2.connect(
            database=os.environ.get('DATABASE'),
            user=os.environ.get('DBUSER'),
            password=os.environ.get('DBPASS'),
            host=os.environ.get('DBHOST'),
            port="5432"
        )

        cursor = self.connection.cursor()
        self.seed_test_database(cursor=cursor)

        self.connection.commit()
        cursor.close()
        self.connection.close()

    def tearDown(self):
        print('tearing down')
        self.connection.close()

    def seed_test_database(*args, cursor):
        print('seeding test database')

        try:
            cursor.execute("DROP TABLE IF EXISTS flashcards;")
            cursor.execute("CREATE TABLE flashcards (id serial PRIMARY KEY,"
                    "origin VARCHAR(300),"
                    "input VARCHAR(2000),"
                    "card_type VARCHAR(100),"
                    "created_at date DEFAULT CURRENT_TIMESTAMP,"
                    "card_front VARCHAR(300),"
                    "card_back VARCHAR(300),"
                    "last_reviewed TIMESTAMP,"
                    "status VARCHAR(100),"
                    "ease INTEGER DEFAULT 100,"
                    "owner VARCHAR(100),"
                    "due date DEFAULT CURRENT_TIMESTAMP);")

            seed_cards = [("https://www.nytimes.com/2021/03/31/technology/amazon-union-vote.html",
                        "blah blah blah",
                        "default",
                        "What have the workers at Amazon been doing?",
                        "They have been trying to unionize.",
                        "new",
                        "Seph"),
                        ("https://en.wikipedia.org/wiki/Henry_VIII",
                        "Henry VIII (28 June 1491 – 28 January 1547) was King of England from 22 April 1509 until his death in 1547. Henry is best known for his six marriages, and for his efforts to have his first marriage (to Catherine of Aragon) annulled. His disagreement with Pope Clement VII about such an annulment led Henry to initiate the English Reformation, separating the Church of England from papal authority. He appointed himself Supreme Head of the Church of England and dissolved convents and monasteries, for which he was excommunicated by the pope.",
                        "default",
                        "Who was Henry VIII?",
                        "King of England from 1509 until his death in 1547.",
                        "new",
                        "Seph"),
                        ("https://en.wikipedia.org/wiki/Henry_VIII",
                        "Henry VIII (28 June 1491 – 28 January 1547) was King of England from 22 April 1509 until his death in 1547. Henry is best known for his six marriages, and for his efforts to have his first marriage (to Catherine of Aragon) annulled. His disagreement with Pope Clement VII about such an annulment led Henry to initiate the English Reformation, separating the Church of England from papal authority. He appointed himself Supreme Head of the Church of England and dissolved convents and monasteries, for which he was excommunicated by the pope.",
                        "default",
                        "What is Henry VIII best known for?",
                        "Six marriages",
                        "new",
                        "Seph"),
                        ("https://en.wikipedia.org/wiki/Henry_VIII",
                        "Henry VIII (28 June 1491 – 28 January 1547) was King of England from 22 April 1509 until his death in 1547. Henry is best known for his six marriages, and for his efforts to have his first marriage (to Catherine of Aragon) annulled. His disagreement with Pope Clement VII about such an annulment led Henry to initiate the English Reformation, separating the Church of England from papal authority. He appointed himself Supreme Head of the Church of England and dissolved convents and monasteries, for which he was excommunicated by the pope.",
                        "default",
                        "What did Henry VIII do that led to the English Reformation?",
                        "Disagree with Pope Clement VII about an annulment of his first marriage.",
                        "new",
                        "Seph")]

            seed_cards_sql = "INSERT INTO flashcards (origin, input, card_type, card_front, card_back, status, owner) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.executemany(seed_cards_sql, seed_cards)

            cursor.execute("DROP TABLE IF EXISTS users;")
            cursor.execute("CREATE TABLE users (id serial PRIMARY KEY,"
                        "username VARCHAR(100) UNIQUE,"
                        "email VARCHAR(200) UNIQUE,"
                        "password VARCHAR(200) NOT NULL,"
                        "created_at date DEFAULT CURRENT_TIMESTAMP,"
                        "updated_at date DEFAULT CURRENT_TIMESTAMP,"
                        "is_verified BOOLEAN DEFAULT FALSE);")

            seed_cards_sql = "INSERT INTO users (username, email, password, is_verified) VALUES (%s, %s, %s, %s)"
            seed_users = "Joseph", "jjuhlar@gmail.com", bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()), True
            cursor.execute(seed_cards_sql, seed_users)
        except Exception as e:
            print("Error seeding test database")
            print(e)

        
    @patch('app.check_password')
    def test_login_success(self, mock_check_password):
        mock_check_password.return_value = True  

        response = self.app.post('/api/login', json={'username': 'Joseph', 'password': 'password'})

        data = response.get_json()
        print(response.get_json(), "<<<<<")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['msg'], 'Login successful!')
        self.assertIn('sessionToken', data)

    @patch('app.check_password')
    def test_login_failure(self, mock_check_password):
        mock_check_password.return_value = False 

        response = self.app.post('/api/login', json={'username': 'Joseph', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        print(response)
        # self.assertEqual(data, {'error': 'Invalid username or password'})
    

if __name__ == '__main__':
    unittest.main()