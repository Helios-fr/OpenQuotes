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

def getStatistics(conn):
    # returns a dictionary of the number of quotes in the database, the most recent quote, and the total of individual authors
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM quotes')
    total = c.fetchone()[0]
    c.execute('SELECT * FROM quotes ORDER BY date DESC LIMIT 1')
    latest = c.fetchone()
    c.execute('SELECT COUNT(DISTINCT author) FROM quotes')
    authors = c.fetchone()[0]
    return {
        'total': total,
        'latest': {
            'id': latest[0],
            'author': latest[1],
            'content': latest[2],
            'date': latest[3]
        },
        'authors': authors
    }

def validateQuote(conn, author, content, date):
    # check if the author, content, and date are not empty
    if not author or not content or not date:
        return (False, 'Author, content, and date must not be empty.')
    
    # check if the date is in the correct format
    if not date[4] == date[7] == '-':
        return (False, 'Date must be in the format YYYY-MM-DD.')

    # check if the author, content, and date are not too long
    if len(author) > 100 or len(content) > 1000 or len(date) > 10:
        return (False, 'Author, content, and date must not exceed 100, 1000, and 10 characters respectively.')
    
    # check if the quote is similar to an existing quote in the database by comparing the characterdiff between the content
    c = conn.cursor()
    c.execute('SELECT * FROM quotes')
    for row in c.fetchall():
        if characterDiff(content, row[2]) < 10:
            return (False, 'This quote is too similar to an existing quote.')

    return (True, 'Success')

def characterDiff(a, b):
    # returns the number of characters that are different between two strings
    return sum(1 for x, y in zip(a, b) if x != y)

def addQuote(conn, author, content, date):
    c = conn.cursor()
    c.execute('INSERT INTO quotes (author, content, date) VALUES (?, ?, ?)', (author, content, date))
    conn.commit()
    return True

