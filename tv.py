import json
import random
import re
import string
from datetime import datetime
import requests
from websocket import create_connection
import logging
import pymongo
conn = pymongo.MongoClient("mongodb://localhost:27017/")
nuovodb = conn["goldapi"]
colle = nuovodb["xau"]


logging.basicConfig(filename="/root/api_gold/stat_tv.log", level=logging.INFO)




def search(query, type):
    res = requests.get(
        f"https://symbol-search.tradingview.com/symbol_search/?text={query}&provider_id={type}"
    )
    if res.status_code == 200:
        res = res.json()
        assert len(res) != 0, "Nothing Found."
        return res[0]
    else:
        print("Network Error!")
        exit(1)


def generateSession():
    stringLength = 12
    letters = string.ascii_lowercase
    random_string = "".join(random.choice(letters) for i in range(stringLength))
    return "qs_" + random_string


def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st


def constructMessage(func, paramList):
    return json.dumps({"m": func, "p": paramList}, separators=(",", ":"))


def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))


def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))


def sendPingPacket(ws, result):
    pingStr = re.findall(".......(.*)", result)
    if len(pingStr) != 0:
        pingStr = pingStr[0]
        ws.send("~m~" + str(len(pingStr)) + "~m~" + pingStr)


def socketJob(ws):
    logging.info(f"Start socket job: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    while True:
        try:
            result = ws.recv()
            if "quote_completed" in result or "session_id" in result:
                continue
            # pattern = r"^.*?({.*)$"
            # print(result)
            pattern = pattern = r"~m~\d+~m~({\"m\":\"qsd\",\"p\":\[.*?\]})"
            matches = re.findall(pattern, result, flags=re.DOTALL)
            dato = ''
            if len(matches) > 0:
                
                for match in matches:
                    dato = match
                # if match:
                
                jsonRes = json.loads(dato)
                
                if jsonRes["m"] == "qsd":
                    symbol = jsonRes["p"][1]["n"]
                    price = jsonRes["p"][1]["v"]["lp"]
                    # print(f"{symbol.split(':')[1]}: {price:.4f}")
                    record = {'symbol': symbol.split(':')[1], 'price': format(price, '.4f'), 'time': datetime.timestamp(datetime.now()), 'ora': datetime.now().strftime("%H:%M:%S")}
                    # record = {'symbol': symbol.split(':')[1], 'price': format(price, '.4f'), 'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}
                    print(record)
                    try:
                        filter = {"symbol": symbol.split(':')[1]}
                        total_rows = colle.count_documents(filter)

                        if total_rows >= 5:
                            oldest_rows = colle.find(filter).sort("time", pymongo.ASCENDING).limit(total_rows - 4)
                            oldest_ids = [row["_id"] for row in oldest_rows]
                            colle.delete_many({"_id": {"$in": oldest_ids}})

                        colle.insert_one(record)
                    except Exception as e:
                        print(e)
                

                    
            else:
                # ping packet
                sendPingPacket(ws, result)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit(0)
        except Exception as e:
            print(f"ERROR: {e}\nTradingView message: {result}")
            logging.error(f"ERROR: {e}\nTradingView message: {result} {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
            if "was lost." in str(e):
                print("Reconnecting...")
                main(symbol.split(':')[1], 'bitstamp')
                continue


def getSymbolId(pair, market):
    data = search(pair, market)
    symbol_name = data["symbol"]
    try:
        broker = data["prefix"]
    except KeyError:
        broker = data["exchange"]
    symbol_id = f"{broker.upper()}:{symbol_name.upper()}"
    return symbol_id

def connectdb():
    try:
        conn = pymongo.MongoClient("mongodb://localhost:27017/")
        if 'goldapi' in conn.list_database_names():
            print("Database exists!")
            logging.info(f"Database exists: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        else:
            insert = colle.insert_one({})
            delete_insert = colle.delete_one({"_id": insert.inserted_id})
            print("Collection created!")
            logging.info(f"Collection created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    except Exception as e:
        print(e)

def main(pair, market):
    # check if mongodb is running
    
    connectdb()

    # serach btcusdt from crypto category
    symbol_id = getSymbolId(pair, market)

    # create tunnel
    tradingViewSocket = "wss://data.tradingview.com/socket.io/websocket"
    headers = json.dumps({"Origin": "https://data.tradingview.com"})
    ws = create_connection(tradingViewSocket, headers=headers)
    session = generateSession()

    # Send messages
    sendMessage(ws, "quote_create_session", [session])
    sendMessage(ws, "quote_set_fields", [session, "lp"])
    sendMessage(ws, "quote_add_symbols", [session, symbol_id])

    # Start job
    socketJob(ws)
    logging.info(f"End socket job: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")

if __name__ == "__main__":
    pair = "XAUEUR"
    market = "bitstamp"
    main(pair, market)
    
# 