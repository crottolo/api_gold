from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
import requests
import json
import logging
import datetime
import dbm
logging.basicConfig(filename="call_post.log", level=logging.INFO)

app = FastAPI()

@app.get("/")
async def index():
    logging.info(f"Creato richiesta: + {datetime.datetime.now()}")
    
    
    
    data = dbm.print_db()
    data = json.dumps(data)
    return {}
