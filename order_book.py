# order_book.py
import heapq
from models import Order, Trade

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
