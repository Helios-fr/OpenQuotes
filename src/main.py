# External Imports
import sqlite3
import fastapi
import uvicorn
import datetime
import random
import os

with open('admin.secret', 'r') as f:
    admin_token = f.read().strip()

app = fastapi.FastAPI()
conn = sqlite3.connect('quotes.db', check_same_thread=False)
cursor = conn.cursor()

if not cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="quotes"').fetchone():
    cursor.execute('''CREATE TABLE quotes
                (id INTEGER PRIMARY KEY, author TEXT, content TEXT, date TEXT)''')
    cursor.execute('INSERT INTO quotes (author, content, date) VALUES ("Anonymous", "Hello, World!", "2021-01-01")')
    conn.commit()

# Create routers
general_router = fastapi.APIRouter()
admin_router = fastapi.APIRouter()

@general_router.get('/')
def Documentation():
    """
    Redirects to the API documentation
    """
    return fastapi.responses.RedirectResponse(url='/docs')

@general_router.get('/random')
def RandomQuote():
    """
    Returns a random quote from the database
    """
    with conn:
        cursor.execute('SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1')
        r = cursor.fetchone()
        
    return {'id': r[0], 'author': r[1], 'content': r[2], 'date': r[3]}

@general_router.get('/quote/{id}')
def GetQuote(id: int):
    """
    Returns a quote by its id
    """
    with conn:
        if not cursor.execute('SELECT * FROM quotes WHERE id=?', (id,)).fetchone():
            return fastapi.responses.JSONResponse(content={'error': 'Quote not found'}, status_code=404)

        cursor.execute('SELECT * FROM quotes WHERE id=?', (id,))
        r = cursor.fetchone()
        
    return {'id': r[0], 'author': r[1], 'content': r[2], 'date': r[3]}

@general_router.get('/all')
def AllQuotes():
    """
    Returns all quotes in the database
    """
    with conn:
        cursor.execute('SELECT * FROM quotes')
        r = cursor.fetchall()
        
    return [{'id': i[0], 'author': i[1], 'content': i[2], 'date': i[3]} for i in r]

@general_router.get('/search')
def SearchQuotes(author: str = None, content: str = None, date: str = None):
    """
    Returns quotes that match or are like the search criteria
    """
    with conn:
        if author:
            cursor.execute('SELECT * FROM quotes WHERE author like ?', (author,))
        elif content:
            cursor.execute('SELECT * FROM quotes WHERE content LIKE ?', (f'%{content}%',))
        elif date:
            cursor.execute('SELECT * FROM quotes WHERE date=?', (date,))
        else:
            return fastapi.responses.JSONResponse(content={'error': 'No search criteria provided'}, status_code=400)
        
        r = cursor.fetchall()
        
    return [{'id': i[0], 'author': i[1], 'content': i[2], 'date': i[3]} for i in r]

@general_router.get('/qotd')
def QuoteOfTheDay():
    """
    Returns the quote of the day using a random quote from the database found using the current date as the seed
    """
    random.seed(datetime.datetime.now().strftime('%Y-%m-%d'))
    with conn:
        cursor.execute('SELECT * FROM quotes')
        r = cursor.fetchall()
    
    qotd = random.choice(r)
    return {'id': qotd[0], 'author': qotd[1], 'content': qotd[2], 'date': qotd[3]}

@general_router.get('/stats')
def Stats():
    """
    Returns the number of quotes in the database, the number of unique authors, and the number of quotes by the top author
    """
    with conn:
        cursor.execute('SELECT COUNT(*) FROM quotes')
        num_quotes = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT author) FROM quotes')
        num_authors = cursor.fetchone()[0]
        
        cursor.execute('SELECT author, COUNT(*) FROM quotes GROUP BY author ORDER BY COUNT(*) DESC LIMIT 1')
        top_author = cursor.fetchone()

    return {'num_quotes': num_quotes, 'num_authors': num_authors, 'top_author': top_author}

@general_router.post('/add')
def AddQuote(author: str, content: str):
    """
    Adds a quote to the database
    """
    with conn:
        cursor.execute('INSERT INTO quotes (author, content, date) VALUES (?, ?, ?)', (author, content, datetime.datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        
    return {'author': author, 'content': content}

@admin_router.delete('/delete/{id}')
def DeleteQuote(id: int, admin_token: str):
    """
    Deletes a quote from the database by its id if the admin token is correct
    """
    if admin_token != 'admin':
        return fastapi.responses.JSONResponse(content={'error': 'Unauthorized'}, status_code=401)
    
    with conn:
        if not cursor.execute('SELECT * FROM quotes WHERE id=?', (id,)).fetchone():
            return fastapi.responses.JSONResponse(content={'error': 'Quote not found'}, status_code=404)
        
        cursor.execute('DELETE FROM quotes WHERE id=?', (id,))
        conn.commit()
        
    return {'id': id}

# Include routers in the app
app.include_router(general_router, tags=["General"])
app.include_router(admin_router, prefix="/admin", tags=["Administration"])