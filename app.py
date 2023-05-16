from flask import *
from flashcards import getFlashcards, addCards, getDueCards
import os


# other models include: text-davinci-002, text-curie-001, text-babbage-001, text-ada-001
# Should build in redundancy w/ other models in case one is down

app = Flask(__name__)

@app.route('/',methods=['GET'])
def hello():
    print('got request')
    return jsonify({"msg": "hello flashcards!"})

@app.route('/flashcards', methods=['POST'])
def flashcards():
    print('got request')
    try:
        text = request.json['text']
        cardType = request.json['type']
        cards = getFlashcards(str(text), str(type))
        print(cards)

        for card in cards['flashcards']:
            print(card, "<<<<")
            card['origin'] = request.json['url']
            card['input'] = text
            card['type'] = cardType

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

        return( jsonify({"msg": "got cards!"}))
    except: 
        return jsonify({"msg": "couldn't find flashcards"})
    
@app.route('/due_cards', methods=['GET'])
def due_cards():
    try:
        due_cards = getDueCards()
        return jsonify({"flashcards": due_cards})
    except:
        return jsonify({"msg": "couldn't get due cards"})