'''
Exercise 2. OrderBook. Using your knwledge of Python which has built in data structures for lists and dictionaries,
develop a Python class named OrderBook, that can model and store an order book. Please note the following:
• OrderBook should be able to handle both the bid and ask sides.
• OrderBook should be able to handle both market and limit orders. A market order should be matched immediately, while
the limit order may or may not be filled fully. A partially filled or totally unfilled order becomes part of the
order book.
• Any any time, be able to output the best bid, best ask, bid/ask spread, and all market depth.
• Any any price, ensure time priority of orders by matching orders that were placed first.
'''

import enum
import queue
import time
from collections import defaultdict

class Side(enum.Enum):
    BUY = 0
    SELL = 1


def get_timestamp():
    """ Microsecond timestamp """
    return int(1e6 * time.time())


class OrderBook(object):
    def __init__(self):
        """
        Orders stored as two default dicts of {price:[orders at price]}
        Orders sent to OrderBook through OrderBook.unprocessed_orders queue
        """
        self.bid_prices = []
        self.bid_sizes = []
        self.offer_prices = []
        self.offer_sizes = []
        self.bids = defaultdict(list)
        self.offers = defaultdict(list)
        self.unprocessed_orders = queue.Queue()
        self.trades = queue.Queue()
        self.order_id = 0

    def new_order_id(self):
        self.order_id += 1
        return self.order_id

    @property
    def max_bid(self):
        if self.bids:
            return max(self.bids.keys())
        else:
            return 0.
    @property
    def min_offer(self):
        if self.offers:
            return min(self.offers.keys())
        else:
            return float('inf')

    def process_order(self, incoming_order):
        """ Main processing function. If incoming_order matches delegate to process_match."""
        incoming_order.timestamp = get_timestamp()
        incoming_order.order_id = self.new_order_id()
        if incoming_order.side == Side.BUY:
            if incoming_order.price >= self.min_offer and self.offers:
                self.process_match(incoming_order)
            else:
                self.bids[incoming_order.price].append(incoming_order)
        else:
            if incoming_order.price <= self.max_bid and self.bids:
                self.process_match(incoming_order)
            else:
                self.offers[incoming_order.price].append(incoming_order)

    def process_match(self, incoming_order):
        """ Match an incoming order against orders on the other side of the book, in price-time priority."""
        levels = self.bids if incoming_order.side == Side.SELL else self.offers
        prices = sorted(levels.keys(), reverse=(incoming_order.side == Side.SELL))

        def price_doesnt_match(book_price):
            if incoming_order.side == Side.BUY:
                return incoming_order.price < book_price
            else:
                return incoming_order.price > book_price

        for (i, price) in enumerate(prices):
            if (incoming_order.size == 0) or (price_doesnt_match(price)):
                break
            orders_at_level = levels[price]
            for (j, book_order) in enumerate(orders_at_level):
                if incoming_order.size == 0:
                    break
                trade = self.execute_match(incoming_order, book_order)
                incoming_order.size = max(0, incoming_order.size - trade.size)
                book_order.size = max(0, book_order.size - trade.size)
                self.trades.put(trade)
            levels[price] = [o for o in orders_at_level if o.size > 0]
            if len(levels[price]) == 0:
                levels.pop(price)

        # If the incoming order has not been completely matched, add the remainder to the order book
        if incoming_order.size > 0:
            same_side = self.bids if incoming_order.side == Side.BUY else self.offers
            same_side[incoming_order.price].append(incoming_order)

    def execute_match(self, incoming_order, book_order):
        trade_size = min(incoming_order.size, book_order.size)
        return Trade(incoming_order.side, book_order.price, trade_size, incoming_order.order_id, book_order.order_id)

    def book_summary(self):
        self.bid_prices = sorted(self.bids.keys(), reverse=True)
        self.offer_prices = sorted(self.offers.keys())
        self.bid_sizes = [sum(o.size for o in self.bids[p]) for p in self.bid_prices]
        self.offer_sizes = [sum(o.size for o in self.offers[p]) for p in self.offer_prices]

    def show_book(self):
        self.book_summary()
        print('Sell side:')
        if len(self.offer_prices) == 0:
            print('EMPTY')
        for i, price in reversed(list(enumerate(self.offer_prices))):
            print('{0}) Price={1}, Total units={2}'.format(i + 1, self.offer_prices[i], self.offer_sizes[i]))
        print('Buy side:')
        if len(self.bid_prices) == 0:
            print('EMPTY')
        for i, price in enumerate(self.bid_prices):
            print('{0}) Price={1}, Total units={2}'.format(i + 1, self.bid_prices[i], self.bid_sizes[i]))
        print()


