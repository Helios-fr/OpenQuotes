# External Imports
import sqlite3
import fastapi
import uvicorn

# Internal Imports import from the adjacent file .functions.py
from functions import initialise_db, getRandom

app = fastapi.FastAPI()
conn = initialise_db()

@app.get('/')
def read_root():
    '''
    This is the root of the API, it returns a random quote from the database.
    '''
    with conn:
        return getRandom(conn)

# run the app
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

