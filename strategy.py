import math
import backtrader as bt
from datetime import datetime

# create feed data
def stock(symbol = '0939.HK',
          start = datetime(2011, 1, 1),
          end = datetime(2012, 12, 31)):
    data = bt.feeds.YahooFinanceData(dataname=symbol, 
                                     fromdate=start,
                                     todate=end)
    return data

########################
# Sample 1 Create a Stratey
class TestStrategy(bt.Strategy):
#     params = (
#         ('exitbars',5),
#     )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else: # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
    def next(self):
#         self.log('Close, %.2f' % self.dataclose[0])
        if self.order:
            return
        if not self.position:
            if self.dataclose[0] < self.dataclose[-1]:
                if self.dataclose[-1] < self.dataclose[-2]:
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.order = self.buy()
        else:
            if len(self) >= (self.bar_executed + 5):
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

########################
# Sample 2 only print stock close price
class PrintClose(bt.Strategy):
    def __init__(self):
        ##??????data[0]????????????????????????
        self.dataclose = self.datas[0].close

    def log(self, txt, dt=None):     
        dt = dt or self.datas[0].datetime.date(0)     
        print('%s, %s' % (dt.isoformat(), txt)) #Print date and close

    def next(self):     
        #???????????????????????????????????????    
        self.log('Close: %.2f' % self.dataclose[0])

########################
# Sample 3 MA
class MAcrossover(bt.Strategy): 
    #??????????????????
    params = (('pfast',20),('pslow',50),)
    def log(self, txt, dt=None):     
        pass
#         dt = dt or self.datas[0].datetime.date(0)     
#         print('%s, %s' % (dt.isoformat(), txt))  # ????????????????????? ??????????????????
    def __init__(self):     
        self.dataclose = self.datas[0].close     
        # Order?????????????????????????????????
        self.order = None     
        # ???????????????????????????     
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                        period=self.params.pslow)     
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
                        period=self.params.pfast)
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():             
                self.log('BUY EXECUTED, %.2f' % order.executed.price)         
            elif order.issell():             
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')     
        #????????????
        self.order = None
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
    def next(self):
#         self.log('Close, %.2f' % self.dataclose[0])
        # ??????????????????????????????
        if self.order:
            return
        #?????????????????????
        if not self.position:
        #???????????????????????????????????????
            #SMA????????????SMA??????
            if self.fast_sma[0] > self.slow_sma[0] and \
            self.fast_sma[-1] < self.slow_sma[-1]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
            #??????SMA????????????SMA??????
            elif self.fast_sma[0] < self.slow_sma[0] and \
            self.fast_sma[-1] > self.slow_sma[-1]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
        else:
            # ???????????????????????????????????????
            if len(self) >= (self.bar_executed + 5):
                self.log('CLOSE CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()

########################
# Sample 4 DonchianChannels
# ????????????Indicator??????
class DonchianChannels(bt.Indicator):
    # ???????????????????????????????????????????????????DCH/DonchianChannel?????????????????????
    alias = ('DCH', 'DonchianChannel',)
    
    # ?????????????????????????????????????????? ??????(????????????????????????2)??????????????????
    lines = ('dcm', 'dch', 'dcl',)  # dc middle, dc high, dc low
    
    # ?????????????????????????????????20??????????????????????????????period???20???lookback???????????????????????????????????????????????????????????????????????????????????????20?????????????????????????????????????????????????????????????????????????????????????????????????????????-1(?????????????????????20???)
    params = dict(
        period=20,
        lookback=-1,  # consider current bar or not
    )
    
    # ????????????Indicators??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????subplot=False
    plotinfo = dict(subplot=False)  # plot along with data
    
    # ???????????????ls???line style???'--'????????????
    plotlines = dict(
        dcm=dict(ls='--'),  # dashed line
        dch=dict(_samecolor=True),  # use same color as prev line (dcm)
        dcl=dict(_samecolor=True),  # use same color as prev line (dch)
    )
    
    def __init__(self):
        # hi???lo??????????????????????????????????????????
        hi, lo = self.data.high, self.data.low
        
        # ????????????????????????????????????????????????????????????????????????lookback????????????????????????????????????????????????????????????
        if self.p.lookback:  # move backwards as needed
            hi, lo = hi(self.p.lookback), lo(self.p.lookback)
        
        # ??????????????????????????????
        self.l.dch = bt.ind.Highest(hi, period=self.p.period)
        self.l.dcl = bt.ind.Lowest(lo, period=self.p.period)
        self.l.dcm = (self.l.dch + self.l.dcl) / 2.0  # avg of the above
        
# ??????????????????
class MyStrategy(bt.Strategy):
    def __init__(self):
        # DCH????????????????????? DonchianChannels???alias
        self.myind = DCH()

    def next(self):
        if self.data[0] > self.myind.dch[0]:
            self.buy()
        elif self.data[0] < self.myind.dcl[0]:
            self.sell()      
########################            
# Sample 5 SmaCross
########################
class AllSizer(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy:
            return math.floor(cash/data.high)
        else:
            return self.broker.getposition(data)
 
 
class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma10 = bt.ind.SMA(period=10)
        sma30 = bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma10, sma30)
        self.signal_add(bt.SIGNAL_LONG, crossover)
 
        self.setsizer(AllSizer())
########################            
# custom
########################
class MAStrategy(bt.Strategy):
    params = (('pfast',20),('pslow',50))
    def log(self,txt,dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s,%s' %(dt.isoformat(),txt))
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.params.pfast)
        self.crossover = bt.indicators.CrossOver(self.slow_sma,self.fast_sma)
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f'%order.executed.price)
            elif order.issell():
                self.log('SELL EXCUTED, %.2F'%order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
    def next(self):
        if self.order:
            return
        if not self.position:
#             if self.fast_sma[0] > self.slow_sma[0] and \
#             self.fast_sma[-1]<self.slow_sma[-1]:
#                 self.log('BUY CREATE, %.2f'%self.dataclose[0])
#                 self.order = self.buy()
#             elif self.fast_sma[0] < self.slow_sma[0] and \
#             self.fast_sma[-1]>self.slow_sma[-1]:
#                 self.log('SELL CREATE, %.2f'%self.dataclose[0])
#                 self.order = self.sell()
            if self.crossover>0:
                self.log('BUY CREATE, %.2f'%self.dataclose[0])
                self.order = self.buy()
            elif self.crossover<0:
                self.log('SELL CREATE, %.2f'%self.dataclose[0])
                self.order = self.sell()
        else:
            if len(self)>=(self.bar_executed+5):
                self.log('Close CTEATE: %.2f'%self.dataclose[0])
                self.order=self.close()
class MAStrategy_opt(bt.Strategy):
    params = (('pfast',20),('pslow',50))
    def log(self,txt,dt=None):
        pass
#         dt = dt or self.datas[0].datetime.date(0)
#         print('%s,%s' %(dt.isoformat(),txt))
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0],
                                                          period=self.params.pfast)
        self.crossover = bt.indicators.CrossOver(self.slow_sma,self.fast_sma)
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f'%order.executed.price)
            elif order.issell():
                self.log('SELL EXCUTED, %.2F'%order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
    def next(self):
        if self.order:
            return
        if not self.position:
            if self.crossover>0:
                self.log('BUY CREATE, %.2f'%self.dataclose[0])
                self.order = self.buy()
            elif self.crossover<0:
                self.log('SELL CREATE, %.2f'%self.dataclose[0])
                self.order = self.sell()
        else:
            if len(self)>=(self.bar_executed+5):
                self.log('Close CTEATE: %.2f'%self.dataclose[0])
                self.order=self.close()
