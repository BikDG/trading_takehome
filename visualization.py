# visualization.py
import matplotlib.pyplot as plt
import time

def visualize_all_commodities(engine):
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
    time_sec = time.time()
    plt.savefig(f'output/trade_history{time_sec}.png')
