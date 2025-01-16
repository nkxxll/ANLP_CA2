#!/usr/bin/env python3
"""help with hand classification and topic finding

This is a little scripts that helps with classifying topics by hand and/or
generating topics by reading some topics by hand.

Installation:
pip/conda install pandas termcolor
"""

import signal
from argparse import ArgumentParser
from datetime import datetime
from logging import getLogger
from textwrap import wrap

from pandas import DataFrame, Series, read_csv
from termcolor import colored

logger = getLogger(__name__)

TOPICS = []
NUMBERS = "1234567890"
N = 10


def eval_topics(topics):
    res = []
    for topic in topics:
        if topic in NUMBERS:
            res.append(TOPICS[topic])
            continue
        if topic not in TOPICS:
            logger.error(f"this topic was not in the topics: {topic}")
            return False, []
        res.append(topic)
    return True, res


def classification_main(samplesize: int):
    file = "reviews_100k_raw.csv.bz2"
    csv: DataFrame = read_csv(file, compression="bz2", low_memory=False)

    sample: DataFrame = csv.sample(n=samplesize)
    res = []

    def handle_interrupt():
        """Try to gracefully handle control-c and save the current data"""

        # if the identification generation is canceled save the data any ways
        def signal_handler(signal, frame):
            sample.join(Series(res, name="topics"))
            sample.to_csv(
                f"{str(datetime.now()).replace(" ", "_")}-canceled.csv",
                encoding="utf8",
            )
            logger.warning("interrupted")
            exit(1)

        signal.signal(signal.SIGINT, signal_handler)

    handle_interrupt()

    for _, s in sample.iterrows():
        print("\n".join(wrap(str(s["review"]))))
        topics_input = input(
            f"\n{colored("Write down some topics (one of '{TOPICS}' or the numbers): ", color="green")}"
        )
        print()
        topics = [t.strip() for t in topics_input.split(",")]
        res.append(topics)

    sample.join(Series(res, name="topics"))
    sample.to_csv(
        f"{str(datetime.now()).replace(" ", "_")}-finished.csv",
        encoding="utf8",
    )


def identification_main(samplesize: int):
    # read csv
    file = "reviews_100k_raw.csv.bz2"
    csv: DataFrame = read_csv(file, compression="bz2", low_memory=False)

    sample: DataFrame = csv.sample(n=samplesize)
    res = []

    def handle_interrupt():
        """Try to gracefully handle control-c and save the current data"""

        # if the identification generation is canceled save the data any ways
        def signal_handler(signal, frame):
            sample.join(Series(res, name="topics"))
            sample.to_csv(
                f"{str(datetime.now()).replace(" ", "_")}-canceled.csv",
                encoding="utf8",
            )
            logger.warning("interrupted")
            exit(1)

        signal.signal(signal.SIGINT, signal_handler)

    handle_interrupt()

    for _, s in sample.iterrows():
        print("\n".join(wrap(str(s["review"]))))
        topics_input = input(
            f"\n{colored("write down some topics ('t1,t2,t3'): ", color="green")}"
        )
        print()
        topics = [t.strip() for t in topics_input.split(",")]
        res.append(topics)

    sample.join(Series(res, name="topics"))
    sample.to_csv(
        f"{str(datetime.now()).replace(" ", "_")}-finished.csv",
        encoding="utf8",
    )


def main():
    ap = ArgumentParser()
    ap.add_argument("-g", "--generate", action="store_true", default=False)
    ap.add_argument("-c", "--classify", action="store_true", default=False)
    ap.add_argument("-s", "--samplesize", type=int, default=N)

    args = ap.parse_args()

    if not args.classify and not args.generate:
        logger.warning("You have to either choose classify or generate")
        ap.print_help()
        exit(1)

    if args.classify and args.generate:
        logger.warning("You have to either choose classify or generate")
        ap.print_help()
        exit(1)

    if args.classify:
        classification_main(args.samplesize)
    else:
        identification_main(args.samplesize)


if __name__ == "__main__":
    main()
