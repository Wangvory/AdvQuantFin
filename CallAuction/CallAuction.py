'''
Exercise 1. Call Auction. With the Excel spreadsheet distributed in class, showing how the call auction works, write a general purpose call auction computer program in Python that does the following:
• Read from a file the buy and sell orders. Fields within the file should consist of the price, side, quantity.
• Determine the opening price, i.e. the price that matches all buy and sell pre-orders.
• Determine the initial opening order book after the call auction.
'''
import pandas as pd
Order = pd.read_excel('CallAuction.xlsx',sheet_name='Sheet2')
records=Order.values.tolist()
records.sort(key=(lambda x: x[0]), reverse=True)  # Sort by Price

def listcreation():
    buylist = {}
    lastbuy = 0
    for price, amount,side in records:
        if (side == "Buy"):
            lastbuy += amount
        buylist[price] = lastbuy

    selllist = {}
    lastsell = 0
    for price, amount,side in records[::-1]:
        if (side == "Sell"):
            lastsell += amount
        selllist[price] = lastsell
    return buylist,selllist

def pricerender(buylist,selllist):
    prices=list(buylist)
    max_amount=0
    best_price = 0
    for price in prices:
        if(min(buylist[price],selllist[price])>max_amount):
            best_price=price
            max_amount=min(buylist[price],selllist[price])
    orderbook=[]
    print('The Best Price for Call Auction is',best_price,'\nThe Amount Traded Under that Price is',max_amount)
    #Buylist and Selllist quant are different
    #Get First Item
    if buylist[best_price]==max_amount:
        orderbook.append([best_price,selllist[best_price]-max_amount,'Sell'])
    else:
        orderbook.append([best_price, buylist[best_price] - max_amount, 'Buy'])

    for price, amount,side in records:
        if side =='Buy' and price < best_price:
            orderbook.append([price, amount,side])
        elif side =='Sell' and price > best_price:
            orderbook.append([price, amount, side])
    orderbook.sort(key=(lambda x: x[0]), reverse=True)
    print('After Auction, the unexcused orderbook \n',pd.DataFrame(orderbook,columns=('Price','Quantity','Side')))


buylist,selllist  = listcreation()
pricerender(buylist,selllist)