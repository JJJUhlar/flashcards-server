from flask import *
from flashcards import getFlashcards, addCards, getDueCards, updateCard, deleteCard
import os

app = Flask(__name__)

@app.route('/',methods=['GET'])
def hello():
    print('got request')
    return jsonify({"msg": "hello flashcards!"})

@app.route('/flashcards', methods=['POST'])
def flashcards():
    try:
        text = request.json['text']
        card_type = request.json['type']
        cards = getFlashcards(str(text), str(card_type))
        print(cards)

        for card in cards['flashcards']:
            print(card, "<<card<<")
            card['origin'] = request.json['url']
            card['input'] = text
            card['type'] = card_type

        return jsonify(cards)    
    except:
        return jsonify({"msg": "couldn't get flashcards"})

@app.route('/save_cards', methods=['POST'])
def save_cards():
    try:
        new_cards = request.json['flashcards']
        print('recieved cards')
        for card in new_cards:
            
            try:
                addCards(card['origin'], card['input'], card['type'], card['front'], card['back'])
            except:
                print('error saving card:', card)

        return jsonify({"msg": "got cards!"})
    except: 
        return jsonify({"msg": "couldn't find flashcards"})

@app.route('/due_cards', methods=['GET'])
def due_cards():
    #get number of cards to review from request
    try:
        due_cards = getDueCards(10)
        return jsonify({"due_cards": due_cards})
    except:
        return jsonify({"msg": "couldn't get due cards"})
    
@app.route('/update_cards', methods=['PATCH'])
def update_cards():
    try:
        cards_to_update = request.json['cards_to_update']
        print('recieved cards_to_update')
        print(cards_to_update)
        for card in cards_to_update:
            print(card)
            try:
                updateCard(card['id'])
            except:
                print('error updating card:', card)

        return jsonify({"msg": "updated cards!"})
    except: 
        return jsonify({"msg": "couldn't update cards"})
    
@app.route('/delete_card', methods=['DELETE'])
def delete_card():
    try:
        card_to_delete_id = request.json['card_to_delete_id']
        print('recieved card_to_delete')
        deleteCard(card_to_delete_id)
        return jsonify({"msg": "deleted card!"})
    except: 
        return jsonify({"msg": "couldn't delete card"})