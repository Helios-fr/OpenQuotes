import sqlite3

def initialise_db():
    conn = sqlite3.connect('quotes.db', check_same_thread=False)
    c = conn.cursor()

    if not c.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="quotes"').fetchone():
        c.execute('''CREATE TABLE quotes
                    (id INTEGER PRIMARY KEY, author TEXT, content TEXT, date TEXT)''')
        c.execute('INSERT INTO quotes (author, content, date) VALUES ("Anonymous", "Hello, World!", "2021-01-01")')
        conn.commit()
    
    return conn

def getRandom(conn):
    c = conn.cursor()
    c.execute('SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1')
    # format the result as a dictionary
    data = c.fetchone()
    return {
        'id': data[0],
        'author': data[1],
        'content': data[2],
        'date': data[3]
    }