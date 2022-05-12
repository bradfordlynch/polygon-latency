import argparse
from functools import partial
import json
import os
from typing import Union
import time

from polygon import WebSocketClient
import requests


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test",
        type=str,
        default="wss",
        help="API to test: wss or rest",
    )
    parser.add_argument(
        "--print_interval",
        type=int,
        default=1000,
        help="Interval for computing and displaying stats",
    )
    parser.add_argument(
        "--symbol",
        type=str,
        default="QQQ",
        help="symbol to use in latency test",
    )
    args = parser.parse_args()

    return args


def handle_msg(msgs: Union[str, bytes], print_interval: int):
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
            print(f"mu_nbbo_ts = {mu:.1f} ms +/- {std:.2f}")
            n_until_print = print_interval
            obs = []
    except:
        # Status message
        print(most_recent)


def run_rest_test(symbol: str, print_interval: int):
    global n_until_print
    global obs

    uri = f"https://api.polygon.io/v2/last/nbbo/{symbol}"
    params = {"apiKey": os.environ.get("POLYGON_API_KEY")}

    while True:
        ts_req = time.time_ns()
        resp = requests.get(uri, params=params)
        ts_resp = time.time_ns()
        dt_call = (ts_resp - ts_req) / 1e6
        nbbo = resp.json()["results"]
        dt_nbbo_ts = (ts_resp - nbbo["t"]) / 1e6

        obs.append((dt_call, dt_nbbo_ts))
        n_until_print -= 1

        if n_until_print == 0:
            mu_call = sum([ob[0] for ob in obs]) / len(obs)
            std_call = (sum([(ob[0] - mu_call) ** 2 for ob in obs]) / len(obs)) ** 0.5
            mu_nbbo_ts = sum([ob[1] for ob in obs]) / len(obs)
            std_nbbo_ts = (
                sum([(ob[1] - mu_nbbo_ts) ** 2 for ob in obs]) / len(obs)
            ) ** 0.5
            print(
                f"mu_call = {mu_call:.1f} ms +/- {std_call:.2f}, mu_nbbo_ts = {mu_nbbo_ts:.1f} ms +/- {std_nbbo_ts:.2f}"
            )
            n_until_print = print_interval
            obs = []


if __name__ == "__main__":
    args = _parse_args()

    n_until_print = args.print_interval
    obs = []

    if args.test == "wss":
        c = WebSocketClient(subscriptions=[f"Q.{args.symbol}"], raw=True)
        processor = partial(handle_msg, print_interval=args.print_interval)
        c.run(processor)
    elif args.test == "rest":
        run_rest_test(args.symbol, args.print_interval)
    else:
        raise NotImplementedError(f"Unsupported test {args.test}")
