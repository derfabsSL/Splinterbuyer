# Splinterbuyer - Splinterlands Autobid Market Bot

A market bot written in Python that listens to HIVE blockchain transactions to automatically buy underpriced cards as soon as they get listed.

## How it works
The bot streams the HIVE blockchain and listens for new sell orders. You can set bids for specific cards, rarities or editions, and when the bot finds a listing that fits one of your bids, it buys the card automatically.

### Features
- Fully automated lightning fast buying of cards
- Filter by card id, rarity, edition, gold foil
- You can configure how many cards the bot should buy
- You don't have to compete against other bidders like on Peakmonsters Autobid
- Can run 24/7

### Fees
The bot is completely free to use, if you enjoy it, please consider donating. :)

## Installation

1. Download and install [Git](https://git-scm.com/) and [Python](https://www.python.org/)
2. Clone the repo: 

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
   
#### bids

1. `cards`: This specifies individual cards you want the bot to buy. For Example to buy Chicken, you would put ["131"].
          If you want to buy only a single card, leave the other fields empty!

          Example, only buy chicken:
      ```
        "cards": ["131"]
      ```
4. `editions`: This specifies the editions the bot will filter for, formatted by the edition IDs as they appear in the Splinterlands API. The keys are as following: 

      `0` - alpha

      `1` - beta

      `2` - promo

      `3` - reward

      `4` - untamed

      `5` - dice

      `7` - chaos_legion

      Note that 5 is missing, as it is for Gladiator cards, which are not tradable.
      Example, only buy alpha, beta, promo and untamed cards:
      ```
        "editions": ["0","1","2","4"]
      ```
3. `rarities`: : This specifies the rarities the bot will filter for, formatted by the IDs as they appear in the Splinterlands API. The keys are as following: 
      `0` - common

      `1` - rare

      `2` - epic

      `3` - legendary
 
     Example, only buy epic and legendary cards:
      ```
        "rarities": ["3","4"]
      ```
4. `max_price`: The maximum price in USD to buy the cards. Everything cheaper than this price will be bought by the bot.

       Example, buy everything under 69.420 USD:
      ```
        "max_price": [69.42]
      ```
6. `max_quantity`: How many cards the bot should buy for this specific bid

 Example, buy 5 cards:
      ```
        "max_quantity": 5
      ```
8. `gold_only`: If this is set to true, the bot will only  buy gold foil cards.

  Example, buy only gold foil cards:
      ```
        "gold_only": true
      ```
10. `exclude_cl`: This parameter is meant to be paired with filtering for Reward Edition cards, because these cards cannot be filtered by edition, but Chaos Legion cards are worth significantly less atm. If this is set to true, the bot will NOT buy any cards released with ID > 330.
 
Example, don't buy CL (reward) cards:
      ```
        "exclude_cl": true
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
