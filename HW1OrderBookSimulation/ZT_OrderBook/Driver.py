from Api import *
from DateTimeUtils import *


def main():
    trace = True

    # instantiate call to API
    #
    api = Api()

    # load appropriate h5 file corresponding to a instrument and specific day
    #
    instruments = Api.get_instrument_names()
    year, month, day = '2018', '06', '13'
    api.load_h5(instruments[3], year, month, day)

    # get timestamps
    #
    timestamps = api.get_timestamps()
    if trace:
        print(len(timestamps))
        print(timestamps[0], convert_timestamp_to_dtstring(timestamps[0]))
        print(timestamps[-1], convert_timestamp_to_dtstring(timestamps[-1]))

    index = 0
    for timestamp in timestamps:
        print(index, timestamp, convert_timestamp_to_dtstring(timestamp))
        index += 1

    # get order_book
    # get book_balance
    # get weighted_book_balance
    #
    order_book = api.get_order_book(timestamps[5207])
    print(order_book)
    Api.plot_order_book(order_book)
    order_book = api.get_order_book(timestamps[5208])
    print(order_book)
    Api.plot_order_book(order_book)

    # order_book2 = api2.get_order_book(timestamps2[9000])
    # print(order_book2)
    # Api.plot_order_book(order_book2)

    # get trades
    #
    trades = api.get_trades(timestamp=timestamps[5207])
    if trace:
        print(trades)

    # get limit_flows
    #
    order_book_start = api.get_order_book(timestamps[5207])
    order_book_end = api.get_order_book(timestamps[5208])
    trades = api.get_trades(timestamps[5207])

    limit_flows = api.get_limit_flows(timestamp_start=timestamps[5207],
                                      timestamp_end=timestamps[5208])

    # Api.plot_flows(limit_flows)
    if trace:
        print('OrderBookStart', order_book_start)
        print('OrderBookEnd', order_book_end)
        print('Trades', trades)
        print('LimitFlows', limit_flows)


if __name__ == '__main__':
    main()
