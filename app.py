from flask import *

import guardrails as gd
import openai
import os

os.environ["OPENAI_API_KEY"] = "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"


app = Flask(__name__)

def getFlashcards(text, type="default"):

    if type == "default":
        flashcard_guard = gd.Guard.from_rail('default_flashcards.rail', num_reasks=1)

        raw_llm_output, validated_output = flashcard_guard(
            openai.Completion.create,
            prompt_params={"text": text},
            engine="text-davinci-003",
            max_tokens=1024,
            temperature=0.3,
        )
        return validated_output
    elif type == "acrostic":
        acrostic_guard = gd.Guard.from_rail('acrostic_keyword.rail', num_reasks=1)

        acrostic = {}

        raw_llm_output, validated_output = acrostic_guard(
            openai.Completion.create,
            prompt_params={"text": text},
            engine="text-davinci-003",
            max_tokens=1024,
            temperature=0.3,
        )

        for letter in validated_output['acrostic']:
            letter.upper()
            acrostic[letter] = ""
            if not letter == " ":
                acrostic_line_guard = gd.Guard.from_rail('acrostic_line.rail', num_reasks=1)
                raw_llm_output, acrostic_line = acrostic_line_guard(
                    openai.Completion.create,
                    prompt_params={"text": text, "letter": letter},
                    engine="text-davinci-003",
                    max_tokens=1024,
                    temperature=0.3,
                )
                acrostic[letter] = acrostic_line

        return acrostic
    elif type == "mcq":
        mcq_guard = gd.Guard.from_rail('multiple_choice_cards.rail', num_reasks=1)

        raw_llm_output, validated_output = mcq_guard(
            openai.Completion.create,
            prompt_params={"text": text},
            engine="text-davinci-003",
            max_tokens=1024,
            temperature=0.3,
        )
        return validated_output


    elif type == "rhyme":
        rhyme_guard = gd.Guard.from_rail('rhyme.rail', num_reasks=1)

        raw_llm_output, validated_output = rhyme_guard(
            openai.Completion.create,
            prompt_params={"text": text},
            engine="text-davinci-003",
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
    print(request.data)
    text = request.json['text']
    type = request.json['type']
    cards = getFlashcards(text, type)
    return jsonify(cards)