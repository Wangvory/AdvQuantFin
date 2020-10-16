import matplotlib.pyplot as plt
import pandas as pd
import DateTimeUtils


class Api:
    instruments = {'ES': {'name': 'S&P Mini', 'ticksize': 0.25},
                   'TN': {'name': 'Ultra 10y', 'ticksize': 1.0 / 64.0},
                   'UB': {'name': 'Ultra Bond', 'ticksize': 1.0 / 32.0},
                   'ZT': {'name': 'Tsy 2y', 'ticksize': 1.0 / 256.0},
                   'ZF': {'name': 'Tsy 5y', 'ticksize': 1.0 / 128.0},
                   'ZN': {'name': 'Tsy 10y', 'ticksize': 1.0 / 64.0},
                   'ZB': {'name': 'Tsy 30y', 'ticksize': 1.0 / 32.0}}
    instrument = None

    # region Static methods

    @staticmethod
    def get_instruments():
        return Api.instruments

    @staticmethod
    def get_instrument_names():
        return list(Api.instruments.keys())

    @staticmethod
    def get_instrument_name(instrument):
        return Api.instruments[instrument]['name']

    @staticmethod
    def get_instrument_ticksize(instrument):
        return Api.instruments[instrument]['ticksize']

    @staticmethod
    def is_instrument_valid(instrument):
        return instrument in Api.get_instrument_names()

    @staticmethod
    def get_filename(instrument, year, month, day):
        Api.instrument = instrument
        return 'TickData_ZT/' + instrument + '/' + year + '/' + month + '/' + day + '/foreground.h5'

    # endregion

    # region Constructor and load_h5
    def __init__(self):
        self.df = ''
        self.append_number = None

    def load_h5(self, instrument, year, month, day):
        # get the filename and read into a dataframe
        #
        filename = Api.get_filename(instrument, year, month, day)
        df1 = pd.read_hdf(filename, 'main')
        columns = df1.columns

        # make sure that all columns have the same append number
        # store that append number
        #
        for column_name in columns:
            if column_name == 'timestamp': continue
            number = column_name[column_name.rfind('_') + 1:]
            if self.append_number is None:
                self.append_number = number
            elif self.append_number != number:
                raise Exception("Not all columns have the same end number")

        # set the dataframe index to the timestamp
        self.df = df1.set_index("timestamp", drop=False)

    # endregion

    def get_columns(self):
        return self.df.columns

    def get_timestamps(self):
        return self.df['timestamp'].tolist()

    def get_order_book(self, timestamp, depth_max=10):
        sides = ['bid', 'ask']
        order_book = {}
        for s in sides:
            for d in range(depth_max):
                column = 'book_price_' + s + '_' + str(d) + '_' + str(self.append_number)
                price = self.df.loc[timestamp, column]
                column = 'book_qty_' + s + '_' + str(d) + '_' + str(self.append_number)
                qty = self.df.loc[timestamp, column]
                column = 'book_count_' + s + '_' + str(d) + '_' + str(self.append_number)
                count = self.df.loc[timestamp, column]
                order_book[s + '_' + str(d)] = (price, qty, count)
        order_book['instrument'] = Api.instrument
        order_book['depth_max'] = depth_max
        order_book['timestamp'] = timestamp
        order_book['datetime'] = DateTimeUtils.convert_timestamp_to_dtstring(timestamp)
        return order_book

    def get_order_book_balance(self, order_book):
        order_book_balance = 0.0
        for d in range(order_book['depth_max']):
            order_book_balance += order_book['ask_' + str(d)][1] - order_book['bid_' + str(d)][1]
        order_book['balance'] = order_book_balance
        return order_book_balance

    def get_weighted_order_book_balance(self, order_book):
        mid_price = (order_book['bid_0'][0] + order_book['ask_0'][0])/2.0
        weighted_order_book_balance = 0.0
        sizes = 0.0
        for d in range(order_book['depth_max']):
            weighted_order_book_balance += (order_book['ask_' + str(d)][0] - mid_price) * order_book['ask_' + str(d)][1]
            weighted_order_book_balance += (order_book['bid_' + str(d)][0] - mid_price) * order_book['bid_' + str(d)][1]
            sizes += order_book['ask_' + str(d)][1] + order_book['bid_' + str(d)][1]
        order_book['weighted_balance'] = mid_price + weighted_order_book_balance/sizes
        return weighted_order_book_balance

    def get_trades(self, timestamp):
        trade_types = ['buy', 'sell']
        trades = {}
        column = 'trade_price_' + str(self.append_number)
        price = self.df.loc[timestamp, column]
        trades['price'] = price
        for tt in trade_types:
            column = 'trade_qty_' + tt + '_' + str(self.append_number)
            qty = self.df.loc[timestamp, column]
            column = 'trade_count_' + tt + '_' + str(self.append_number)
            count = self.df.loc[timestamp, column]
            trades[tt] = (qty, count)
        return trades

    def get_all_trades(self, trade_types):
        timestamps = self.get_timestamps()
        trades = {}
        for timestamp in timestamps:
            trades[timestamp] = self.get_trades(trade_types, timestamp)
        return trades

    def get_limit_flows(self, timestamp_start, timestamp_end, depth_max=10):
        order_book_start = self.get_order_book(timestamp_start, depth_max)
        order_book_end = self.get_order_book(timestamp_end, depth_max)
        trades = self.get_trades(timestamp_start)

        start, end = {}, {}
        depth_max = order_book_start['depth_max']
        for i, d in enumerate(range(depth_max - 1, -1, -1)):
            start[order_book_start['bid_' + str(d)][0]] = order_book_start['bid_' + str(d)][1]
        for i, d in enumerate(range(depth_max)):
            start[order_book_start['ask_' + str(d)][0]] = order_book_start['ask_' + str(d)][1]

        depth_max = order_book_end['depth_max']
        for i, d in enumerate(range(depth_max - 1, -1, -1)):
            end[order_book_end['bid_' + str(d)][0]] = order_book_end['bid_' + str(d)][1]
        for i, d in enumerate(range(depth_max)):
            end[order_book_end['ask_' + str(d)][0]] = order_book_end['ask_' + str(d)][1]

        # intersection of two order books on prices
        prices = []
        for item in start.keys():
            if item in end.keys():
                prices.append(item)

        # assemble flows on prices with trades
        limit_flows = {}
        for price in prices:
            if price in end.keys():
                limit_flows[price] = end[price]
        for price in prices:
            if price in start.keys():
                limit_flows[price] -= start[price]
        for price in prices:
            if price == trades['price']:
                limit_flows[price] += trades['buy'][0] + trades['sell'][0]
        return limit_flows

    @staticmethod
    def plot_order_book(order_book):
        depth_max = order_book['depth_max']

        bid_prices, bid_sizes = [], []
        ask_prices, ask_sizes = [], []
        for i, d in enumerate(range(depth_max - 1, -1, -1)):
            bid_prices.append(order_book['bid_' + str(d)][0])
            bid_sizes.append(order_book['bid_' + str(d)][1])
        for i, d in enumerate(range(depth_max)):
            ask_prices.append(order_book['ask_' + str(d)][0])
            ask_sizes.append(order_book['ask_' + str(d)][1])

        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.set_facecolor((0.0, 0.0, 0.0))

        tick_size = Api.instruments[Api.instrument]['ticksize']
        prices = [min(bid_prices) - tick_size]
        prices += bid_prices
        prices.append(max(bid_prices))
        sizes = [0]
        sizes += bid_sizes
        sizes.append(0)
        plt.step(prices, sizes, label='bid', color='b')

        prices = [min(ask_prices)]
        prices.extend([x + tick_size for x in ask_prices])
        prices.append(max(ask_prices) + tick_size)
        prices.append(max(ask_prices) + tick_size)
        sizes = [0]
        sizes += ask_sizes
        sizes.append(ask_sizes[-1])
        sizes.append(0)
        plt.step(prices, sizes, label='ask', color='r')

        title = f"OrderBook : {order_book['instrument']} : {order_book['datetime']}"

        plt.title(title)
        plt.xlabel('price')
        plt.ylabel('size')
        plt.legend(fancybox=True)
        plt.xlim(min(bid_prices) - 2 * Api.instruments[Api.instrument]['ticksize'],
                 max(ask_prices) + 2 * Api.instruments[Api.instrument]['ticksize'])
        plt.ylim(0, 1.40 * max(max(bid_sizes), max(ask_sizes)))

        mid = (max(bid_prices + min(ask_prices))) / 2.0
        ax.vlines(x=mid, ymin=0, ymax=1.20 * max(max(bid_sizes), max(ask_sizes)), linewidth=1, color='w')

        txt = f'Mid={mid}'
        if 'balance' in order_book.keys():
            txt += f"\nBalance={order_book['balance']}"
        if 'weighted_balance' in order_book.keys():
            txt += f"\nWeighted Balance={order_book['weighted_balance']}"
        plt.figtext(mid, 1.20 * max(max(bid_sizes), max(ask_sizes)), txt, transform=ax.transData,
                    horizontalalignment='center', fontsize=9, multialignment='center',
                    bbox=dict(boxstyle="round", facecolor='#D8D8D8', ec="0.5", pad=0.5, alpha=1.0), fontweight='bold')

        plt.show()

