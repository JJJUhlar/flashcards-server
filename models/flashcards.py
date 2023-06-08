import guardrails as gd
import openai
import os 
import psycopg2
import psycopg2.extras
from flask import jsonify
from datetime import datetime;
from datetime import timedelta;
from database import connection_pool
from rich import print
import json

openai.api_key = os.environ.get("OPENAI_API_KEY")

def getFlashcards(input_text, card_type="default", model="text-davinci-003"): 
    input_text = str(input_text)
    print("input text: ", input_text)
    print("key: ", openai.api_key)
    json.dumps(input_text)
    input_params = {"text": input_text}
    if card_type == "default":
        flashcard_guard = gd.Guard.from_rail('card-rails/default_flashcards.rail', num_reasks=1)
        
        try:
            validated_output = flashcard_guard(
                openai.Completion.create,
                prompt_params= dict(input_params),
                engine=model,
                max_tokens=1024,
                temperature=0.3,
            )
            print(flashcard_guard.state.most_recent_call.tree)
            return validated_output
        except Exception as e:
            print(flashcard_guard.state.most_recent_call)
            print('error getting cards: ', e)
            return "error getting flashcards from model"

    elif card_type == "acrostic":
        acrostic_guard = gd.Guard.from_rail('./card-rails/acrostic_keyword.rail', num_reasks=1)

        acrostic = {}
        raw_llm_output, validated_output = acrostic_guard(
            openai.Completion.create,
            prompt_params={"text": input_text},
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
                    prompt_params={"text": input_text, "letter": letter},
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
            prompt_params={"text": input_text},
            engine=model,
            max_tokens=1024,
            temperature=0.3,
        )
        return validated_output
    
    elif card_type == "rhyme":
        rhyme_guard = gd.Guard.from_rail('./card-rails/rhyme.rail', num_reasks=1)

        raw_llm_output, validated_output = rhyme_guard(
            openai.Completion.create,
            prompt_params={"text": input_text},
            engine=model,
            max_tokens=1024,
            temperature=0.3,
        )
        return validated_output
    
    else:
        return "failed to get flashcards from model"

def addCards(origin, input, card_type, card_front, card_back, status="new", owner="Joseph" ):
    conn = connection_pool.getconn()
    cur=conn.cursor()

    try: 
        add_cards_sql = "INSERT INTO flashcards (origin, input, card_type, card_front, card_back, status, owner) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;"
        add_cards_query = (origin, input, card_type, card_front, card_back, status, owner)
        cur.execute(add_cards_sql, add_cards_query)

        return jsonify({"msg": "saved cards!"})
    except (Exception, psycopg2.Error) as error:
        print("Error in insert operation", error)
        return jsonify({"msg": "couldn't insert cards! :\'("})
    finally:
        conn.commit()
        cur.close()
        connection_pool.putconn(conn)

def getDueCards(username, n=10):
    conn = connection_pool.getconn()
    cur=conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    try:
        get_due_cards_sql = "SELECT * FROM flashcards WHERE due <= current_date AND owner = (%s) ORDER BY due;"  
        cur.execute(get_due_cards_sql, (username,))
        records = cur.fetchall()
        
        if len(records) == 0:
            return jsonify({"msg": "no cards due today!"})
        due_cards = []
        for row in records:
            due_cards.append(dict(row))
        
        return due_cards
    except (Exception, psycopg2.Error) as error:
        print("Error in select operation", error)
        return jsonify({"msg": "error getting cards from db :\'("})
    
    finally:
        conn.commit()
        cur.close()
        connection_pool.putconn(conn)

def updateCard(id):
    conn = connection_pool.getconn()
    cur=conn.cursor()
    
    try:
        get_card_ease_sql = "SELECT ease FROM flashcards WHERE id = (%s)"
        cur.execute(get_card_ease_sql, [id])
        card_ease = cur.fetchone()[0]

        base_interval = 1
        next_interval = timedelta(base_interval * (card_ease / 100))
        next_due = datetime.now() + next_interval
        print("card is next due at: ", next_due)
        
        update_card_reviewed_sql = """UPDATE flashcards SET last_reviewed = CURRENT_TIMESTAMP WHERE id = %s;"""
        cur.execute(update_card_reviewed_sql, [id])
        
        update_card_due_sql = "UPDATE flashcards SET due = %s WHERE id = %s;"
        cur.execute(update_card_due_sql, [next_due, id])

        update_card_ease_sql = "UPDATE flashcards SET ease = ease * 2 WHERE id = %s RETURNING *;"
        cur.execute(update_card_ease_sql, [id])

        record = cur.fetchone()[0]

        return jsonify({"msg": "updated card!"})
    
    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
        return jsonify({"msg": "couldn't update card! :\'("})
    
    finally:
        conn.commit()
        cur.close()
        connection_pool.putconn(conn)

def resetCard(id):
    conn = connection_pool.getconn()
    cur=conn.cursor()
    
    try:
        update_last_viewed_card_sql = "UPDATE flashcards SET last_reviewed = CURRENT_TIMESTAMP WHERE id = %s;"  
        cur.execute(update_last_viewed_card_sql, [id])

        reset_ease_sql = "UPDATE flashcards SET ease = 100 WHERE id = %s;"
        cur.execute(reset_ease_sql, [id])

        reset_due_date_sql = "UPDATE flashcards SET due = CURRENT_TIMESTAMP + INTERVAL '1 DAY' WHERE id = %s RETURNING *;"
        cur.execute(reset_due_date_sql, [id])

        return jsonify({"msg": "updated card!"})
    
    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
        return jsonify({"msg": "couldn't update card! :\'("})
    
    finally:
        conn.commit()
        cur.close()
        connection_pool.putconn(conn)


def deleteCard(card_to_delete_id):
    conn = connection_pool.getconn()
    cur=conn.cursor()

    try:
        delete_card_sql = "DELETE FROM flashcards WHERE id = %s; RETURNING id;"  
        cur.execute(delete_card_sql, card_to_delete_id)

        return jsonify({"msg": "deleted card!"})
    except (Exception, psycopg2.Error) as error:
        print("Error in update operation", error)
        return jsonify({"msg": "error deleting card from db! :\'("})

    finally:
        conn.commit()
        cur.close()
        connection_pool.putconn(conn)