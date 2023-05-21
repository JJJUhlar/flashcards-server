from flask import *
from flashcards import getFlashcards, addCards, getDueCards, updateCard, deleteCard, resetCard
import os

app = Flask(__name__)

@app.route('/flashcards', methods=['POST'])
def flashcards():
    try:
        text = request.json['text']
        card_type = request.json['type']
        created_cards = getFlashcards(str(text), str(card_type))

        for card in created_cards['flashcards']:
            card['origin'] = request.json['url']
            card['input'] = text
            card['type'] = card_type

        return jsonify(created_cards)    
    except:
        return jsonify({"msg": "couldn't generate flashcards"})

@app.route('/save_cards', methods=['POST'])
def save_cards():
    try:
        created_cards = request.json['created_cards']
        for card in created_cards:
            addCards(card['origin'], card['input'], card['type'], card['front'], card['back'])

        return jsonify({"msg": "got cards!"})
    except: 
        return jsonify({"msg": "couldn't find flashcards"})

@app.route('/due_cards', methods=['GET'])
def due_cards():
    #get number of cards to review from request
    try:
        due_cards = getDueCards(10)
        return jsonify(due_cards)
    except:
        return jsonify({"msg": "couldn't get due cards"})
    
@app.route('/update_card', methods=['PATCH'])
def update_card():

    try:
        card_to_update_id = request.json['card_to_update_id']
        updateCard(card_to_update_id)
        return jsonify({"msg": "updated card!"})
    except: 
        return jsonify({"msg": "couldn't update cards"})
    
@app.route('/delete_card', methods=['DELETE'])
def delete_card():
    try:
        card_to_delete_id = request.json['card_to_delete_id']
        deleteCard(card_to_delete_id)
        return jsonify({"msg": "deleted card!"})
    except: 
        return jsonify({"msg": "couldn't delete card"})
    
@app.route('/reset_card', methods=['PATCH'])
def reset_card():
    try:
        card_to_reset_id = request.json['card_to_reset_id']
        resetCard(card_to_reset_id)
        return jsonify({"msg": "reset card!"})
    except: 
        return jsonify({"msg": "couldn't reset card"})