# Splinterbuyer - Splinterlands Autobid Market Bot

A market bot written in Python that listens to HIVE blockchain transactions to automatically buy underpriced cards as soon as they get listed.

## How it works
The bot streams the HIVE blockchain and listens for new sell orders. You can set bids for specific cards, rarities or editions, and when the bot finds a listing that fits one of your bids, it buys the card automatically.

### Features
- Fully automated lightning fast buying (and selling) of cards
- Filter by card id, rarity, edition, gold foil
- You can configure how many cards the bot should buy
- You don't have to compete against other bidders like on Peakmonsters Autobid
- Can run 24/7

### Fees
The bot is completely free to use, if you enjoy it please consider donating. :)

## Installation

1. Download and install [Python](https://www.python.org/)
2. Download the latest release from the [release page.](https://github.com/derfabsSL/Splinterbuyer/releases)
 
    Alternatively, download [Git](https://git-scm.com/) and clone the repo: 

      ```sh
      git clone https://github.com/derfabsSL/Splinterbuyer.git
      ```
3. Go to repo directory
      ```sh
      cd Splinterbuyer
      ```

4. Install the required libraries by running: 
      ```sh
      pip install -r requirements.txt
      ```

### Bids.json
The bids.json file is where you can set the parameters of the bot as well as specify your account info. An example file is included in the folder.

The fields are as following:

#### account

1. `name`: Your Splinterlands username, without the @, for example:
  ```
  "username": "derfabs",
  ```
2. `active_key`: Your HIVE active key, this is never shared with anyone and only used to buy cards on the blockchain
```
"active_key": "iednwodpdw2112einoenpdisdnpsa",
```
3. `currency`: Either "DEC" or "CREDITS", depending on how you want to buy
```
"currency": "DEC"
```

#### global_params

1. `currency`: Either "DEC" or "CREDITS", depending on how you want to buy
   ```
   "currency": "DEC"
   ```

2. `auto_set_buy_price`: If this is set to true, the bot will check current market prices and bid accordingly, to buy underpriced cards.
    ```
    "auto_set_buy_price": "true"
    ```

3. `buy_pct_below_market`: Use this parameter in combination with "auto_set_buy_price":true
   This specifies how many percent below market price the bot should buy.

    **This is only active if "auto_set_buy_price":true**

    Example, buy 10% below current market price:
    ```
    "buy_pct_below_market": 10
    ```

5. `sell_pct_above_buy`: Use this parameter in combination with "auto_set_buy_price":true
   This specifies how many percent above buying price the bot should resell cards.

   **This is only active if "auto_set_buy_price":true, otherwise the bot uses the bids' individual "sell_for_pct_more**

    Example, sell for 15% more than buy price: 
    ```
    "sell_pct_above_buy": 15
    ```

6. `tip_pct_of_profit`: This specifies how many percent of your **profit** you want to send to me as a tip. This tipping occurs only if the bot successfully resells a card. So if for example you buy a card for 1$ and sell it for 1.2$ and this is set to 10%, the tip would amount to 0.02$ (10% of 0.2$ profit). 
   
   *In case you don't want to tip me, set this to 0.*

   Example, you love this bot, so you tip 50% of your profits: 
    ```
    "tip_pct_of_profit": 50
    ```
   
#### bids

1. `comment`: This field is there to name your bids. You can write whatever you want here, the bot will ignore it.
              
    Example:

    ```
    "comment": "I love Splinterbuyer Market bot!"
    ```

2. `cards`: This specifies individual cards you want the bot to buy. For Example to buy Chicken, you would put ["131"].

     If you fill in this field, all other ones will be ignored, you can leave them empty.

     Example, only buy chicken:
      ```
      "cards": ["131"]
      ```
3. `editions`: This specifies the editions the bot will filter for. The keys are as following: 

   `alpha`

   `beta` 

   `promo`

   `reward` 

   `untamed`

   `dice`

   `chaos`

      Example, only buy alpha, beta, promo and untamed cards:
      ```
      "editions": ["alpha","beta","promo","untamed"]
      ```
4. `rarities`: This specifies the rarities the bot will filter for, formatted by the IDs as they appear in the Splinterlands API. The keys are as following: 

    `common`

    `rare`

    `epic`

    `legendary` 
 
     Example, only buy epic and legendary cards:
     
      ```
      "rarities": ["epic","legendary"]
      ```
5. `elements`: The bot can also filter for specific elements, like "fire", "death" or "dragon" 
   
   The keys are: 

   `fire`

   `water`

   `earth`

   `life`

   `death`

   `dragon`

   `neutral`

    Example, filter for dragon cards only:

    ```
    "elements": ["dragon"]
    ```
    
6. `types`: To filter for Summoners or Monsters. Values are:
   
   `summoner`

   `monster`

    Example, buy summoners and monsters:

    ```
    "types": ["summoner", "monster"]
    ```
    
7. `min_bcx`: To buy only cards with a bcx equal o higher than this parameter
   
    Example, buy cards with >= 5 bcx:

    ```
    "min_bcx": 5
    ```
    
8. `min_cp_per_usd`: To buy only cards with a specific CP/USD (Collection Power per USD)

    Example, buy cards with CP/USD >= 200:

    ```
    "min_cp_per_usd": 200
    ```

9. `max_price`: The maximum price in USD to buy the cards. Everything cheaper than this price will be bought by the bot.

     Example, buy everything under 69.420 USD:
     
      ```
      "max_price": 69.42
      ```
10. `max_quantity`: How many cards the bot should buy for this specific bid

    Example, buy 5 cards:

        ```
        "max_quantity": 5
        ```
11. `gold_only`: If this is set to true, the bot will only  buy gold foil cards.

    Example, buy only gold foil cards:
  
      ```
      "gold_only": true
      ```
12. `exclude_cl`: This parameter is meant to be paired with filtering for Reward Edition cards, because these cards cannot be filtered by edition, but Chaos Legion cards are worth significantly less atm. If this is set to true, the bot will NOT buy any cards released with ID > 330.
 
     Example, don't buy CL (reward) cards:

          ```
          "exclude_cl": true
          ```

13. `sell_for_pct_more`: If you want the bot to put the cards on the market immediately after buying, you can use this parameter. The bot will sell the card for x   percent more than the buy price. For example, if the card is bought for 10$ and "buy_for_pct_more" is set to 10, the bot will list the card for 11$

     **If you don't want the bot to sell automatically, leave this parameter at 0**
     **This is only active if "auto_set_buy_price":false, otherwise it is ignores and the global parameter is used**

     Example, sell for 10% higher than buy price:

           ```
           "sell_for_pct_more": 10
           ```

     Example 2, don't sell cards:

           ```
           "sell_for_pct_more": 0
           ```


### Running the bot

fill out "bids.json"

click "Splinterbuyer.py"

or
```sh
python Splinterbuyer.py
```
or
```sh
python3 Splinterbuyer.py
```

## Are my Keys Safe?

Your keys are only used to sign blockchain transactions for buying cards and will never leave your computer.
The bot needs your active key to be able to make purchases independently without needing a confirmation for every purchase.
The code for this bot is open source, so you can see for yourself where the key is used and what for.

## Donations

If you wish to donate to me (the developer), you can do so through Splinterlands
```@derfabs```

Use my referral links for Splinterlands and Rising Star!

https://splinterlands.com?ref=derfabs
https://www.risingstargame.com?referrer=derfabs
