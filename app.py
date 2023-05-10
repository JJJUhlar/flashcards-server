from flask import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    return 'Hello World!'

@app.route('/flashcards', methods=['POST'])
def flashcards():
    return 'Flashcards!'