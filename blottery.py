__author__ = 'josh'

from pymongo import MongoClient
from txwatcher import TxWatcher
import thread
import requests
from time import sleep


client = MongoClient('localhost', 27017)
db = client.meteor
data = db.data


def ticker():
    while 1:
        try:
            rate = requests.get('https://www.bitstamp.net/api/ticker/').json()
            rate = rate['last']
            rate = float(rate)
            data.update({'name': 'bitstamp'}, {'$set': {'exchange_rate': rate}}, True)
            sleep(5)
        except:
            pass


thread.start_new_thread(ticker,())


def tx_handler(tx):
    address = tx['x']['out'][0]['addr']
    value = tx['x']['out'][0]['value']
    blogger_value = int(value * .75)
    jackpot_inc = int(value * .20)
    profit = int(value * .05)
    data.update({'bitcoin_address': address}, {"$inc": {"balance": blogger_value}})
    data.update({'name': "jackpot"}, {"$inc": {"balance": jackpot_inc}})
    data.update({'name': 'blottery'}, {"$inc": {"balance": profit}})
    print "Received transaction for {} at address {}".format(value, address)


monitor_addresses = []


for address in data.find({'bitcoin_address':{'$exists': True}},{'bitcoin_address': 1}):
    monitor_addresses.append(address['bitcoin_address'])


w = TxWatcher(monitor_addresses)
w.on_tx += tx_handler
w.run_forever()
# thread.start_new_thread(w.run_forever, ())
