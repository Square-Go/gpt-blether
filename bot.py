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

class Bot:

    def __init__(self, json_object: dict):
        # assert all required fields are present and show error page if not
        assert "gpt_model" in json_object
        assert "bot_name" in json_object
        assert "bot_description" in json_object
        assert "bot_greeting" in json_object
        

        #load all self variables from json object
        self.gpt_model = json_object["gpt_model"]
        self.bot_name = json_object["bot_name"]
        self.bot_description = json_object["bot_description"]
        self.bot_greeting = json_object["bot_greeting"]
        if "logo_file" in json_object:
            self.logo_file = json_object["logo_file"]
        else:
            self.logo_file = "bot_logo.png"
        

app = Flask(__name__)

with open('config.json', 'r') as f:
    user_settings = json.load(f)


assert "openaikey" in user_settings
openai.api_key = user_settings["openaikey"]

assert "bots" in user_settings
bots = {}
for bot in user_settings["bots"]:
    bots[bot["bot_name"]] = Bot(bot)

assert len(bots) > 0
print (f"Loaded {len(bots)} bots: {', '.join([str(x.__dict__) for x in bots.values()])}")

db_name = f"bot_messages.db"
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


def get_initial_system_description(bot: Bot):
    return Message("system", bot.bot_description, hidden=True)

def get_initial_system_message(bot: Bot):
    return Message("assistant", content=bot.bot_greeting, hidden=False)

def invoke_gpt(bot: Bot, messages):

    converted = [get_initial_system_description(bot)]
    converted.extend(messages)
    converted = [x.to_gpt_request_style() for x in converted]
    response = openai.ChatCompletion.create(
        model=bot.gpt_model,
        messages=converted
    )
    #todo validate stop reason


    return Message(user_name="assistant", content=response['choices'][0]['message']['content'], hidden=False)

@app.route('/images/<filename>')
def images(filename):
    image_folder = os.path.join(app.root_path, 'images')
    return send_from_directory(image_folder, filename)


@app.route("/")
def index():
    return render_template('index.html', bots=bots.values(), main_logo_file="bot_logo.png")


@app.route('/convo/<bot_name>')
def convo(bot_name):

    if not bot_name in bots:
        return render_template('error.html', message=f"The bot {bot_name} does not exist!")

    bot = bots[bot_name]

    convo_id = None
    if "convo_id" not in request.args:
        convo_id = str(uuid.uuid4())
        messages = [get_initial_system_message(bot)]
        add_message(convo_id=convo_id, message=messages[0])
    else: 
        convo_id = str(request.args.get("convo_id"))
        messages = get_messages(convo_id=convo_id)
        if messages is None or len(messages) == 0:
            return render_template('error.html', message="Woops, it looks like this convo no longer exists!")

    return render_template('convo.html', messages=messages, convo_id=convo_id, bot=bot)

@app.route('/convo/<bot_name>', methods=['POST'])
def submit_form(bot_name):
    convo_id = str(request.form['convo_id'])
    bot = bots[str(bot_name)]
    if not validate_convo_id(convo_id=convo_id):
        return render_template('error.html', message="Woops, it looks like this convo no longer exists!")

    user_name = "user"
    content = request.form['content']
    message = Message(user_name=user_name, content=content, hidden=False)
    add_message(convo_id, message)
    all_messages = get_messages(convo_id=convo_id)
    next_message = invoke_gpt(bot, all_messages)
    add_message(convo_id=convo_id, message=next_message)

    if (all_messages is None or len(all_messages) == 0):
        return render_template('error.html', message="Woops, it looks like this convo no longer exists!") 



    return redirect(url_for('convo', bot_name=bot.bot_name, convo_id=convo_id))


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