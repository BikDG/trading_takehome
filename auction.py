# auction.py
import time
import threading
from models import Trade

class Auction:
    def __init__(self, seller_order, duration=5):
        self.seller_order = seller_order
        self.commodity = seller_order.commodity
        self.duration = duration
        self.start_time = time.time()
        self.bids = []  # list of bid orders

    def add_bid(self, bid_order):
        self.bids.append(bid_order)
        print(f"Bid added to auction for {self.commodity}: {bid_order}")

    def is_expired(self):
        return time.time() >= self.start_time + self.duration

    def finalize(self):
        if self.bids:
            winning_bid = max(self.bids, key=lambda o: o.price)
            return winning_bid
        return None

class AuctionManager:
    def __init__(self, engine):
        self.engine = engine
        self.active_auctions = {}  # commodity -> Auction
        self.lock = threading.Lock()

    def start_auction(self, seller_order, duration=5):
        with self.lock:
            if seller_order.commodity in self.active_auctions:
                return None  # Auction already active for this commodity.
            auction = Auction(seller_order, duration)
            self.active_auctions[seller_order.commodity] = auction
            print(f"Auction started for {seller_order.commodity} by {seller_order.order_id}")
            return auction

    def add_bid(self, commodity, bid_order):
        with self.lock:
            if commodity in self.active_auctions:
                auction = self.active_auctions[commodity]
                auction.add_bid(bid_order)
            else:
                print(f"No active auction for {commodity} to add bid.")

    def check_active(self, commodity):
        with self.lock:
            return self.active_auctions.get(commodity, None)

    def run(self, simulation_running):
        while simulation_running():
            with self.lock:
                expired = []
                for commodity, auction in list(self.active_auctions.items()):
                    if auction.is_expired():
                        expired.append(commodity)
                for commodity in expired:
                    auction = self.active_auctions.pop(commodity)
                    winning_bid = auction.finalize()
                    if winning_bid:
                        trade_quantity = min(auction.seller_order.remaining, winning_bid.remaining)
                        trade_price = winning_bid.price  # Winning bid price
                        trade = Trade(buyer=winning_bid.order_id, seller=auction.seller_order.order_id,
                                      commodity=commodity, price=trade_price, quantity=trade_quantity)
                        auction.seller_order.remaining -= trade_quantity
                        winning_bid.remaining -= trade_quantity
                        self.engine.trade_history[commodity].append(trade)
                        print(f"Auction trade executed for {commodity}: {trade}")
                    else:
                        print(f"Auction for {commodity} ended with no bids.")
            time.sleep(0.5)
