"""
This module implements the TradingEngine, which manages order books,
order placement, matching, and trade history.
"""

import threading
import random
from collections import defaultdict
from order_book import OrderBook

class TradingEngine:
    """Trading engine to manage orders and execute trades."""
    def __init__(self):
        self.order_books = {}
        self.trade_history = defaultdict(list)
        self.orders = {}
        self.lock = threading.Lock()

    def get_order_book(self, commodity):
        """Retrieve or create an OrderBook for a commodity."""
        if commodity not in self.order_books:
            self.order_books[commodity] = OrderBook(commodity)
        return self.order_books[commodity]

    def place_order(self, order):
        """Place an order into the order book."""
        with self.lock:
            self.orders[order.order_id] = order
            self.get_order_book(order.commodity).add_order(order)
            print(f"Placed order: {order}")

    def match_all(self):
        """Match orders from all order books and record trades."""
        with self.lock:
            for book in self.order_books.values():
                for trade in book.match_orders():
                    self.trade_history[trade.commodity].append(trade)
                    print(f"Executed {trade}")

    def cancel_all_orders(self):
        """Mark all orders as inactive."""
        with self.lock:
            for order in self.orders.values():
                order.active = False
            print("All pending orders have been canceled.")

    def get_market_value(self, commodity):
        """Return the last trade price for a commodity or a random value if none."""
        history = self.trade_history.get(commodity, [])
        return history[-1].price if history else random.uniform(1.0, 100.0)

    def get_history(self, commodity):
        """Return trade history for a commodity."""
        return self.trade_history.get(commodity, [])
