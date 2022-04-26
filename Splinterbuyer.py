from datetime import datetime
from enum import auto
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
currency = configfile["global_params"]["currency"]
auto_set_buy_price = configfile["global_params"]["auto_set_buy_price"]
buypct = configfile["global_params"]["buy_pct_below_market"]
sellpct = configfile["global_params"]["sell_pct_above_buy"]
tip_pct = configfile["global_params"]["tip_pct_of_profit"]
f.close()

hive = Hive(keys=active_key)
url_purchase = "https://steemmonsters.com/transactions/lookup?trx_id="
url_player_trx = "https://api2.splinterlands.com/market/history?player="
url_card_lookup = "https://steemmonsters.com/cards/find?ids="
url_settings = "https://steemmonsters.com/settings"
url_prices = "https://api.splinterlands.io/market/for_sale_grouped"
url_legs = "https://api.splinterlands.io/cards/get_details"
headers = {
    }

settings = json.loads(requests.request("GET", url_settings, headers=headers).text)
response = requests.request("GET", url_legs, headers=headers)
cardsjson = json.loads(str(response.text))

currently_buying = []
currently_selling = []

def calculate_bcx_from_card(card):
  alpha_bcx = 0
  alpha_dec = 0
  alpha_xp = 0
  if card["alpha_xp"] != None:
    alpha_xp = card["alpha_xp"]
  xp = max(card["xp"] - alpha_xp, 0)
  burn_rate = settings["dec"]["burn_rate"][card["details"]["rarity"] - 1]
  if card["edition"] == 4 or (card["details"]["tier"] != None and  card["details"]["tier"] >= 4):
    burn_rate = settings["dec"]["untamed_burn_rate"][card["details"]["rarity"] - 1]
  if (alpha_xp):
    alpha_bcx_xp = settings["alpha_xp"][card["details"]["rarity"] - 1]
    if card["gold"]:
      alpha_bcx_xp = settings["gold_xp"][card["details"]["rarity"] - 1]
    alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
    if card["gold"]:
      alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
    alpha_dec = burn_rate * alpha_bcx * settings["dec"]["alpha_burn_bonus"]
    if card["gold"]:
      alpha_dec *= settings["dec"]["gold_burn_bonus"]
  
  xp_property = "error"
  if card["edition"] == 0 or (card["edition"] == 2 and int(card["details"]["id"]) < 100):
    if card["gold"]:
      xp_property = "gold_xp"
    else:
      xp_property = "alpha_xp"
  else:
    if card["gold"]:
      xp_property = "beta_gold_xp"
    else:
      xp_property = "beta_xp"
  bcx_xp = settings[xp_property][card["details"]["rarity"] - 1]
  bcx = max((xp + bcx_xp) / bcx_xp, 1)
  if card["gold"]:
    bcx = max(xp / bcx_xp, 1)
  if card["edition"] == 4 or (card["details"]["tier"] != None and card["details"]["tier"] >= 4):
    bcx = card["xp"]
  if (alpha_xp):
      bcx = bcx - 1
  print(str(cardid) + ": " + str(bcx) + "bcx")
  return bcx

def calculate_bcx_from_cardID(cardid):
  print(url_card_lookup + str(cardid))
  response = requests.request("GET", url_card_lookup + str(cardid), headers=headers)
  card = json.loads(str(response.text))[0]
  return calculate_bcx_from_card(card)

