# event.py
class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    pass

class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """
    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = 'MARKET'
        
    
class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """
    def __init__(self, strategy_id, symbol, datetime, signal_type, strength):
        """
        Initialises the SignalEvent.
        Parameters:
        strategy_id - The unique identifier for the strategy that
        generated the signal.
        symbol - The ticker symbol, e.g. ’GOOG’.
        datetime - The timestamp at which the signal was generated.
        signal_type - ’LONG’ or ’SHORT’.
        strength - An adjustment factor "suggestion" used to scale
        quantity at the portfolio level. Useful for pairs strategies.
        """
        self.type = 'SIGNAL'
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = strength

class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """
    def __init__(self, symbol, order_type, quantity, direction):
        """
        Initialises the order type, setting whether it is
        a Market order (’MKT’) or Limit order (’LMT’), has
        a quantity (integral) and its direction (’BUY’ or
        ’SELL’).
        Parameters:
        symbol - The instrument to trade.
        order_type - ’MKT’ or ’LMT’ for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - ’BUY’ or ’SELL’ for long or short.
        """
        self.type ='ORDER'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = self._check_set_quantity_positive(quantity)
        self.direction = direction
    def _check_set_quantity_positive(self, quantity):
        """
        Checks that quantity is a positive integer.
        """
        if not isinstance(quantity, int) or quantity  <= 0:
            raise ValueError("Order event quantity is not a positive integer")
        return quantity
    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print("Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
        (self.symbol, self.order_type, self.quantity, self.direction))        
            
class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, timeindex, symbol, exchange, quantity, 
                 direction, fill_cost, commission=None):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional 
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        timeindex - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        exchange - The exchange where the order was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        fill_cost - The holdings value in dollars.
        commission - An optional commission sent from IB.
        """
        
        self.type = 'FILL'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        # Calculate commission
        if exchange == 'kraken':
            self.commission = self.calculate_kraken_commission()
        else:
            self.commission = commission

    def calculate_kraken_commission(self):
        """
        Gives kraken fixes 0.26% taker fee

        
        
      NEED EDITING
      
      
        """
        
        full_cost = 0.026 * self.quantity
        
        return full_cost            