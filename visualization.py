"""
Visualization module to plot the trade history.
"""
import time
import matplotlib.pyplot as plt

def visualize_all_commodities(engine):
    """
    Generate a plot of trade history for all commodities and save it to a file.
    """
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
    plt.savefig(f'output/trade_history_{int(time.time())}.png')
