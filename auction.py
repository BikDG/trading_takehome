"""
This module implements the Auction and AuctionManager classes for managing auctions.
"""

import time
import threading
from models import Trade

class Auction:
    """Represents an auction for a seller's order."""
    def __init__(self, seller_order, duration=5):
        """
        Initialize the auction with the seller order and duration (seconds).
        """
        self.seller_order = seller_order
        self.commodity = seller_order.commodity
        self.duration = duration
        self.start_time = time.time()
        self.bids = []  # list of bid orders

    def add_bid(self, bid_order):
        """Add a bid order to the auction."""
        self.bids.append(bid_order)
        print(f"Bid added to auction for {self.commodity}: {bid_order}")

    def is_expired(self):
        """Return True if the auction duration has passed."""
        return time.time() >= self.start_time + self.duration

    def finalize(self):
        """
        Finalize the auction by returning the bid with the highest price.
        Returns None if there are no bids.
        """
        if self.bids:
            winning_bid = max(self.bids, key=lambda o: o.price)
            return winning_bid
        return None

class AuctionManager:
    """Manages active auctions for commodities."""
    def __init__(self, engine):
        """
        Initialize with a trading engine.
        """
        self.engine = engine
        self.active_auctions = {}  # commodity -> Auction
        self.lock = threading.Lock()

    def start_auction(self, seller_order, duration=5):
        """
        Start an auction for the seller order if none is active.
        Returns the Auction instance or None.
        """
        with self.lock:
            if seller_order.commodity in self.active_auctions:
                return None
            auction = Auction(seller_order, duration)
            self.active_auctions[seller_order.commodity] = auction
            print(f"Auction started for {seller_order.commodity} by {seller_order.order_id}")
            return auction

    def add_bid(self, commodity, bid_order):
        """
        Add a bid to an active auction for a commodity.
        """
        with self.lock:
            if commodity in self.active_auctions:
                self.active_auctions[commodity].add_bid(bid_order)
            else:
                print(f"No active auction for {commodity} to add bid.")

    def check_active(self, commodity):
        """
        Check and return the active auction for a commodity, or None.
        """
        with self.lock:
            return self.active_auctions.get(commodity, None)

    def run(self, simulation_running):
        """
        Continuously finalize expired auctions while simulation_running() is True.
        """
        while simulation_running():
            with self.lock:
                expired = [c for c, auction in self.active_auctions.items() if auction.is_expired()]
                for commodity in expired:
                    auction = self.active_auctions.pop(commodity)
                    winning_bid = auction.finalize()
                    if winning_bid:
                        trade_quantity = min(auction.seller_order.remaining, winning_bid.remaining)
                        trade_price = winning_bid.price  # Winning bid price
                        trade = Trade(
                            buyer=winning_bid.order_id,
                            seller=auction.seller_order.order_id,
                            commodity=commodity,
                            price=trade_price,
                            quantity=trade_quantity
                        )
                        auction.seller_order.remaining -= trade_quantity
                        winning_bid.remaining -= trade_quantity
                        self.engine.trade_history[commodity].append(trade)
                        print(f"Auction trade executed for {commodity}: {trade}")
                    else:
                        print(f"Auction for {commodity} ended with no bids.")
            time.sleep(0.5)
