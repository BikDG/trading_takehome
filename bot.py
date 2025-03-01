"""
This module implements the Bot class, which simulates a trading bot.
"""

import time
import random
from models import Order

class Bot:
    """
    A trading bot that performs normal order trades or participates in auctions.
    """
    def __init__(self,
                 bot_id,
                 engine,
                 commodity,
                 objective,
                 is_seller=True,
                 time_limit=5,
                 threshold=0.05):
        """
        Initialize the bot with:
          - bot_id: Unique identifier.
          - engine: TradingEngine instance.
          - commodity: Commodity symbol.
          - objective: Dict with 'quantity' and 'price'.
          - is_seller: True for selling, False for buying.
          - time_limit: Seconds allowed for an order.
          - threshold: Initial percentage adjustment.
        """
        self.bot_id = bot_id
        self.engine = engine
        self.commodity = commodity
        self.objective = objective
        self.is_seller = is_seller
        self.time_limit = time_limit
        self.target_price = objective['price']
        self.quantity = objective['quantity']
        self.current_threshold = threshold

    def trade(self, auction_manager, simulation_running):
        """
        Execute a trade. Sellers may start an auction (10% chance);
        buyers place a bid if an auction is active; otherwise, execute a normal trade.
        """
        # Seller auction mode (10% probability)
        if self.is_seller and random.random() < 0.1:
            order_price = self.target_price * (1 - self.current_threshold)
            order_id = f"{self.bot_id}-{time.time()}"
            seller_order = Order(order_id,
                                 'sell',
                                 self.commodity,
                                 self.quantity,
                                 order_price)
            self.engine.place_order(seller_order)
            auction = auction_manager.start_auction(seller_order, duration=self.time_limit)
            if auction:
                while (simulation_running()
                and auction_manager.check_active(self.commodity) is not None):
                    time.sleep(0.5)
                print(f"Seller {self.bot_id} auction completed for {self.commodity}.")
            return

        # Buyer auction mode: place bid if auction is active.
        if not self.is_seller:
            active_auction = auction_manager.check_active(self.commodity)
            if active_auction:
                bid_price = self.target_price * (1 + self.current_threshold)
                order_id = f"{self.bot_id}-{time.time()}"
                bid_order = Order(order_id, 'buy', self.commodity, self.quantity, bid_price)
                auction_manager.add_bid(self.commodity, bid_order)
                print(f"Buyer {self.bot_id} placed bid on auction for {self.commodity} "
                      f"at price {bid_price:.2f}.")

                return

        # Normal order trade.
        start = time.time()
        if self.is_seller:
            order_price = self.target_price * (1 - self.current_threshold)
            order_type = 'sell'
        else:
            order_price = self.target_price * (1 + self.current_threshold)
            order_type = 'buy'
        order_id = f"{self.bot_id}-{time.time()}"
        order = Order(order_id, order_type, self.commodity, self.quantity, order_price)
        self.engine.place_order(order)
        while (simulation_running()
                and (time.time() - start < self.time_limit)
                and order.remaining > 0):
            time.sleep(0.5)
            self.engine.match_all()
        if not simulation_running():
            order.active = False
            return
        if order.remaining > 0:
            order.active = False
            old_threshold = self.current_threshold
            if self.is_seller:
                self.current_threshold = min(self.current_threshold + 0.05, 0.50)
            else:
                self.current_threshold += 0.05
            print(f"{'Seller' if self.is_seller else 'Buyer'} {self.bot_id}"
                  f"timed out on {self.commodity}."
                  f"Threshold increased from {old_threshold:.0%}"
                  f"to {self.current_threshold:.0%}.")
        else:
            print(f"Bot {self.bot_id} successfully traded on {self.commodity}"
                  f"at price {order_price:.2f}.")
