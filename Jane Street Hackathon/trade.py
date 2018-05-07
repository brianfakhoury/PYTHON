# Python3
'''HFT trading script python v=3.x'''
# from __future__ import print_function

import sys
import socket
import time
import json
import math
import numpy as np

# define the average number of transactions_per_tick, to be used in the max array length
transactions_per_tick = 3

# tracking 1 minutes worth of data, assuming 3 buys / sells per tick
max_length = 1000 * transactions_per_tick
# tracking 5 seconds

buy_percent = 0.03 / 100
sell_percent = 0.03 / 100

VWAP = True  # define our trading strategy
# define which securities we want to trade
VWAP_stocks = ["AAPL", "GOOG", "MSFT", "MSFT"]

trade_port = 25000


class Market:
    '''Market tracking class'''

    def __init__(self, exchange):
        self.all_equities = []
        self.all_bonds = []
        self.all_etf = []
        self.half_spreads = {}
        self.running_avg = {}
        self.highest_buys = {"AAPL": 0, "GOOG": 0, "MSFT": 0}
        self.cheapest_sells = {"AAPL": 0, "GOOG": 0, "MSFT": 0}
        self.exchange = exchange
        self.price_history = {"BOND": {"price": [], "volume": []}, "NOKFH": {"price": [], "volume": []},
                              "NOKUS": {"price": [], "volume": []}, "AAPL": {"price": [], "volume": []},
                              "MSFT": {"price": [], "volume": []}, "GOOG": {"price": [], "volume": []},
                              "XLK": {"price": [], "volume": []}}
        self.running_average = {
            "BOND": 0, "NOKFH": 0, "NOKUS": 0, "AAPL": 0, "MSFT": 0, "GOOG": 0, "XLK": 0}
        self.cash_tracker = {"BOND": 0, "NOKFH": 0, "NOKUS": 0,
                             "AAPL": 0, "MSFT": 0, "GOOG": 0, "XLK": 0}


class Portfolio:
    '''General portfolio class'''

    def __init__(self):
        self.our_orders = {}
        self.security_limits = {"BOND": 100, "AAPL": 100, "MSFT": 100, "GOOG": 100, "XLK": 100,
                                "NOKFH": 10, "NOKUS": 10}  # Maximum allowed to buy for each securityLimit
        self.fair_price_etf = {}
        self.latest_order = time.time()
        self.positions = {}
        self.cancelling_orders = []
        self.order_id = 0

    def hold_server(self):
        '''Holds up script pipeline till server has passed 10ms'''
        while time.time() - self.latest_order < .01:
            continue
        self.latest_order = time.time()
        return

    def cancel_dated_orders(self, ticker, fair_price, pos, neg):
        for order_id in self.our_orders:
            order = self.our_orders[order_id]
            if order_id in self.cancelling_orders or order.ticker != ticker:
                continue
            if order.way == "BUY":
                order_price = order.price * (1 + pos)
            elif order.way == "SELL":
                order_price = order.price * (1 - neg)
            if abs(fair_price - order_price) >= .01 * fair_price:
                json_string = '{"type": "cancel", "order_id": ' + \
                    str(order_id) + '} '
                self.hold_server()
                print(json_string, file=sys.stderr)
                print(json_string, file=exchange)
                self.cancelling_orders.append(order_id)

    def outstanding_orders(self, ticker, way):
        result = 0
        for order_id in self.our_orders:
            order = self.our_orders[order_id]
            if order.ticker == ticker and order.way == way:
                result += order.amount
        return result


class Order:
    '''Create a new order object'''

    def __init__(self, ticker, amount, price, way, convert_etf=False):
        self.ticker = ticker
        self.amount = amount
        self.price = price
        self.way = way
        self.convert_etf = convert_etf

    def fill(self, fill_num):
        if self.convert_etf:
            return
        self.amount -= fill_num
        if self.way == "BUY":
            portfolio.positions[self.ticker] += fill_num
        elif self.way == "SELL":
            portfolio.positions[self.ticker] -= fill_num


def connect(address):
    """returns (socket connection, s.makefile()"""
    sok = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sok.connect((address, trade_port))
    return (sok, sok.makefile('rw', 1))


def prepare_order(symbol, fair_price, sell_percent, buy_percent):
    buy = portfolio.positions[symbol] + \
        portfolio.outstanding_orders(symbol, "BUY")
    sell = -1 * portfolio.positions[symbol] + \
        portfolio.outstanding_orders(symbol, "SELL")
    limit = portfolio.security_limits[symbol]

    buyAmount = limit - buy
    sellAmount = limit - sell

    if buy < limit and buyAmount > 0:
        buyPrice = math.floor(fair_price * (1 - buy_percent))
        order_sec(symbol, "BUY", buyPrice, buyAmount)

    if sell < limit and sellAmount > 0:
        sellPrice = math.ceil(fair_price * (1 + sell_percent))
        order_sec(symbol, "SELL", sellPrice, sellAmount)


