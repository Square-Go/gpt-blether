from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import uuid
import json
import openai
import os


class Message:

    def __init__(self, user_name: str, content: str, hidden: bool):
        self.user_name = user_name
        self.content = content
        self.hidden = hidden

    def to_gpt_request_style(self):
        return {"role": self.user_name, "content": self.content}

app = Flask(__name__)

with open('config.json', 'r') as f:
    user_settings = json.load(f)
assert "gpt_model" in user_settings
assert "openaikey" in user_settings
assert "bot_description" in user_settings
assert "bot_greeting" in user_settings
assert "bot_name" in user_settings
assert "logo_file" in user_settings

bot_description = user_settings["bot_description"]
bot_greeting = user_settings["bot_greeting"]
bot_name = user_settings["bot_name"]
logo_file = user_settings["logo_file"]
openai.api_key = user_settings["openaikey"]


db_name = f"{bot_name}_messages.db"
print("Setting up Database.")
with sqlite3.connect(db_name) as conn:
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS messages''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                convo_id TEXT NOT NULL, 
                user_name TEXT,
                content TEXT,
                hidden BOOLEAN DEFAULT 0)''')
    conn.commit()

print("Database Ready.")

def validate_convo_id(convo_id) -> bool:
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM messages WHERE convo_id=?", (convo_id,))
        result = c.fetchone()[0]
        
        return result > 0


def get_initial_system_description():
    return Message("system", bot_description, hidden=True)

def get_initial_system_message():
    return Message("assistant", content=bot_greeting, hidden=False)

def invoke_gpt(messages):

    converted = [get_initial_system_description()]
    converted.extend(messages)
    converted = [x.to_gpt_request_style() for x in converted]
    response = openai.ChatCompletion.create(
        model=user_settings["gpt_model"],
        messages=converted
    )
    #todo validate stop reason


    return Message(user_name="assistant", content=response['choices'][0]['message']['content'], hidden=False)

@app.route('/images/<filename>')
def images(filename):
    image_folder = os.path.join(app.root_path, 'images')
    return send_from_directory(image_folder, filename)


@app.route('/')
def hello():

    convo_id = None
    if "convo_id" not in request.args:
        convo_id = str(uuid.uuid4())
        messages = [get_initial_system_message()]
        add_message(convo_id=convo_id, message=messages[0])
    else: 
        convo_id = str(request.args.get("convo_id"))
        messages = get_messages(convo_id=convo_id)
        if messages is None or len(messages) == 0:
            return render_template('error.html', message="Woops, it looks like this convo no longer exists!")

    return render_template('index.html', messages=messages, convo_id=convo_id, bot_name=bot_name, logo_file=logo_file)

@app.route('/', methods=['POST'])
def submit_form():
    convo_id = str(request.form['convo_id'])
    
    if not validate_convo_id(convo_id=convo_id):
        return render_template('error.html', message="Woops, it looks like this convo no longer exists!")

    user_name = "user"
    content = request.form['content']
    message = Message(user_name=user_name, content=content, hidden=False)
    add_message(convo_id, message)
    all_messages = get_messages(convo_id=convo_id)
    next_message = invoke_gpt(all_messages)
    add_message(convo_id=convo_id, message=next_message)

    if (all_messages is None or len(all_messages) == 0):
        return render_template('error.html', message="Woops, it looks like this convo no longer exists!") 



    return redirect(url_for('hello', convo_id=convo_id))


def get_messages(convo_id: str):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute("SELECT user_name, content, hidden FROM messages where convo_id = ? ORDER BY id", (convo_id,))
        rows = c.fetchall()
        messages = []
        for row in rows:
            message = Message(*row)
            messages.append(message)
        return messages

def add_message(convo_id: str, message: Message):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO messages (convo_id, user_name, content, hidden) VALUES (?, ?, ?, ?)", (convo_id, message.user_name, message.content, message.hidden))
        conn.commit()