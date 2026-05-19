from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import session

import uuid

from rag_engine import answer_question

from memory import init_db
from memory import save_message
from memory import get_conversation_history
from memory import clear_conversation

app = Flask(__name__)

app.secret_key = "super-secret-key"


init_db()


@app.before_request
def create_session_id():

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


@app.route('/api/chat', methods=['POST'])
def api_chat():

    data = request.get_json()

    question = data.get('question', '').strip()

    if question == '':
        return jsonify({
            'error': 'Question cannot be empty.'
        }), 400

    session_id = session["session_id"]

    history = get_conversation_history(session_id)

    save_message(session_id, "user", question)

    result = answer_question(
        question=question,
        conversation_history=history
    )

    answer = result['answer']

    save_message(session_id, "assistant", answer)

    return jsonify({
        'answer': answer,
        'retrieved_context': result['retrieved_context']
    })


@app.route('/api/clear', methods=['POST'])
def api_clear():

    session_id = session["session_id"]

    clear_conversation(session_id)

    return jsonify({
        'message': 'Conversation cleared.'
    })


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000, debug=True)