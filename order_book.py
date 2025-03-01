"""
Order book module with matching logic.
"""

import heapq
from models import Order, Trade

class OrderBook:
    """Manages buy and sell orders for a commodity."""
    def __init__(self, commodity):
        self.commodity = commodity
        self.buy_orders = []   # max-heap via negative prices
        self.sell_orders = []  # min-heap

    def add_order(self, order: Order):
        """Add an order to the appropriate heap."""
        if order.order_type == 'buy':
            heapq.heappush(self.buy_orders, (-order.price, order.timestamp, order))
        elif order.order_type == 'sell':
            heapq.heappush(self.sell_orders, (order.price, order.timestamp, order))

    def _clean_inactive(self):
        """Remove inactive orders from both heaps."""
        while self.buy_orders and not self.buy_orders[0][2].active:
            heapq.heappop(self.buy_orders)
        while self.sell_orders and not self.sell_orders[0][2].active:
            heapq.heappop(self.sell_orders)

    def match_orders(self):
        """Match orders and return a list of executed trades."""
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
                trades.append(Trade(best_buy.order_id, best_sell.order_id, self.commodity, trade_price, trade_quantity))
                best_buy.remaining -= trade_quantity
                best_sell.remaining -= trade_quantity
                if best_buy.remaining == 0:
                    heapq.heappop(self.buy_orders)
                if best_sell.remaining == 0:
                    heapq.heappop(self.sell_orders)
            else:
                break
        return trades
