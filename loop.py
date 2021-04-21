from strategy import Strategy
from event import SignalEvent

try:
    import Queue as queue
except ImportError:
    import queue

from portfolio import Portfolio
from data import LiveKrakenDataHandler
from mac import MovingAverageCrossStrategy
from portfolio import Portfolio
from execution import KrakenExecutionHandler
import time


bars = LiveKrakenDataHandler()
strategy = MovingAverageCrossStrategy()
port = Portfolio()
broker = KrakenExecutionHandler
events = queue.Queue()

while True:
    #if new bar gives market event
    bars.update_bars()

    
    # Handle the events
    while True:
        try:
            event = events.get(False)
        except queue.Empty:
            break
        else:
            if event is not None:
                if event.type == 'MARKET':
                    strategy.calculate_signals(event)
                    port.update_timeindex(event)

                elif event.type == 'SIGNAL':
                    port.update_signal(event)

                elif event.type == 'ORDER':
                    broker.execute_order(event)

                elif event.type == 'FILL':
                    port.update_fill(event)

    # 10-Minute heartbeat
    time.sleep(10*60)