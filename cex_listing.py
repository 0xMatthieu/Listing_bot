import ccxt
import json
from datetime import datetime, timedelta
import os

class ExchangeListingMonitor:
    def __init__(self, exchanges, listings_filename='./data/new_listings.json'):
        self.exchanges = [getattr(ccxt, exchange)() for exchange in exchanges]  # Initialize each exchange
        self.listings_filename = listings_filename  # File to store new listings
        self.previous_markets = {}  # Store initial markets in memory
        self.initialize_markets()

    def initialize_markets(self):
        """Initializes the previous markets by loading the current markets for each exchange."""
        for exchange in self.exchanges:
            try:
                current_markets = exchange.load_markets()
                self.previous_markets[exchange.id] = set(current_markets.keys())
                print(f"Initialized markets for {exchange.id}")
            except Exception as e:
                print(f"Error initializing markets for {exchange.id}: {e}")

    def get_paris_time(self):
        """Get the current time in Paris."""
        utc_time = datetime.utcnow()
        paris_offset = timedelta(hours=1)  # Set to timedelta(hours=2) during daylight savings
        paris_time = utc_time + paris_offset
        return paris_time.strftime('%Y-%m-%d %H:%M:%S')
    
    def log_new_listing(self, exchange_name, currency):
        """Log a new listing with the exchange name, currency, and Paris timestamp."""
        listing = {
            "exchange": exchange_name,
            "currency": currency,
            "time": self.get_paris_time()
        }

        # Load existing listings or start with an empty list if the file is empty or corrupted
        if os.path.exists(self.listings_filename):
            try:
                with open(self.listings_filename, 'r') as file:
                    listings = json.load(file)
            except (json.JSONDecodeError, IOError):
                print(f"Warning: {self.listings_filename} is empty or corrupted. Starting with an empty list.")
                listings = []
        else:
            listings = []

        listings.append(listing)

        # Write updated listings to file
        with open(self.listings_filename, 'w') as file:
            json.dump(listings, file, indent=4)

    def fetch_and_check_new_listings(self):
        """Fetches current markets from each exchange and checks for new listings."""
        for exchange in self.exchanges:
            exchange_name = exchange.id
            try:
                current_markets = exchange.load_markets()
                current_symbols = set(current_markets.keys())
                previous_symbols = self.previous_markets.get(exchange_name, set())

                # Identify new listings by checking for symbols not in the previous snapshot
                new_listings = current_symbols - previous_symbols
                if new_listings:
                    #print(f"New listings on {exchange_name}: {new_listings}")
                    for symbol in new_listings:
                        # Log each new listing
                        self.log_new_listing(exchange_name, symbol)
                
                    # Update the previous markets snapshot with the current symbols
                    self.previous_markets[exchange_name] = current_symbols

                    return new_listings
                #else:
                    #print(f"No new listings on {exchange_name}.")
            except Exception as e:
                print(f"Error fetching data from {exchange_name}: {e}")

