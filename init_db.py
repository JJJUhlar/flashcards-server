import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
import bcrypt

conn = psycopg2.connect(
    host=os.environ['DBHOST'],
    database=os.environ['DATABASE'],
    user=os.environ['DBUSER'],
    password=os.environ['DBPASS']
    )

cur=conn.cursor()

cur.execute("DROP TABLE IF EXISTS flashcards;")
cur.execute("CREATE TABLE flashcards (id serial PRIMARY KEY,"
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

seed_cards = [("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What is the capital of California?",
            "Sacramento",
            "new",
            "Test1"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What state is Santa Barbara in?",
            "California",
            "new",
            "Test1"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What animal is on the flag of California?",
            "The Californian Grizzly",
            "new",
            "Test1"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "Sacramento",
            "What is the capital of California?",
            "new",
            "Test2"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What state is Santa Barbara in?",
            "California",
            "new",
            "Test2"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What animal is on the flag of California?",
            "The Californian Grizzly",
            "new",
            "Test2"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What is the capital of California?",
            "Sacramento",
            "new",
            "Test3"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What state is Santa Barbara in?",
            "California",
            "new",
            "Test3"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What animal is on the flag of California?",
            "The Californian Grizzly",
            "new",
            "Test3"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What is the capital of California?",
            "Sacramento",
            "new",
            "Test4"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What state is Santa Barbara in?",
            "California",
            "new",
            "Test4"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What animal is on the flag of California?",
            "The Californian Grizzly",
            "new",
            "Test4"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What is the capital of California?",
            "Sacramento",
            "new",
            "Test5"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What state is Santa Barbara in?",
            "California",
            "new",
            "Test5"),
            ("https://en.wikipedia.org/wiki/California",
             "some facts about California",
            "default",
            "What animal is on the flag of California?",
            "The Californian Grizzly",
            "new",
            "Test5")]

seed_cards_sql = "INSERT INTO flashcards (origin, input, card_type, card_front, card_back, status, owner) VALUES (%s, %s, %s, %s, %s, %s, %s)"
cur.executemany(seed_cards_sql, seed_cards)

cur.execute("DROP TABLE IF EXISTS users;")
cur.execute("CREATE TABLE users (id serial PRIMARY KEY,"
            "username VARCHAR(100) UNIQUE,"
            "email VARCHAR(200) UNIQUE,"
            "password VARCHAR(200) NOT NULL,"
            "created_at date DEFAULT CURRENT_TIMESTAMP,"
            "updated_at date DEFAULT CURRENT_TIMESTAMP);")

seed_cards_sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
password = "password123"
pwhash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
seed_users = [("Test1", "test1@example.com", pwhash.decode('utf8')),
              ("Test2", "test2@example.com", pwhash.decode('utf8')),
              ("Test3", "test3@example.com", pwhash.decode('utf8')),
              ("Test4", "test4@example.com", pwhash.decode('utf8')),
              ("Test5", "test5@example.com", pwhash.decode('utf8'))]

cur.executemany(seed_cards_sql, seed_users)

conn.commit()
cur.close()
conn.close()
