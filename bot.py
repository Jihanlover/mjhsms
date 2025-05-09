from flask import Flask, request
import requests
import sqlite3

app = Flask(__name__)
BOT_TOKEN = '7899139063:AAHS0UDdzyqmwc15nRdGriy0dqBwk5PFw2Y'
ADMIN_ID = '6535058176'

# DB Setup
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)''')
c.execute('''CREATE TABLE IF NOT EXISTS numbers (num TEXT)''')
conn.commit()

def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=data)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        # Register user
        c.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (chat_id,))
        conn.commit()

        if text == '/start':
            send_message(chat_id, "Welcome to MJH SMS BOT!")

        elif text.startswith('/addnumber') and str(chat_id) == ADMIN_ID:
            number = text.replace('/addnumber', '').strip()
            if number:
                c.execute("INSERT INTO numbers (num) VALUES (?)", (number,))
                conn.commit()
                send_message(chat_id, f"Number '{number}' added.")
            else:
                send_message(chat_id, "Usage: /addnumber <number>")

        elif text == '/broadcast' and str(chat_id) == ADMIN_ID:
            c.execute("SELECT num FROM numbers ORDER BY ROWID DESC LIMIT 1")
            last = c.fetchone()
            if last:
                c.execute("SELECT id FROM users")
                for row in c.fetchall():
                    send_message(row[0], f"New Number: {last[0]}")
                send_message(chat_id, "Broadcast done.")
            else:
                send_message(chat_id, "No number found.")

    return {"ok": True}
