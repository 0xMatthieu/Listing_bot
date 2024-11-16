#!/usr/bin/env python3

import webhook_alerts
import time
import os
from cex_listing import ExchangeListingMonitor
from dotenv import load_dotenv
from Exchange_trade import Exchange
import pandas as pd
import Sharing_data
import logging

class Crypto(object):
    def __init__(self, symbol_spot=None, symbol_futures=None, leverage = 20, timeframe = '1m', percentage = 20, function="MACD"):
        self.symbol_spot = symbol_spot
        self.symbol_futures = symbol_futures
        self.df = pd.DataFrame()
        self.leverage = leverage
        self.timeframe = timeframe
        self.percentage = percentage
        self.stop_loss_percentage = 0.02
            
class Futures_bot(object):

    def __init__(self):
        self.kucoin = Exchange(name='kucoin')
        self.kucoin.load_market(market_type='futures')
        #crypto
        self.crypto = []
        #self.crypto.append(Crypto(symbol_spot='TAO/USDT', symbol_futures='TAOUSDTM', leverage=None, timeframe='1m', percentage = 20, function=None))
        self.life_data = pd.Timestamp.now()

    def run_futures_trading_function(self, Crypto=None, function=None):
        start_time = time.time()
        market_type='futures'
        order_type = 'market' # or 'limit'

        if Crypto.df.empty:
            try:
                Crypto.df = self.kucoin.fetch_klines(symbol=Crypto.symbol_futures, timeframe=Crypto.timeframe, since=None, limit=5, market_type=market_type)
            except Exception as e:
                Sharing_data.append_to_file(f"Error fetching data for {Crypto.symbol_futures}: {e}", level=logging.CRITICAL)
                return Crypto
            Crypto.df['Quantity'] = 0
            Sharing_data.append_to_file(f"Crypto {Crypto.symbol_futures} dataframe created", level=logging.CRITICAL)

        Sharing_data.append_to_file(f"-----------------------------------------------", level=logging.CRITICAL)
        Sharing_data.append_to_file(f"buy on {Crypto.symbol_futures} at time {Crypto.df['timestamp'].max()}", level=logging.CRITICAL)
        Crypto.df.iloc[-1, Crypto.df.columns.get_loc('Quantity')] = self.kucoin.place_order(symbol=Crypto.symbol_futures, percentage=Crypto.percentage, 
            order_side='buy', market_type=market_type, order_type=order_type, leverage=Crypto.leverage)
        self.kucoin.create_stop_orders(symbol=Crypto.symbol_futures, signal='buy', order_type=order_type, stop_loss_long_price=Crypto.df['close'].iloc[-1] * (1 - self.stop_loss_percentage), 
            take_profit_long_price=None, stop_loss_short_price=None, 
            take_profit_short_price=None,  market_type=market_type, quantity=Crypto.df['Quantity'].iloc[-1])
        return Crypto

    def run_futures_trading_monitoring(self, Crypto=None, function=None):
        start_time = time.time()
        market_type='futures'
        order_type = 'market' # or 'limit'
        
        Crypto.df, updated = self.kucoin.fetch_exchange_ticker(symbol=Crypto.symbol_futures, df=Crypto.df, interval='1m', market_type=market_type)
        if updated:
            self.kucoin.monitor_and_adjust_stop_orders(symbol=Crypto.symbol_futures, order_type=order_type, stop_loss_long_price=Crypto.df['close'].iloc[-1] * (1 - self.stop_loss_percentage), 
                take_profit_long_price=None, stop_loss_short_price=None, 
                take_profit_short_price=None,  market_type=market_type)
        return Crypto

    def run_main(self, sleep_time=5):
        start_time = time.time()
        for crypto in self.crypto:
            crypto = self.run_futures_trading_function(Crypto=crypto, function=None)
        #print(f"Main crypto algo time execution {time.time() - start_time}")
        self.life_data = Sharing_data.life_data(life_data=self.life_data, level=logging.DEBUG)
        print(f"Crypto {Crypto.symbol_futures} time execution {time.time() - start_time}")

    def run_monitoring(self, sleep_time=5):
        start_time = time.time()
        for crypto in self.crypto:
            crypto = self.run_futures_trading_monitoring(Crypto=crypto, function=None)
        #print(f"Main crypto algo time execution {time.time() - start_time}")
        #print(f"Crypto {Crypto.symbol_futures} time execution {time.time() - start_time}")

    

load_dotenv()
webhook = webhook_alerts.WebhookAlerts(os.environ.get('token_id'))
exchanges = ['coinbase', 'binance', 'kraken', 'mexc', 'bitget', 'kucoin']  # Add more exchanges as needed
#monitor = ExchangeListingMonitor(exchanges)
Bot = Futures_bot()
Sharing_data.logger_init()



while True:
    start_time = time.time()
    
    new_currency = webhook.get_currency_if_new_coin()
    if new_currency:
        print("New coin added:", new_currency)
        Bot.crypto.append(Crypto(symbol_spot=new_currency + '/USDT', symbol_futures=new_currency + 'USDTM', leverage=20, timeframe='1m', percentage = 50, function=None))
        Bot.run_main()

    
    #new_currency = monitor.fetch_and_check_new_listings()

    if new_currency:
        print("New coin added:", new_currency)


    Bot.run_monitoring()

    #print("time elapsed to run the function:", time.time()-start_time)
    time.sleep(1)
