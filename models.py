import heapq
import time
import random
import threading
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime

# -----------------------------
# Data Models
# -----------------------------
class Order:
    def __init__(self, order_id, order_type, commodity, quantity, price, timestamp=None):
        """
        order_type: 'buy' or 'sell'
        price: order price
        remaining: quantity remaining to be filled (supports partial fills)
        active: flag for cancellation (inactive orders are skipped)
        """
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

# -----------------------------
# Order Book with Matching Logic
# -----------------------------
class OrderBook:
    def __init__(self, commodity):
        self.commodity = commodity
        self.buy_orders = []   # max-heap via negative prices
        self.sell_orders = []  # min-heap

    def add_order(self, order: Order):
        if order.order_type == 'buy':
            heapq.heappush(self.buy_orders, (-order.price, order.timestamp, order))
        elif order.order_type == 'sell':
            heapq.heappush(self.sell_orders, (order.price, order.timestamp, order))

    def _clean_inactive(self):
        while self.buy_orders and not self.buy_orders[0][2].active:
            heapq.heappop(self.buy_orders)
        while self.sell_orders and not self.sell_orders[0][2].active:
            heapq.heappop(self.sell_orders)

    def match_orders(self):
        trades = []
        self._clean_inactive()
        while self.buy_orders and self.sell_orders:
            best_buy = self.buy_orders[0][2]
            best_sell = self.sell_orders[0][2]
            if not best_buy.active:
                heapq.heappop(self.buy_orders)
                continue
            if not best_sell.active:
                heapq.heappop(self.sell_orders)
                continue
            if best_buy.price >= best_sell.price:
                if best_buy.price == best_sell.price:
                    trade_price = best_buy.price
                else:
                    trade_price = (best_buy.price + best_sell.price) / 2
                    print(f"Manual approval needed for trade between {best_buy.order_id} and {best_sell.order_id}... auto-approved.")
                trade_quantity = min(best_buy.remaining, best_sell.remaining)
                trade = Trade(buyer=best_buy.order_id,
                              seller=best_sell.order_id,
                              commodity=self.commodity,
                              price=trade_price,
                              quantity=trade_quantity)
                trades.append(trade)
                best_buy.remaining -= trade_quantity
                best_sell.remaining -= trade_quantity
                if best_buy.remaining == 0:
                    heapq.heappop(self.buy_orders)
                if best_sell.remaining == 0:
                    heapq.heappop(self.sell_orders)
            else:
                break
        return trades

# -----------------------------
# Trading Engine
# -----------------------------
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

    def place_order(self, order: Order):
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

# -----------------------------
# Auction & AuctionManager
# -----------------------------
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
        self.active_auctions = {}  # commodity -> Auction (one active auction per commodity)
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

    def run(self):
        while simulation_running:
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
                        # Update orders.
                        auction.seller_order.remaining -= trade_quantity
                        winning_bid.remaining -= trade_quantity
                        self.engine.trade_history[commodity].append(trade)
                        print(f"Auction trade executed for {commodity}: {trade}")
                    else:
                        print(f"Auction for {commodity} ended with no bids.")
            time.sleep(0.5)

# -----------------------------
# Bot Implementation (Traders)
# -----------------------------
class Bot:
    def __init__(self, bot_id, engine: TradingEngine, commodity, objective, is_seller=True, time_limit=5, threshold=0.05):
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

    def trade(self):
        """Attempt to trade repeatedly (normal order or auction mode)."""
        # For seller bots, with 10% probability, start an auction.
        if self.is_seller and random.random() < 0.1:
            order_price = self.target_price * (1 - self.current_threshold)
            order_id = f"{self.bot_id}-{time.time()}"
            seller_order = Order(order_id=order_id, order_type='sell',
                                 commodity=self.commodity, quantity=self.quantity, price=order_price)
            self.engine.place_order(seller_order)
            auction = auction_manager.start_auction(seller_order, duration=self.time_limit)
            if auction:
                while simulation_running and auction_manager.check_active(self.commodity) is not None:
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
        while simulation_running and (time.time() - start < self.time_limit) and order.remaining > 0:
            time.sleep(0.5)
            self.engine.match_all()
        if not simulation_running:
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

# -----------------------------
# Utility: Generate Random Product Names (limited to 10)
# -----------------------------
def generate_random_product_names(n=10):
    adjectives = ["Cool", "Amazing", "Fantastic", "Ultra", "Super", "Mega", "Hyper", "Smart", "Eco", "Prime"]
    nouns = ["Widget", "Gadget", "Device", "Item", "Tool", "Gear", "Product", "Instrument", "Module", "System"]
    products = set()
    while len(products) < n:
        product = f"{random.choice(adjectives)} {random.choice(nouns)}"
        products.add(product)
    return list(products)

# -----------------------------
# Visualization of All Commodities' Trade History
# -----------------------------
def visualize_all_commodities(engine: TradingEngine):
    plt.figure(figsize=(12, 6))
    for commodity, trades in engine.trade_history.items():
        if trades:
            times = [trade.timestamp for trade in trades]
            prices = [trade.price for trade in trades]
            plt.plot(times, prices, marker='o', label=commodity)
    plt.xlabel("Time (Unix Timestamp)")
    plt.ylabel("Trade Price")
    plt.title("Trade History for All Commodities Over the Simulation")
    plt.legend()
    plt.tight_layout()
    plt.savefig('trade_history.png')

# -----------------------------
# Helper: Create a New Random Bot
# -----------------------------
bot_counter = 0
def create_random_bot(engine, product_list):
    global bot_counter
    bot_counter += 1
    bot_id = f"Bot{bot_counter}"
    commodity = random.choice(product_list)
    is_seller = random.choice([True, False])
    quantity = random.randint(1, 20)
    target_price = round(engine.get_market_value(commodity), 2)
    objective = {'quantity': quantity, 'price': target_price}
    if is_seller:
        threshold = random.uniform(0.01, 0.10)
    else:
        threshold = random.uniform(0.01, 0.20)
    return Bot(bot_id=bot_id, engine=engine, commodity=commodity,
               objective=objective, is_seller=is_seller, time_limit=5, threshold=threshold)

# -----------------------------
# Asynchronous Simulation: Bot Worker Function
# -----------------------------
simulation_running = True

def bot_worker(engine, product_list):
    while simulation_running:
        bot = create_random_bot(engine, product_list)
        bot.trade()
        time.sleep(random.uniform(0.1, 0.5))

