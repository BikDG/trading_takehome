# engine.py
import threading
import random
from collections import defaultdict
from order_book import OrderBook

class TradingEngine:
    def __init__(self):
        self.order_books = {}
        self.trade_history = defaultdict(list)
        self.orders = {}
        self.lock = threading.Lock()

    def get_order_book(self, commodity):
        if commodity not in self.order_books:
            self.order_books[commodity] = OrderBook(commodity)
        return self.order_books[commodity]

    def place_order(self, order):
        with self.lock:
            self.orders[order.order_id] = order
            book = self.get_order_book(order.commodity)
            book.add_order(order)
            print(f"Placed order: {order}")

    def match_all(self):
        with self.lock:
            for commodity, book in self.order_books.items():
                trades = book.match_orders()
                for trade in trades:
                    self.trade_history[commodity].append(trade)
                    print(f"Executed {trade}")

    def cancel_all_orders(self):
        with self.lock:
            for order in self.orders.values():
                order.active = False
            print("All pending orders have been canceled.")

    def get_market_value(self, commodity):
        history = self.trade_history.get(commodity, [])
        if history:
            return history[-1].price
        else:
            return random.uniform(1.0, 100.0)

    def get_history(self, commodity):
        return self.trade_history.get(commodity, [])
