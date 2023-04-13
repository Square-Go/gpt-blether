from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import uuid


class Message:

    def __init__(self, user_name: str, content: str, hidden: bool):
        self.user_name = user_name
        self.content = content
        self.hidden = hidden

app = Flask(__name__)


db_name = f"{__name__}_messages.db"

with sqlite3.connect(db_name) as conn:
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS messages
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                convo_id TEXT NOT NULL, 
                user_name TEXT,
                content TEXT,
                BOOLEAN DEFAULT 0)''')
    c.commit()

def validate_convo_id(convo_id) -> bool:
    with sqlite3.connect(db_name) as conn:
        c.execute("SELECT COUNT(*) FROM messages WHERE convo_id=?", (convo_id,))
        result = c.fetchone()[0]
        
        return result > 0


def get_initial_system_prompt():
    return "You are roastbot, whatever the user says, you use elaborate metaphors to roast the shit out of them."

def get_initial_system_message():
    return Message("system", content="Hi there, who do we have here?", hidden=False)

def invoke_gpt(messages):



@app.route('/')
def hello():

    convo_id = None
    if "convo_id" not in request.args:
        convo_id = str(uuid.uuid4())
        messages = [get_initial_system_message()]
        add_message(convo_id=convo_id, message=messages[0])
    else: 
        convo_id = request.args.request.args.get("convo_id")
        messages = get_messages(convo_id=convo_id)
        if messages is None or len(messages) == 0:
            return render_template('error.html', message="Woops, it's an invalid convo!")
        


    messages = [Message(user_name="User", content="Hi there"), Message(user_name="System", content="Yo yo yo!")]

    return render_template('index.html', messages=messages)

@app.route('/', methods=['POST'])
def submit_form():
    convo_id = request.form['convo_id']
    
    if not validate_convo_id(convo_id=convo_id):
        return render_template('error.html', message="Woops, it's an invalid convo!")

    user_name = request.form['user_name']
    content = request.form['content']
    message = Message(user_name=user_name, content=content, hidden=False)
    add_message(convo_id, message)
    # todo speak to openAI
    all_messages = get_messages(convo_id=convo_id)

    if (all_messages is None or len(all_messages) == 0):
        return render_template('error.html', message="Woops, it's an invalid convo!") 



    return redirect(url_for('view_messages'), convo_id=convo_id)


def get_messages(convo_id: str):
    with sqlite3.connect(db_name) as conn:
        c = conn.cursor()
        c.execute("SELECT id, user_name, content, hidden FROM messages where convo_id = ?", (convo_id))
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