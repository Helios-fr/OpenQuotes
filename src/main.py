# External Imports
import sqlite3
import fastapi
import uvicorn

# Internal Imports import from the adjacent file .functions.py
from functions import *

app = fastapi.FastAPI()
conn = initialise_db()

@app.get('/')
def statistics():
    '''
    This route returns simple statistics about the database.
    '''
    with conn:
        return getStatistics(conn)

@app.get('/random')
def random():
    '''
    This route returns a random quote from the database.
    '''
    with conn:
        return getRandom(conn)

@app.post('/add')
def add(author: str, content: str, date: str):
    '''
    This route adds a new quote to the database.
    '''
    with conn:
        validation = validateQuote(conn, author, content, date)
        if validation[0] == True:
            addQuote(conn, author, content, date)
        else:
            return {'status': 'error', 'message': validation[1]}
        return {'status': 'success'}

# run the app
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

