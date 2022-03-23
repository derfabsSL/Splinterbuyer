from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import os
from beem.blockchain import Blockchain
from beem import Hive
import json
import requests
import logging 
import time
from threading import Thread

colors = {
  "Red": "fire",
  "Blue": "water",
  "Green": "earth",
  "White": "life",
  "Black": "death",
  "Gold": "dragon",
  "Gray": "neutral"
}

rarities = {
  1: "common",
  2: "rare",
  3: "epic",
  4: "legendary"
}

editions = {
  "alpha": 0,
  "beta": 1,
  "promo": 2,
  "reward": 3,
  "untamed": 4,
  "dice": 5,
  "chaos": 7
}

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
Log_Format = "%(asctime)s - %(message)s"

logger = logging.getLogger()
filename = (f'transactions-{datetime.now():%Y-%m-%w}.log')
handler = TimedRotatingFileHandler(os.path.join(THIS_FOLDER, filename),  when='midnight')
formatter = logging.Formatter("%(asctime)s - %(message)s", "%Y-%m-%d:%H-%M-%S")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.error("starting...")

my_file = os.path.join(THIS_FOLDER, 'bids.json')
f = open(my_file)
configfile = json.load(f)
bids = configfile["bids"]
account_name = configfile["account"]["name"]
active_key = configfile["account"]["active_key"]
currency = configfile["account"]["currency"]
f.close()

hive = Hive(keys=active_key)
url_purchase = "https://steemmonsters.com/transactions/lookup?trx_id="
headers = {
    }

url_legs = "https://api.splinterlands.io/cards/get_details"
url_decprice = "https://steemmonsters.com/settings"
response = requests.request("GET", url_legs, headers=headers)
cardsjson = json.loads(str(response.text))

currently_buying = []

def check_desired(listing, trx_id):
  price = float(listing["price"])
  cardid = str(listing["cards"])[5:-13]
  if(len(cardid) > 5):
    raise Exception("Invalid CardID")
  print(str(listing["cards"])[2] + "-" + cardid + " $" + str(price))
  for bid in bids:
    if (float(bid["max_quantity"]) > 0 
    and cardid in bid["cards"] 
    and price <= float(bid["max_price"]) 
    and ((not bid["gold_only"]) or (str(listing["cards"])[2] == "G"))):
          bid["max_quantity"] = bid["max_quantity"] - 1
          print("buying, remaining quantity: " + str(bid["max_quantity"]))
          currently_buying.append({"id": trx_id, "bid_idx": bids.index(bid), "cardid": str(listing["cards"])[2:-2]})
          return True
  return False

def check_buying_result(txa):
  n = 3
  while n > 0:
      response = requests.request("GET", url_purchase + txa["trx_id"], headers=headers)
      data = json.loads(response.text)
      if "trx_info" in data:
        n = 0
        buydata = json.loads(data["trx_info"]["data"])
        if(data["trx_info"]["success"] == True):
          res = json.loads(data["trx_info"]["result"])
          print(url_purchase + txa["trx_id"])
          print("############################")
          print("successfully bought card for: " + str(res["total_dec"]) + "DEC")
          for buy in currently_buying:
            if((str(buy["id"])) in buydata["items"]):
              logger.error("bought card " + str(buy["cardid"]) +  " for: " + str(res["total_usd"]) + "$")
              if bids[buy["bid_idx"]]["sell_for_pct_more"] > 0:
                new_price = float(res["total_usd"])  + (float(res["total_usd"]) / float(bids[buy["bid_idx"]]["sell_for_pct_more"]))
                jsondata = '{"cards":["' + str(buy["cardid"]) + '"],"currency":"USD","price":' + str(new_price) +',"fee_pct":500}'
                hive.custom_json('sm_sell_cards', json_data=jsondata, required_auths=[account_name])
                logger.error("selling " + str(buy["cardid"]) + " for " + str(new_price) + "$")
                bids[buy["bid_idx"]]["sell_for_pct_more"]
              print("############################")
              currently_buying.remove(buy)
        else:
          for buy in currently_buying:
            if((str(buy["id"])) in buydata["items"]):
              bids[buy["bid_idx"]]["max_quantity"] = bids[buy["bid_idx"]]["max_quantity"] + 1
              print("buy failed, card already sold")
              currently_buying.remove(buy)
      else:
        n -= 1
        time.sleep(1)

for bid in bids:
  if(bid["exclude_cl"]):
    cards_tmp = [card for card in cardsjson if rarities[int(card["rarity"])] in bid["rarities"] 
    and colors[str(card["color"])] in bid["elements"] 
    and str(card["type"]).lower() in str(bid["types"]).lower() and int(card["id"]) < 330]
  else:
    cards_tmp = [card for card in cardsjson if rarities[int(card["rarity"])] in bid["rarities"]
    and colors[str(card["color"])] in bid["elements"]
    and str(card["type"]).lower() in str(bid["types"]).lower()]
  all_eds = []
  for ed in bid["editions"]:
    current_ed = [str(card["id"]) for card in cards_tmp if str(editions[str(ed)]) in card["editions"]]
    all_eds = all_eds + current_ed
  if len(bid["cards"]) == 0:
    bid["cards"] =  all_eds

blockchain = Blockchain(blockchain_instance=hive, mode="head")
stream = blockchain.stream()

for op in stream:
  if(op["type"] == 'custom_json'):
    if op["id"] == 'sm_sell_cards' and account_name not in op["required_auths"]:
      try:
        listings = []
        if(op["json"][:1] == '[' ):
          str_listings = op["json"].strip().replace(" ", "").replace("'", "")
          listings = json.loads(str_listings)
        else:
          listings.append(json.loads(op["json"]))
        for index, listing in enumerate(listings):
          if (check_desired(listing, op["trx_id"] + "-" + str(index)) == True):
              price = float(listing["price"])
              cardid = str(listing["cards"])[5:-13]
              id = op["trx_id"]
              jsondata_old = '{"items":["'+ str(id) + '-' + str(index) + '"], "price":' + str(price) +', "currency":"' + str(currency) + '"}'
              hive.custom_json('sm_market_purchase', json_data=jsondata_old, required_auths=[account_name])
      except Exception as e:
          print("error occured while checking cards: "  + repr(e))
    else:
      if(len(currently_buying) > 0 and account_name in op["required_auths"]):
        try:
          t = Thread(target = check_buying_result(op))
          t.start() 
        except Exception as e:
          print("error occured while buying: "  + repr(e))