def order_sec(symbol, direction, price, amount):
    if price > 12000 and direction == "BUY":
        return
    id = portfolio.order_id
    portfolio.order_id += 1
    json_string = '{"type": "add", "order_id": ' + str(id) + ',"symbol": "' + symbol + \
        '", "dir": "' + direction + '", "price": ' + \
        str(price) + ', "size" : ' + str(amount) + '}'
    print(json_string, file=sys.stderr)
    portfolio.hold_server()
    print(json_string, file=exchange)
    portfolio.our_orders[id] = Order(symbol, amount, price, direction)


def parse_data(msg):
    dat = json.loads(msg)
    if dat['type'] == "reject" and dat['error'] == "TRADING_CLOSED":
        sys.exit(2)
    elif dat['type'] == 'out':
        order_id = dat["order_id"]
        if order_id in portfolio.cancelling_orders:
            portfolio.cancelling_orders.remove(order_id)
            del portfolio.our_orders[order_id]
    elif dat['type'] == "fill":
        order = portfolio.our_orders[dat['order_id']]
        sym = dat["symbol"]
        if dat['dir'] == "BUY":
            market.cash_tracker[sym] = market.cash_tracker[sym] - \
                dat["price"] * dat["size"]
        if dat['dir'] == "SELL":
            if portfolio.positions[sym] != 0:
                costPerShare = market.cash_tracker[sym] / \
                    portfolio.positions[sym]
                profit = (dat["price"] + costPerShare) * dat["size"]
                market.cash_tracker[sym] = market.cash_tracker[sym] + \
                    costPerShare * dat["size"]
                print("The profit on the last sell was %d", profit)

        order.fill(dat['size'])
#    elif dat['type'] == "trade":

    elif dat['type'] == "book":
        sym = dat['symbol']
        # only compute the moving average of the stocks we care about
        if sym in VWAP_stocks:
            # buy contains price volume paired data -> [(val1,size1),(val2,size2)]
            buy = dat['buy']
            sell = dat['sell']

            for price, volume in buy:
                # keep the length constrained by max_length
                if len(market.price_history[sym]['price']) > max_length:
                    del market.price_history[sym]['price'][0]
                    del market.price_history[sym]['volume'][0]

                # add the new data
                market.price_history[sym]['price'].append(price)
                market.price_history[sym]['volume'].append(volume)

            for price, volume in sell:
                if len(market.price_history[sym]['price']) > max_length:
                    del market.price_history[sym]['price'][0]
                    del market.price_history[sym]['volume'][0]

                market.price_history[sym]['price'].append(price)
                market.price_history[sym]['volume'].append(volume)

            # compute the weighted average and store it in the running_average
            market.running_average[sym] = np.average(
                market.price_history[sym]['price'], weights=market.price_history[sym]['volume'])

        sell = dat['sell']
        buy = dat['buy']
        cheapSell = 10000000
        highBuy = 0
        for (val, size) in sell:
            if val < cheapSell:
                cheapSell = val
        for (val, size) in buy:
            if val > highBuy:
                highBuy = val
        market.highest_buys[sym] = highBuy
        market.cheapest_sells[sym] = cheapSell

    elif dat['type'] == "hello":
        sym = dat['symbols']
        for info in sym:
            asym = info['symbol']
            position = info['position']
            portfolio.positions[asym] = position


def main():
    '''Start the running bot'''
    global exchange
    global market
    global portfolio
    s, exchange = connect(sys.argv[1])
    market = Market(exchange)
    jsn = '{"type": "hello", "team": "THETRADERJOES"}'
    print(jsn, file=exchange)
    xcg_hello = exchange.readline().strip()
    print("The exchange said: {}".format(str(xcg_hello)), file=sys.stderr)
    portfolio = Portfolio()
    parse_data(xcg_hello)
    print("Entering trade loop!", file=sys.stderr)

    VWAP = False
    tradeBond = True
    tradeSecurities = False
    while 1:

        message = exchange.readline().strip()
        parse_data(message)

        if VWAP:
            for sec in VWAP_stocks:
                fair_price = market.running_average[sec]

                # check to see if the previous orders we have placed are still within our range
                portfolio.cancel_dated_orders(
                    sec, fair_price, buy_percent, sell_percent)

                # Now place orders with any funds we have remaining
                prepare_order(sec, fair_price, sell_percent, buy_percent)

        if tradeBond:
            prepare_order('BOND', 1000, .001, .001)

        if tradeSecurities:
            # for sym in VWAP_stocks:
            sym = "GOOG"
            if market.highest_buys[sym] != 0 and market.cheapest_sells[sym] != 0:
                # print("This is highest_buys", market.highest_buys[sym])
                # print("This is cheapest_sells", market.cheapest_sells[sym])
                current_price = (
                    market.highest_buys[sym] + market.cheapest_sells[sym]) / 2
                portfolio.cancel_dated_orders(sym, current_price, .01, .01)
                prepare_order(sym, current_price, .0005, .0005)

        if message is not None:
            # chuck away book messages for now
            m_type = json.loads(message)['type']
            if m_type == 'book' or m_type == 'trade' or m_type == 'ack':
                pass
            else:
                print("> %s" % str(message), file=sys.stderr)
        # have we got a message ?


if __name__ == "__main__":
    main()