def calc_cp_per_usd(cardid, price_usd):
  response = requests.request("GET", url_card_lookup + str(cardid), headers=headers)
  card = json.loads(str(response.text))[0]
  bcx = calculate_bcx_from_card(card)
  alpha_bcx = 0
  alpha_dec = 0
  alpha_xp = 0
  if card["alpha_xp"] != None:
    alpha_xp = card["alpha_xp"]
  xp = max(card["xp"] - alpha_xp, 0)
  burn_rate = settings["dec"]["burn_rate"][card["details"]["rarity"] - 1]
  if card["edition"] == 4 or (card["details"]["tier"] != None and  card["details"]["tier"] >= 4):
    burn_rate = settings["dec"]["untamed_burn_rate"][card["details"]["rarity"] - 1]
  if (alpha_xp):
    alpha_bcx_xp = settings["alpha_xp"][card["details"]["rarity"] - 1]
    if card["gold"]:
      alpha_bcx_xp = settings["gold_xp"][card["details"]["rarity"] - 1]
    alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
    if card["gold"]:
      alpha_bcx = max(alpha_xp / alpha_bcx_xp, 1)
    alpha_dec = burn_rate * alpha_bcx * settings["dec"]["alpha_burn_bonus"]
    if card["gold"]:
      alpha_dec *= settings["dec"]["gold_burn_bonus"]
  
  xp_property = "error"
  if card["edition"] == 0 or (card["edition"] == 2 and int(card["details"]["id"]) < 100):
    if card["gold"]:
      xp_property = "gold_xp"
    else:
      xp_property = "alpha_xp"
  else:
    if card["gold"]:
      xp_property = "beta_gold_xp"
    else:
      xp_property = "beta_xp"
  bcx_xp = settings[xp_property][card["details"]["rarity"] - 1]
  bcx = max((xp + bcx_xp) / bcx_xp, 1)
  if card["gold"]:
    bcx = max(xp / bcx_xp, 1)
  if card["edition"] == 4 or (card["details"]["tier"] != None and card["details"]["tier"] >= 4):
    bcx = card["xp"]
  if (alpha_xp):
      bcx = bcx - 1
  dec = burn_rate * bcx
  if (card["gold"]):
    gold_burn_bonus_prop = "gold_burn_bonus"
    if card["details"]["tier"] != None and card["details"]["tier"] >= 7:
      gold_burn_bonus_prop = "gold_burn_bonus_2"
    dec *= settings["dec"][gold_burn_bonus_prop]
  
  if (card["edition"] == 0):
      dec *= settings["dec"]["alpha_burn_bonus"]
  if (card["edition"] == 2):
      dec *= settings["dec"]["promo_burn_bonus"]
  total_dec = dec + alpha_dec
  #if (card.xp >= getMaxXp(details, card.edition, card.gold)):
   # total_dec *= SM.settings.dec.max_burn_bonus;
  if (card["details"]["tier"] != None and card["details"]["tier"] >= 7):
    total_dec = total_dec / 2;
  return total_dec / price_usd

