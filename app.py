from flask import *

import guardrails as gd
import openai
import os

os.environ["OPENAI_API_KEY"] = "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"
# other models include: text-davinci-002, text-curie-001, text-babbage-001, text-ada-001
# Should build in redundancy w/ other models in case one is down
openai.api_key = os.environ["OPENAI_API_KEY"]


app = Flask(__name__)

def getFlashcards(text, type="default", model="text-davinci-003"): 
    text = str(text)

    if type == "default":
        flashcard_guard = gd.Guard.from_rail('./card-rails/default_flashcards.rail', num_reasks=1)
        # print(str(model))
        raw_llm_output, validated_output = flashcard_guard(
            openai.Completion.create,
            prompt_params={"text": text},
            engine=model,
            max_tokens=1024,
            temperature=0.3,
        )

        return validated_output
    elif type == "acrostic":
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
    elif type == "mcq":
        mcq_guard = gd.Guard.from_rail('./card-rails/multiple_choice_cards.rail', num_reasks=1)

        raw_llm_output, validated_output = mcq_guard(
            openai.Completion.create,
            prompt_params={"text": text},
            engine=model,
            max_tokens=1024,
            temperature=0.3,
        )
        return validated_output


    elif type == "rhyme":
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
        return "couldn't get flashcards"



@app.route('/', methods=['GET'])
def hello():
    print('got request')
    return jsonify({"msg": "hello flashcards!"})

@app.route('/flashcards', methods=['POST'])
def flashcards():
    print('got request')

    text = request.json['text']
    type = request.json['type']
    
    cards = getFlashcards(str(text), str(type))
    print(cards)
    return jsonify(cards)

@app.route('/new_cards', methods=['POST'])
def new_cards():
    print('recieved cards')

    new_cards = request.json['new_cards']

    print(new_cards)
    return( jsonify({"msg": "got cards!"}))
