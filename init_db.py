import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()

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

seed_cards = [("https://www.nytimes.com/2021/03/31/technology/amazon-union-vote.html",
            "blah blah blah",
            "default",
            "What have the workers at Amazon been doing?",
            "They have been trying to unionize.",
            "new",
            "Joseph"),
            ("https://en.wikipedia.org/wiki/Henry_VIII",
            "Henry VIII (28 June 1491 – 28 January 1547) was King of England from 22 April 1509 until his death in 1547. Henry is best known for his six marriages, and for his efforts to have his first marriage (to Catherine of Aragon) annulled. His disagreement with Pope Clement VII about such an annulment led Henry to initiate the English Reformation, separating the Church of England from papal authority. He appointed himself Supreme Head of the Church of England and dissolved convents and monasteries, for which he was excommunicated by the pope.",
            "default",
            "Who was Henry VIII?",
            "King of England from 1509 until his death in 1547.",
            "new",
            "Joseph"),
            ("https://en.wikipedia.org/wiki/Henry_VIII",
            "Henry VIII (28 June 1491 – 28 January 1547) was King of England from 22 April 1509 until his death in 1547. Henry is best known for his six marriages, and for his efforts to have his first marriage (to Catherine of Aragon) annulled. His disagreement with Pope Clement VII about such an annulment led Henry to initiate the English Reformation, separating the Church of England from papal authority. He appointed himself Supreme Head of the Church of England and dissolved convents and monasteries, for which he was excommunicated by the pope.",
            "default",
            "What is Henry VIII best known for?",
            "Six marriages",
            "new",
            "Joseph"),
            ("https://en.wikipedia.org/wiki/Henry_VIII",
            "Henry VIII (28 June 1491 – 28 January 1547) was King of England from 22 April 1509 until his death in 1547. Henry is best known for his six marriages, and for his efforts to have his first marriage (to Catherine of Aragon) annulled. His disagreement with Pope Clement VII about such an annulment led Henry to initiate the English Reformation, separating the Church of England from papal authority. He appointed himself Supreme Head of the Church of England and dissolved convents and monasteries, for which he was excommunicated by the pope.",
            "default",
            "What did Henry VIII do that led to the English Reformation?",
            "Disagree with Pope Clement VII about an annulment of his first marriage.",
            "new",
            "Joseph")]

seed_cards_sql = "INSERT INTO flashcards (origin, input, card_type, card_front, card_back, status, owner) VALUES (%s, %s, %s, %s, %s, %s, %s)"
cur.executemany(seed_cards_sql, seed_cards)

cur.execute("DROP TABLE IF EXISTS users;")
cur.execute("CREATE TABLE users (id serial PRIMARY KEY,"
            "username VARCHAR(100) UNIQUE,"
            "email VARCHAR(100) NOT NULL,"
            "password VARCHAR(100) NOT NULL,"
            "created_at date DEFAULT CURRENT_TIMESTAMP);")

seed_cards_sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
seed_users = "Joseph", "jjuhlar@gmail.com", "password"
cur.execute(seed_cards_sql, seed_users)

conn.commit()
cur.close()
conn.close()
