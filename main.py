#!/usr/bin/env python3

import webhook_alerts
import time
import os
from cex_listing import ExchangeListingMonitor

webhook = webhook_alerts.WebhookAlerts(os.environ.get('token_id'))
exchanges = ['coinbase', 'binance', 'kraken', 'mexc', 'bitget', 'kucoin']  # Add more exchanges as needed
monitor = ExchangeListingMonitor(exchanges)

while True:
    start_time = time.time()
    
    new_currency = webhook.get_currency_if_new_coin()
    if new_currency:
        print("New coin added:", new_currency)
    
    new_currency = monitor.fetch_and_check_new_listings()

    if new_currency:
        print("New coin added:", new_currency)

    #print("time elapsed to run the function:", time.time()-start_time)
    time.sleep(1)
