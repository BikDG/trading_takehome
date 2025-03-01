"""
Data models for the trading simulation, including Order and Trade.
"""

import time
from datetime import datetime

class Order:
    """Represents an order for a commodity."""
    def __init__(self, order_id, order_type, commodity, quantity, price, timestamp=None):
        self.order_id = order_id
        self.order_type = order_type
        self.commodity = commodity
        self.quantity = quantity
        self.price = price
        self.remaining = quantity
        self.timestamp = timestamp or time.time()
        self.active = True

    def __repr__(self):
        return (f"Order({self.order_id}, {self.order_type}, {self.commodity}, "
                f"Qty:{self.remaining}/{self.quantity}, Price:{self.price:.2f})")

class Trade:
    """Represents an executed trade between a buyer and a seller."""
    def __init__(self, buyer, seller, commodity, price, quantity, timestamp=None):
        self.buyer = buyer
        self.seller = seller
        self.commodity = commodity
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp or time.time()

    def __repr__(self):
        ts = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
        return (f"Trade({self.commodity}, Qty:{self.quantity}, Price:{self.price:.2f}, "
                f"Buyer:{self.buyer}, Seller:{self.seller}, Time:{ts})")
