import os
from beem.blockchain import Blockchain
from beem import Hive
import json
import requests

# Opening JSON file
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_file = os.path.join(THIS_FOLDER, 'bids.json')
f = open(my_file)
configfile = json.load(f)
bids = configfile["bids"]
account_name = configfile["account"]["name"]
active_key = configfile["account"]["active_key"]
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
  print(str(listing["cards"])[2] + "-" + cardid + " $" + str(price))
  for bid in bids:
    if (float(bid["max_quantity"]) > 0 
    and cardid in bid["cards"] 
    and price <= float(bid["max_price"]) 
    and ((not bid["gold_only"]) or (str(listing["cards"])[2] == "G"))):
          bid["max_quantity"] = bid["max_quantity"] - 1
          print("buying, remaining quantity: " + str(bid["max_quantity"]))
          currently_buying.append({"id": trx_id, "bid_idx": bids.index(bid)})
          return True
  return False

for bid in bids:
  if(bid["exclude_cl"]):
    bid["cards_tmp"] = [card for card in cardsjson if str(card["rarity"]) in bid["rarities"] and int(card["id"]) < 330]
  else:
    bid["cards_tmp"] = [card for card in cardsjson if str(card["rarity"]) in bid["rarities"]]
  bid["cards"] = []
  for ed in bid["editions"]:
    current_ed = [str(card["id"]) for card in bid["cards_tmp"] if str(ed) in card["editions"]]
    bid["cards"] =  bid["cards"] + current_ed

blockchain = Blockchain(blockchain_instance=hive)
stream = blockchain.stream()

for op in stream:
  if(op["type"] == 'custom_json'):
    if op["id"] == 'sm_sell_cards':
      try:
        if(op["json"][:1] == '[' ):
          listing = json.loads(op["json"][1:-1])
        else:
          listing = json.loads(op["json"])
        
        if (check_desired(listing, op["trx_id"]) == True):
            price = float(listing["price"])
            cardid = str(listing["cards"])[5:-13]
            id = op["trx_id"]
            jsondata_old = '{"items":["'+ str(id) + '-0"], "price":' + str(price) +', "currency":"DEC"}'
            hive.custom_json('sm_market_purchase', json_data=jsondata_old, required_auths=[account_name])
      except:
        print("...") 
    else:
      if(len(currently_buying) > 0 and account_name in op["required_auths"]):
        try:
          response = requests.request("GET", url_purchase + op["trx_id"], headers=headers)
          data = json.loads(response.text)
          buydata = json.loads(data["trx_info"]["data"])
          if(data["trx_info"]["success"] == True):
            res = json.loads(data["trx_info"]["result"])
            print("############################")
            print("successfully bought card for: " + str(res["total_dec"]) + "DEC")
            print("############################")
            hive.custom_json('sm_token_transfer', json_data={"to":"derfabs","qty":res["total_dec"]/100,"token":"DEC"}, required_auths=[account_name])
            for buy in currently_buying:
              if((str(buy["id"]) + "-0") in buydata["items"]):
                currently_buying.remove(buy)
          else:
            for buy in currently_buying:
              if((str(buy["id"]) + "-0") in buydata["items"]):
                bids[buy["bid_idx"]]["max_quantity"] = bids[buy["bid_idx"]]["max_quantity"] + 1
                print("buy failed, card already sold")
                currently_buying.remove(buy)
        except:
          print("...")