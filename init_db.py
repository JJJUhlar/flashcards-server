import os
import psycopg2

conn = psycopg2.connect(
    host=os.environ['DBHOST'],
    database=os.environ['DATABASE'],
    user=os.environ['DBUSER'],
    password=os.environ['DBPASS'])

cur=conn.cursor()

cur.execute("DROP TABLE IF EXISTS flashcards;")
cur.execute("CREATE TABLE flashcards (id serial PRIMARY KEY, "
            "origin VARCHAR(300),"
             "input VARCHAR(2000)," 
             "card_type VARCHAR(100)," 
             "created_at date DEFAULT CURRENT_TIMESTAMP," 
             "card_front VARCHAR(300)," 
             "card_back VARCHAR(300)," 
             "last_reviewed TIMESTAMP," 
             "status VARCHAR(100)," 
             "ease INTEGER DEFAULT 100," 
             "owner VARCHAR(100));")

cur.execute("INSERT INTO flashcards (origin, input, card_type, card_front, card_back, status, owner)"
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            ("https://www.nytimes.com/2021/03/31/technology/amazon-union-vote.html",
            "blah blah blah",
            "default",
            "What have the workers at Amazon been doing?",
            "They have been trying to unionize.",
            "new",
            "Joseph")
            )

conn.commit()
cur.close()
conn.close()
