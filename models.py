import heapq, time, random, threading, matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime

# Data Models
class Order:
    def __init__(self, order_id, order_type, commodity, quantity, price, timestamp=None):
        self.order_id, self.order_type, self.commodity = order_id, order_type, commodity
        self.quantity, self.price, self.remaining = quantity, price, quantity
        self.timestamp = timestamp or time.time()
        self.active = True
    def __repr__(self):
        return f"Order({self.order_id}, {self.order_type}, {self.commodity}, Qty:{self.remaining}/{self.quantity}, Price:{self.price:.2f})"

class Trade:
    def __init__(self, buyer, seller, commodity, price, quantity, timestamp=None):
        self.buyer, self.seller, self.commodity = buyer, seller, commodity
        self.price, self.quantity, self.timestamp = price, quantity, timestamp or time.time()
    def __repr__(self):
        ts = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
        return f"Trade({self.commodity}, Qty:{self.quantity}, Price:{self.price:.2f}, Buyer:{self.buyer}, Seller:{self.seller}, Time:{ts})"

# Order Book with Matching Logic
class OrderBook:
    def __init__(self, commodity):
        self.commodity = commodity; self.buy_orders, self.sell_orders = [], []
    def add_order(self, order):
        heapq.heappush(self.buy_orders if order.order_type=='buy' else self.sell_orders, ((-order.price if order.order_type=='buy' else order.price), order.timestamp, order))
    def _clean(self):
        while self.buy_orders and not self.buy_orders[0][2].active: heapq.heappop(self.buy_orders)
        while self.sell_orders and not self.sell_orders[0][2].active: heapq.heappop(self.sell_orders)
    def match_orders(self):
        trades = []; self._clean()
        while self.buy_orders and self.sell_orders:
            best_buy, best_sell = self.buy_orders[0][2], self.sell_orders[0][2]
            if not best_buy.active: heapq.heappop(self.buy_orders); continue
            if not best_sell.active: heapq.heappop(self.sell_orders); continue
            if best_buy.price >= best_sell.price:
                trade_price = best_buy.price if best_buy.price==best_sell.price else (best_buy.price+best_sell.price)/2
                if best_buy.price != best_sell.price:
                    print(f"Manual approval needed for trade between {best_buy.order_id} and {best_sell.order_id}... auto-approved.")
                qty = min(best_buy.remaining, best_sell.remaining)
                trades.append(Trade(best_buy.order_id, best_sell.order_id, self.commodity, trade_price, qty))
                best_buy.remaining -= qty; best_sell.remaining -= qty
                if best_buy.remaining==0: heapq.heappop(self.buy_orders)
                if best_sell.remaining==0: heapq.heappop(self.sell_orders)
            else:
                break
        return trades

# Trading Engine
class TradingEngine:
    def __init__(self):
        self.order_books = {}; self.trade_history = defaultdict(list); self.orders = {}; self.lock = threading.Lock()
    def get_order_book(self, commodity):
        if commodity not in self.order_books:
            self.order_books[commodity] = OrderBook(commodity)
        return self.order_books[commodity]
    def place_order(self, order):
        with self.lock:
            self.orders[order.order_id] = order
            self.get_order_book(order.commodity).add_order(order)
            print(f"Placed order: {order}")
    def match_all(self):
        with self.lock:
            for book in self.order_books.values():
                for trade in book.match_orders():
                    self.trade_history[trade.commodity].append(trade)
                    print(f"Executed {trade}")
    def cancel_all_orders(self):
        with self.lock:
            for order in self.orders.values(): order.active = False
            print("All pending orders have been canceled.")
    def get_market_value(self, commodity):
        history = self.trade_history.get(commodity, [])
        return history[-1].price if history else random.uniform(1.0, 100.0)
    def get_history(self, commodity):
        return self.trade_history.get(commodity, [])

# Auction & AuctionManager
class Auction:
    def __init__(self, seller_order, duration=5):
        self.seller_order = seller_order; self.commodity = seller_order.commodity; self.duration = duration
        self.start_time = time.time(); self.bids = []
    def add_bid(self, bid_order):
        self.bids.append(bid_order); print(f"Bid added to auction for {self.commodity}: {bid_order}")
    def is_expired(self): return time.time() >= self.start_time + self.duration
    def finalize(self): return max(self.bids, key=lambda o: o.price) if self.bids else None

