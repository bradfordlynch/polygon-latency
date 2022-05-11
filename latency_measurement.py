import json
from typing import Union
import time

from polygon import WebSocketClient

PRINT_INTERVAL = 10

c = WebSocketClient(subscriptions=["Q.QQQ"], raw=True)
n_until_print = PRINT_INTERVAL
obs = []


def handle_msg(msgs: Union[str, bytes]):
    global n_until_print
    global obs

    ts_now = time.time()
    msgs_parsed = json.loads(msgs)
    most_recent = msgs_parsed[-1]
    try:
        latency_ms = ts_now * 1000 - most_recent["t"]
        obs.append(latency_ms)
        n_until_print -= 1

        if n_until_print == 0:
            mu = sum(obs) / len(obs)
            std = (sum([(ob - mu) ** 2 for ob in obs]) / len(obs)) ** 0.5
            print(f"mu_latency = {mu:.1f} ms +/- {std:.2f}")
            n_until_print = PRINT_INTERVAL
            obs = []
    except:
        # Status message
        print(most_recent)


c.run(handle_msg)
