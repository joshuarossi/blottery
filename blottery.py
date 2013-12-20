__author__ = 'josh'

from pymongo import MongoClient
from txwatcher import TxWatcher
# import thread

client = MongoClient('localhost', 3002)
db = client.meteor
data = db.data

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
