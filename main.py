"""
Main entry point for the trading simulation.
Reads simulation parameters from environment variables.
"""

import time
import threading
import os
from engine import TradingEngine
from auction import AuctionManager, Auction
from utils import generate_random_product_names, create_random_bot
from visualization import visualize_all_commodities

POOL_SIZE = int(os.environ.get("POOL_SIZE", "200"))
SIMULATION_DURATION = int(os.environ.get("SIMULATION_DURATION", "120"))
NUM_PRODUCTS = int(os.environ.get("NUM_PRODUCTS", "10"))

simulation_running = True

def simulation_running_func():
    """Return the current simulation running state."""
    return simulation_running

def bot_worker(engine, product_list, auction_manager):
    """Worker function to continuously run a bot."""
    while simulation_running_func():
        bot = create_random_bot(engine, product_list)
        bot.trade(auction_manager, simulation_running_func)
        time.sleep(0.1)

def main():
    global simulation_running
    engine = TradingEngine()
    product_names = generate_random_product_names(NUM_PRODUCTS)

    # Start AuctionManager thread.
    auction_manager = AuctionManager(engine)
    auction_thread = threading.Thread(target=auction_manager.run, args=(simulation_running_func,))
    auction_thread.start()

    # Initial Demo: Manual Orders & Auction
    from models import Order
    demo_orders = [
        Order("O1", "buy", "Widget", 10, 50.0),
        Order("O2", "sell", "Widget", 5, 48.0),
        Order("O3", "sell", "Widget", 7, 49.0),
    ]
    for order in demo_orders:
        engine.place_order(order)
    engine.match_all()

    # Auction demo for Gadget.
    from models import Order as OrderModel
    auction_demo = Auction(OrderModel("A0", "sell", "Gadget", 5, 60.0), duration=5)
    with auction_manager.lock:
        auction_manager.active_auctions["Gadget"] = auction_demo
    auction_demo.add_bid(OrderModel("A1", "buy", "Gadget", 5, 75.0))
    auction_demo.add_bid(OrderModel("A2", "buy", "Gadget", 5, 80.0))
    time.sleep(auction_demo.duration + 1)
    with auction_manager.lock:
        if "Gadget" in auction_manager.active_auctions:
            auction_manager.active_auctions.pop("Gadget")
    print("Auction demo finalized.")

    # Asynchronous Bot Simulation
    pool_size = POOL_SIZE
    threads = []
    for _ in range(pool_size):
        t = threading.Thread(target=bot_worker, args=(engine, product_names, auction_manager))
        threads.append(t)
        t.start()

    time.sleep(SIMULATION_DURATION)
    simulation_running = False
    engine.cancel_all_orders()

    for t in threads:
        t.join()
    auction_thread.join()

    visualize_all_commodities(engine)

if __name__ == "__main__":
    main()
