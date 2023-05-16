import guardrails as gd
import openai
import os 
import psycopg2
from psycopg2 import pool
from flask import jsonify

postgreSQL_pool = psycopg2.pool.SimpleConnectionPool(1, 20, user=os.environ['DBUSER'],
                                                         password=os.environ['DBPASS'],
                                                         host=os.environ['DBHOST'],
                                                         database=os.environ['DATABASE'])

openai.api_key = os.environ["OPENAI_API_KEY"]

def getFlashcards(text, card_type="default", model="text-davinci-003"): 
    text = str(text)
    print('getting cards', openai.api_key)

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


def addCards(origin, input, card_type, card_front, card_back, status="new", owner="joseph" ):
    try: 
        conn = postgreSQL_pool.getconn()

        cur=conn.cursor()

        cur.execute("INSERT INTO flashcards (origin, input, card_type, card_front, card_back, status, owner)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (origin,
                input,
                card_type,
                card_front,
                card_back,
                status,
                owner)
                )
        
        conn.commit()
        cur.close()
        postgreSQL_pool.putconn(conn)

        return jsonify({"msg": "saved cards!"})
    except:
        return jsonify({"msg": "couldn't save cards! :\'("})
    
def getDueCards():
    try:

        conn = postgreSQL_pool.getconn()

        cur=conn.cursor()

        due_cards = cur.execute("SELECT * FROM flashcards;")
        
        print(due_cards, "<<<<")
        conn.commit()
        cur.close()
        postgreSQL_pool.putconn(conn)

    

        return jsonify({"due_cards": due_cards})
    except:
        return jsonify({"msg": "couldn't save cards! :\'("})