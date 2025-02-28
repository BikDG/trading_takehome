# bot.py
import time
import random
from models import Order

class Bot:
    def __init__(self, bot_id, engine, commodity, objective, is_seller=True, time_limit=5, threshold=0.05):
        """
        objective: {'quantity': int, 'price': float} – target price and quantity.
        is_seller: True if selling, False if buying.
        threshold: initial percentage (e.g. 0.05 for 5%). For sellers, it discounts the target; for buyers, it increases it.
        time_limit: seconds allowed for an order before retrying.
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
        # For seller bots, with 10% probability, start an auction.
        if self.is_seller and random.random() < 0.1:
            order_price = self.target_price * (1 - self.current_threshold)
            order_id = f"{self.bot_id}-{time.time()}"
            seller_order = Order(order_id=order_id, order_type='sell',
                                 commodity=self.commodity, quantity=self.quantity, price=order_price)
            self.engine.place_order(seller_order)
            auction = auction_manager.start_auction(seller_order, duration=self.time_limit)
            if auction:
                while simulation_running() and auction_manager.check_active(self.commodity) is not None:
                    time.sleep(0.5)
                print(f"Seller {self.bot_id} auction completed for {self.commodity}.")
            return

        # For buyer bots, if an active auction exists, place a bid.
        if not self.is_seller:
            active_auction = auction_manager.check_active(self.commodity)
            if active_auction:
                bid_price = self.target_price * (1 + self.current_threshold)
                order_id = f"{self.bot_id}-{time.time()}"
                bid_order = Order(order_id=order_id, order_type='buy',
                                  commodity=self.commodity, quantity=self.quantity, price=bid_price)
                auction_manager.add_bid(self.commodity, bid_order)
                print(f"Buyer {self.bot_id} placed bid on auction for {self.commodity} at price {bid_price:.2f}.")
                return

        # Otherwise, perform a normal order trade.
        start = time.time()
        if self.is_seller:
            order_price = self.target_price * (1 - self.current_threshold)
            order_type = 'sell'
        else:
            order_price = self.target_price * (1 + self.current_threshold)
            order_type = 'buy'
        order_id = f"{self.bot_id}-{time.time()}"
        order = Order(order_id=order_id, order_type=order_type,
                      commodity=self.commodity, quantity=self.quantity, price=order_price)
        self.engine.place_order(order)
        while simulation_running() and (time.time() - start < self.time_limit) and order.remaining > 0:
            time.sleep(0.5)
            self.engine.match_all()
        if not simulation_running():
            order.active = False
            return
        if order.remaining > 0:
            order.active = False
            if self.is_seller:
                old_threshold = self.current_threshold
                self.current_threshold = min(self.current_threshold + 0.05, 0.50)
                print(f"Seller {self.bot_id} timed out on {self.commodity}. Threshold increased from {old_threshold:.0%} to {self.current_threshold:.0%}.")
            else:
                old_threshold = self.current_threshold
                self.current_threshold += 0.05
                print(f"Buyer {self.bot_id} timed out on {self.commodity}. Threshold increased from {old_threshold:.0%} to {self.current_threshold:.0%}.")
        else:
            print(f"Bot {self.bot_id} successfully traded on {self.commodity} at price {order_price:.2f}.")
