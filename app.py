from flask import *
import os
from dotenv import load_dotenv

instance = os.environ.get('FLASK_ENV')
load_dotenv(f"./.env.{instance}")

from config.testing_config import TestingConfig
from config.production_config import ProductionConfig
from config.development_config import DevelopmentConfig

app = Flask(__name__)
if instance == 'testing':
    app.config.from_object(TestingConfig)
elif instance == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

print("instance: ", instance)
print(load_dotenv(f"./.env.{instance}"))
print(app.config)

from database import init_connection_pool
init_connection_pool()
from models.flashcards import getFlashcards, addCards, getDueCards, updateCard, deleteCard, resetCard
from models.users import generate_auth_token, check_password, authenticate_token, get_user_id


# print(FLASK_ENV)

@app.route('/api/flashcards', methods=['POST'])
@authenticate_token
def flashcards():
    data = request.json

    input_text = data['text']

    try:
        created_cards = getFlashcards(input_text)
        if created_cards == "error getting flashcards from model":
            return jsonify({"msg": "couldn't generate flashcards"})
        elif created_cards:
            for card in created_cards[1]['flashcards']:
                card['origin'] = data['origin']
                card['input'] = data['text']
                card['card_back'] = card['back']
                card['card_front'] = card['front']
                card['card_type'] = "default"
                del card['front']
                del card['back']

        print(created_cards)
        return jsonify(created_cards[1])    
    except Exception as e:
        print(e)
        return jsonify({"msg": "couldn't generate flashcards"})


@app.route('/api/save_cards', methods=['POST'])
@authenticate_token
def save_cards():

    try:
        created_cards = request.json['created_cards']
        username = request.json['username']
        print(username)
        print(created_cards)
        for card in created_cards:
            addCards(card['url'], card['input'], card['type'], card['card_front'], card['card_back'], owner = username)

        return jsonify({"msg": "saved cards!"})
    except: 
        return jsonify({"msg": "couldn't save flashcards"})


@app.route('/api/due_cards', methods=['GET'])
@authenticate_token
def due_cards():
    #get number of cards to review from request
    data = request.args
    username = data['username']

    try:
        due_cards = getDueCards(username, 10)
        return jsonify(due_cards)
    except:
        return jsonify({"msg": "couldn't get due cards"})
    

@app.route('/api/update_card', methods=['PATCH'])
@authenticate_token
def update_card():
    data = request.json
    try:
        card_to_update_id = data['card_to_update_id']
        updateCard(card_to_update_id)
        return jsonify({"msg": "updated card!"})
    except: 
        return jsonify({"msg": "couldn't update cards"})
    

@app.route('/api/delete_card', methods=['DELETE'])
@authenticate_token
def delete_card():
    try:
        card_to_delete_id = request.json['card_to_delete_id']
        deleteCard(card_to_delete_id)
        return jsonify({"msg": "deleted card!"})
    except: 
        return jsonify({"msg": "couldn't delete card"})
    

@app.route('/api/reset_card', methods=['PATCH'])
@authenticate_token
def reset_card():
    try:
        card_to_reset_id = request.json['card_to_reset_id']
        resetCard(card_to_reset_id)
        return jsonify({"msg": "reset card!"})
    except:
        return jsonify({"msg": "couldn't reset card"})
    

@app.route('/api/login', methods=['POST'])
def login():

    data = request.json
    user = data['user']

    if user:
        token = generate_auth_token(user)
        return jsonify({"msg": "Login successful!", 'sessionToken': token, 'username': user})
    else:
        abort(401, description="No user provided")