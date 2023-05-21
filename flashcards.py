import guardrails as gd
import openai
import os 
import psycopg2
from psycopg2 import pool
import psycopg2.extras
from flask import jsonify
from datetime import datetime;
from datetime import timedelta;

postgreSQL_pool = pool.SimpleConnectionPool(1, 20, user=os.environ['DBUSER'],
                                                         password=os.environ['DBPASS'],
                                                         host=os.environ['DBHOST'],
                                                         database=os.environ['DATABASE'])

openai.api_key = os.environ["OPENAI_API_KEY"]

def getFlashcards(text, card_type="default", model="text-davinci-003"): 
    text = str(text)

    if card_type == "default":
        flashcard_guard = gd.Guard.from_rail('./card-rails/default_flashcards.rail', num_reasks=1)
        try:
            raw_llm_output, validated_output = flashcard_guard(
                openai.Completion.create,
                prompt_params={"text": text},
                engine=model,
                max_tokens=1024,
                temperature=0.3,
            )
            return validated_output
        except:
            print('error getting cards')
            return "error getting flashcards from model"

    elif card_type == "acrostic":
        acrostic_guard = gd.Guard.from_rail('./card-rails/acrostic_keyword.rail', num_reasks=1)

        acrostic = {}
        raw_llm_output, validated_output = acrostic_guard(
            openai.Completion.create,
            prompt_params={"text": text},
            engine=model,
            max_tokens=1024,
            temperature=0.3,
        )

        for letter in validated_output['acrostic']:
            letter.upper()
            acrostic[letter] = ""
            if not letter == " ":
                acrostic_line_guard = gd.Guard.from_rail('./card-rails/acrostic_line.rail', num_reasks=1)
                raw_llm_output, acrostic_line = acrostic_line_guard(
                    openai.Completion.create,
                    prompt_params={"text": text, "letter": letter},
                    engine=model,
                    max_tokens=1024,
                    temperature=0.3,
                )
                acrostic[letter] = acrostic_line

        return acrostic
    elif card_type == "mcq":
        mcq_guard = gd.Guard.from_rail('./card-rails/multiple_choice_cards.rail', num_reasks=1)

        raw_llm_output, validated_output = mcq_guard(
            openai.Completion.create,
            prompt_params={"text": text},
            engine=model,
            max_tokens=1024,
            temperature=0.3,
        )
        return validated_output
    elif card_type == "rhyme":
        rhyme_guard = gd.Guard.from_rail('./card-rails/rhyme.rail', num_reasks=1)

        raw_llm_output, validated_output = rhyme_guard(
            openai.Completion.create,
            prompt_params={"text": text},
            engine=model,
            max_tokens=1024,
            temperature=0.3,
        )
        return validated_output
    else:
        return "failed to get flashcards from model"


def addCards(origin, input, card_type, card_front, card_back, status="new", owner="Joseph" ):
    try: 
        conn = postgreSQL_pool.getconn()
        cur=conn.cursor()

        add_cards_sql = "INSERT INTO flashcards (origin, input, card_type, card_front, card_back, status, owner) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;"
        add_cards_query = (origin, input, card_type, card_front, card_back, status, owner)
        cur.execute(add_cards_sql, add_cards_query)

        conn.commit()
        cur.close()
        postgreSQL_pool.putconn(conn)

        return jsonify({"msg": "saved cards!"})
    except (Exception, psycopg2.Error) as error:
        print("Error in insert operation", error)
        return jsonify({"msg": "couldn't save cards! :\'("})
    
def getDueCards(n=10):
    try:
        conn = postgreSQL_pool.getconn()
        cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        get_due_cards_sql = "SELECT * FROM flashcards WHERE due = current_date ORDER BY due;"  
        cur.execute(get_due_cards_sql, n)
        records = cur.fetchall()

        if len(records) == 0:
            return jsonify({"msg": "no cards due today!"})
        due_cards = []
        for row in records:
            due_cards.append(dict(row))
 
        conn.commit()
        cur.close()
        postgreSQL_pool.putconn(conn)

        return due_cards
    except (Exception, psycopg2.Error) as error:
        print("Error in select operation", error)
        return jsonify({"msg": "error getting cards from db :\'("})
    

def updateCard(id):
    try:
        conn = postgreSQL_pool.getconn()
        cur=conn.cursor()
  
        get_card_ease_sql = "SELECT ease FROM flashcards WHERE id = (%s)"
        cur.execute(get_card_ease_sql, [id])
        card_ease = cur.fetchone()[0]

        base_interval = 1
        next_interval = timedelta(base_interval * (card_ease / 100))
        next_due = datetime.now() + next_interval
        
        update_card_reviewed_sql = """UPDATE flashcards SET last_reviewed = CURRENT_TIMESTAMP WHERE id = %s;"""
        cur.execute(update_card_reviewed_sql, [id])
        
        update_card_due_sql = "UPDATE flashcards SET due = %s WHERE id = %s;"
        cur.execute(update_card_due_sql, [next_due, id])

        update_card_ease_sql = "UPDATE flashcards SET ease = ease * 2 WHERE id = %s RETURNING *;"
        cur.execute(update_card_ease_sql, [id])

        record = cur.fetchone()[0]

        conn.commit()
        cur.close()
        postgreSQL_pool.putconn(conn)

        return jsonify({"msg": "updated card!"})
    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
        return jsonify({"msg": "couldn't update card! :\'("})

def resetCard(id):
    try:
        conn = postgreSQL_pool.getconn()
        cur=conn.cursor()

        update_last_viewed_card_sql = "UPDATE flashcards SET last_reviewed = CURRENT_TIMESTAMP WHERE id = %s;"  
        cur.execute(update_last_viewed_card_sql, [id])

        reset_ease_sql = "UPDATE flashcards SET ease = 100 WHERE id = %s;"
        cur.execute(reset_ease_sql, [id])

        reset_due_date_sql = "UPDATE flashcards SET due = CURRENT_TIMESTAMP + INTERVAL '1 DAY' WHERE id = %s RETURNING *;"
        cur.execute(reset_due_date_sql, [id])

        record = cur.fetchone()[0]

        conn.commit()
        cur.close()
        postgreSQL_pool.putconn(conn)

        return jsonify({"msg": "updated card!"})
    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
        return jsonify({"msg": "couldn't update card! :\'("})
   

def deleteCard(card_to_delete_id):
    try:
        conn = postgreSQL_pool.getconn()
        cur=conn.cursor()

        delete_card_sql = "DELETE FROM flashcards WHERE id = %s; RETURNING id;"  
        cur.execute(delete_card_sql, card_to_delete_id)
        
        conn.commit()
        cur.close()
        postgreSQL_pool.putconn(conn)

        return jsonify({"msg": "deleted card!"})
    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
        return jsonify({"msg": "error deleting card from db! :\'("})