class AuctionManager:
    def __init__(self, engine):
        self.engine = engine; self.active_auctions = {}; self.lock = threading.Lock()
    def start_auction(self, seller_order, duration=5):
        with self.lock:
            if seller_order.commodity in self.active_auctions: return None
            auction = Auction(seller_order, duration)
            self.active_auctions[seller_order.commodity] = auction
            print(f"Auction started for {seller_order.commodity} by {seller_order.order_id}")
            return auction
    def add_bid(self, commodity, bid_order):
        with self.lock:
            if commodity in self.active_auctions:
                self.active_auctions[commodity].add_bid(bid_order)
            else:
                print(f"No active auction for {commodity} to add bid.")
    def check_active(self, commodity):
        with self.lock: return self.active_auctions.get(commodity, None)
    def run(self):
        while simulation_running:
            with self.lock:
                expired = [c for c, a in self.active_auctions.items() if a.is_expired()]
                for c in expired:
                    auction = self.active_auctions.pop(c)
                    winning_bid = auction.finalize()
                    if winning_bid:
                        qty = min(auction.seller_order.remaining, winning_bid.remaining)
                        trade = Trade(winning_bid.order_id, auction.seller_order.order_id, c, winning_bid.price, qty)
                        auction.seller_order.remaining -= qty; winning_bid.remaining -= qty
                        self.engine.trade_history[c].append(trade)
                        print(f"Auction trade executed for {c}: {trade}")
                    else:
                        print(f"Auction for {c} ended with no bids.")
            time.sleep(0.5)

# Bot Implementation
class Bot:
    def __init__(self, bot_id, engine, commodity, objective, is_seller=True, time_limit=5, threshold=0.05):
        self.bot_id = bot_id; self.engine = engine; self.commodity = commodity; self.objective = objective
        self.is_seller = is_seller; self.time_limit = time_limit; self.target_price = objective['price']
        self.quantity = objective['quantity']; self.current_threshold = threshold
    def trade(self):
        # Seller auction mode (10% chance)
        if self.is_seller and random.random() < 0.1:
            order_price = self.target_price * (1 - self.current_threshold)
            order = Order(f"{self.bot_id}-{time.time()}", 'sell', self.commodity, self.quantity, order_price)
            self.engine.place_order(order)
            auction = auction_manager.start_auction(order, duration=self.time_limit)
            if auction:
                while simulation_running and auction_manager.check_active(self.commodity) is not None:
                    time.sleep(0.5)
                print(f"Seller {self.bot_id} auction completed for {self.commodity}.")
            return
        # Buyer auction mode
        if not self.is_seller:
            active_auction = auction_manager.check_active(self.commodity)
            if active_auction:
                bid_price = self.target_price * (1 + self.current_threshold)
                bid_order = Order(f"{self.bot_id}-{time.time()}", 'buy', self.commodity, self.quantity, bid_price)
                auction_manager.add_bid(self.commodity, bid_order)
                print(f"Buyer {self.bot_id} placed bid on auction for {self.commodity} at price {bid_price:.2f}.")
                return
        # Normal order trade
        start = time.time()
        order_price = self.target_price * (1 - self.current_threshold) if self.is_seller else self.target_price * (1 + self.current_threshold)
        order = Order(f"{self.bot_id}-{time.time()}", 'sell' if self.is_seller else 'buy', self.commodity, self.quantity, order_price)
        self.engine.place_order(order)
        while simulation_running and (time.time()-start < self.time_limit) and order.remaining > 0:
            time.sleep(0.5); self.engine.match_all()
        if not simulation_running:
            order.active = False; return
        if order.remaining > 0:
            order.active = False
            old = self.current_threshold
            self.current_threshold = min(self.current_threshold+0.05, 0.50) if self.is_seller else self.current_threshold+0.05
            print(f"{'Seller' if self.is_seller else 'Buyer'} {self.bot_id} timed out on {self.commodity}. Threshold increased from {old:.0%} to {self.current_threshold:.0%}.")
        else:
            print(f"Bot {self.bot_id} successfully traded on {self.commodity} at price {order_price:.2f}.")

# Utility Functions
def generate_random_product_names(n=10):
    adjectives = ["Cool","Amazing","Fantastic","Ultra","Super","Mega","Hyper","Smart","Eco","Prime"]
    nouns = ["Widget","Gadget","Device","Item","Tool","Gear","Product","Instrument","Module","System"]
    return list({f"{random.choice(adjectives)} {random.choice(nouns)}" for _ in range(n)})
bot_counter = 0
def create_random_bot(engine, product_list):
    global bot_counter; bot_counter += 1
    bot_id = f"Bot{bot_counter}"
    commodity = random.choice(product_list)
    is_seller = random.choice([True, False])
    quantity = random.randint(1,20)
    target_price = round(engine.get_market_value(commodity),2)
    objective = {'quantity': quantity, 'price': target_price}
    threshold = random.uniform(0.01, 0.10) if is_seller else random.uniform(0.01, 0.20)
    return Bot(bot_id, engine, commodity, objective, is_seller, 5, threshold)

# Visualization
def visualize_all_commodities(engine):
    plt.figure(figsize=(12,6))
    for commodity, trades in engine.trade_history.items():
        if trades:
            times = [t.timestamp for t in trades]
            prices = [t.price for t in trades]
            plt.plot(times, prices, marker='o', label=commodity)
    plt.xlabel("Time (Unix Timestamp)"); plt.ylabel("Trade Price")
    plt.title("Trade History for All Commodities Over the Simulation")
    plt.legend(); plt.tight_layout(); plt.savefig('trade_history.png')

# Bot Worker Function
simulation_running = True
def bot_worker(engine, product_list):
    while simulation_running:
        create_random_bot(engine, product_list).trade()
        time.sleep(random.uniform(0.1,0.5))