def check_desired(listing, trx_id):
  price = float(listing["price"])
  cardid = str(listing["cards"])[5:-13]
  if str(listing["cards"])[4] != "-":
    print("unable to parse: " + str(listing["cards"])[2:-2] +  ", looking up cardid...")
    response = requests.request("GET", url_card_lookup + (str(listing["cards"])[2:-2]), headers=headers)
    card = json.loads(str(response.text))
    cardid = str(card[0]["card_detail_id"])
  if len(cardid) > 3:
    raise Exception("skipping card set...")
  for bid in bids:
    if ((float(bid["max_quantity"]) > 0) 
    and (cardid in bid["cards"]) 
    and (price <= float(bid["prices"][cardid])) 
    and (price <= float(bid["max_price"]))
    and ((not bid["gold_only"]) or (str(listing["cards"])[2] == "G"))
    and (bid["min_bcx"] == 0 or calculate_bcx_from_cardID(str(listing["cards"])[2:-2]) >= bid["min_bcx"])
    and (bid["min_cp_per_usd"] == 0 or calc_cp_per_usd(str(listing["cards"])[2:-2], price) >= bid["min_cp_per_usd"])):
          bid["max_quantity"] = bid["max_quantity"] - 1
          currently_buying.append({"id": trx_id, "bid_idx": bids.index(bid), "cardid": str(listing["cards"])[2:-2]})
          return True
  print(str(listing["cards"])[2] + "-" + cardid + " $" + str(price))
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
          logger.error("successfully bought card for: " + str(res["total_dec"]) + "DEC")
          logger.error(str(url_purchase) + str(txa["trx_id"]))
          for buy in currently_buying:
            if((str(buy["id"])) in buydata["items"]):
              logger.error("bought card " + str(buy["cardid"]) +  " for: " + str(res["total_usd"]) + "$")
              if auto_set_buy_price:
                new_price = float(res["total_usd"])  + (float(res["total_usd"]) * (sellpct / 100))
                jsondata = '{"cards":["' + str(buy["cardid"]) + '"],"currency":"USD","price":' + str(new_price) +',"fee_pct":500}'
                hive.custom_json('sm_sell_cards', json_data=jsondata, required_auths=[account_name])
                print("selling " + str(buy["cardid"]) + " for " + str(new_price) + "$")
                logger.error("selling " + str(buy["cardid"]) + " for " + str(new_price) + "$")
                currently_selling.append(str(buy["cardid"]))
              elif bids[buy["bid_idx"]]["sell_for_pct_more"] > 0:
                new_price = float(res["total_usd"])  + (float(res["total_usd"]) * (bids[buy["bid_idx"]]["sell_for_pct_more"] / 100))
                jsondata = '{"cards":["' + str(buy["cardid"]) + '"],"currency":"USD","price":' + str(new_price) +',"fee_pct":500}'
                hive.custom_json('sm_sell_cards', json_data=jsondata, required_auths=[account_name])
                print("selling " + str(buy["cardid"]) + " for " + str(new_price) + "$")
                logger.error("selling " + str(buy["cardid"]) + " for " + str(new_price) + "$")
                currently_selling.append(str(buy["cardid"]))
              print("############################")
              currently_buying.remove(buy)
        else:
          for buy in currently_buying:
            if((str(buy["id"])) in buydata["items"]):
              bids[buy["bid_idx"]]["max_quantity"] = bids[buy["bid_idx"]]["max_quantity"] + 1
              print("buy failed: " + str(data["trx_info"]["error"]))
              currently_buying.remove(buy)
      else:
        n -= 1
        time.sleep(1)

def check_for_sold():
  response = requests.request("GET", url_player_trx + str(account_name), headers=headers)
  history = json.loads(response.text)
  for entry in history:
    if entry["card_id"] in currently_selling and entry["type"] == "SELL":
      currently_selling.remove(entry["card_id"])
      logger.error("card " + str(entry["card_id"]) + "sold, sending " + str(tip_pct) + " tip")
      print("card " + str(entry["card_id"]) + "sold, sending " + str(tip_pct) + " tip")
      if tip_pct > 0:
        hive.custom_json('sm_token_transfer', json_data={"to":"derfabs","qty":float(entry["payment"][:-4]) * (tip_pct/100),"token":"DEC"}, required_auths=[account_name])

def check_prices():
  for bid in bids:
    bid["prices"] = {}
  if auto_set_buy_price:  
    logger.error("checking prices...")
    response = requests.request("GET", url_prices, headers=headers)
    cardsjson = json.loads(str(response.text))
    for bid in bids:
      for card in cardsjson:
        if str(card["card_detail_id"]) in bid["cards"] and card["gold"] == bid["gold_only"]:
          bid["prices"][str(card["card_detail_id"])] = (card["low_price"] * (1 - (buypct / 100)))
    return
  else:
    for cardid in bid["cards"]:
      bid["prices"][cardid] = bid["max_price"]
    return
  
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


check_prices()
last_checked = time.time()
blockchain = Blockchain(blockchain_instance=hive, mode="head")
stream = blockchain.stream()

for op in stream:
  if(time.time() - last_checked) > 600:
    print(time.time())
    print(last_checked)
    if auto_set_buy_price:
      check_prices()
    check_for_sold()
    last_checked = time.time()
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
              print(str(listing["cards"])[2] + "-" + cardid + " $" + str(price) + " - buying...")
      except Exception as e:
          print("error occured while checking cards: "  + repr(e))
    else:
      if(len(currently_buying) > 0 and account_name in op["required_auths"]):
        try:
          t = Thread(target = check_buying_result(op))
          t.start() 
        except Exception as e:
          print("error occured while buying: "  + repr(e))
