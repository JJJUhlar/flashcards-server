from flask import *
from flashcards import getFlashcards, addCards, getDueCards
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
        print(new_cards)
        for card in new_cards:
            print(card)
            try:
                addCards(card['origin'], card['input'], card['type'], card['card_front'], card['card_back'])
            except:
                print('error saving card:', card)

        return jsonify({"msg": "got cards!"})
    except: 
        return jsonify({"msg": "couldn't find flashcards"})

@app.route('/due_cards', methods=['GET'])
def due_cards():
    try:
        due_cards = getDueCards()
        return jsonify({"due_cards": due_cards})
    except:
        return jsonify({"msg": "couldn't get due cards"})