class LimitOrder(object):
    def __init__(self,side,price,size,timestamp=None,order_id=None):
        self.side = side
        self.size = size
        self.price = price
        self.timestamp = timestamp
        self.order_id = order_id
    def __repr__(self):
        return '{0} {1} units at {2}'.format(self.side, self.size, self.price)

class MarketOrder(object):
    def __init__(self,side,size,timestamp=None,order_id=None):
        self.side = side
        self.size = size
        self.timestamp = timestamp
        self.order_id = order_id
        if side == Side.BUY:
            self.price = float('inf')
        else:
            self.price = 0.
    def __repr__(self):
        return '{0} {1} units at {2}'.format(self.side, self.size, 'MarketPrice')

class Trade(object):
    def __init__(self, incoming_side, incoming_price, trade_size, incoming_order_id, book_order_id):
        self.side = incoming_side
        self.price = incoming_price
        self.size = trade_size
        self.incoming_order_id = incoming_order_id
        self.book_order_id = book_order_id

    def __repr__(self):
        return 'Executed: {0} {1} units at {2}'.format(self.side, self.size, self.price)


if __name__ == '__main__':
    print('Example(No Opponent):')
    ob = OrderBook()
    orders = [LimitOrder(Side.BUY, 1., 2),
              LimitOrder(Side.BUY, 2., 3, 2),
              LimitOrder(Side.BUY, 1., 4, 3)]
    print('We receive these orders:')
    for order in orders:
        print(order)
        ob.unprocessed_orders.put(order)
    while not ob.unprocessed_orders.empty():
        ob.process_order(ob.unprocessed_orders.get())
    print()
    print('Resulting order book:')
    ob.show_book()
    print('Now Its Your Turn')
    ob = OrderBook()
    orders = [LimitOrder(Side.BUY, 12.23, 10),
              LimitOrder(Side.BUY, 12.31, 20),
              LimitOrder(Side.SELL, 13.55, 5),
              LimitOrder(Side.BUY, 12.23, 5),
              LimitOrder(Side.BUY, 12.25, 15),
              LimitOrder(Side.SELL, 13.31, 5),
              LimitOrder(Side.BUY, 12.25, 30),
              LimitOrder(Side.SELL, 13.31, 5)]
    print('We receive these orders:')
    for order in orders:
        print(order)
        ob.unprocessed_orders.put(order)
    while not ob.unprocessed_orders.empty():
        ob.process_order(ob.unprocessed_orders.get())
    print()
    print('Resulting order book:')
    ob.show_book()
    Type = input('What Kind Of Order you want Place? Market/Limit')
    Sides = input('What Side you want to choose? Please Enter the number, BUY=0/SELL=1')
    SideS=Side(int(Sides))
    Quant = int(input('How many stocks you want to trade?'))
    if Type == 'Limit':
        price =input('Cool, whats the price?')
        offer_order = LimitOrder(SideS, price, Quant)
    elif Type == 'Market':
        offer_order = MarketOrder(SideS, Quant)
    print('Now we get a order {}'.format(offer_order))
    print('Here is the new order book')
    ob.unprocessed_orders.put(offer_order)
    ob.process_order(ob.unprocessed_orders.get())
    ob.show_book()
