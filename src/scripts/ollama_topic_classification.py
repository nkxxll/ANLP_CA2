#!/usr/bin/env python3

import csv
import json
import string
from argparse import ArgumentParser
from datetime import datetime
from enum import StrEnum
from logging import INFO, Logger, basicConfig, getLogger
from types import FunctionType
from typing import Literal

from tqdm import tqdm

from annotations import lstudio_label_mapping_to_dict, update_df_review_labels
from ollama import ChatResponse, Client, Message, Options, RequestError
from pandas import read_csv
from termcolor import colored

PROMPTDIR = "./assets/"
DATA_DIR = "../../data/"
RAW_DATA_FILE = "reviews_100k_raw.csv.bz2"
JSON_PATH = "../../data/lstudio_annotations.json"
JSON_MIN_PATH = "../../data/lstudio_min_annotations.json"
CLEANED_DATA_FILE = "reviews_fetch_100k_cleaned_v2.csv.bz2"


class Model(StrEnum):
    LLAMA3B = "llama3.2"
    LLAMA1B = "llama3.2:1b"
    MISTRAL = "mistral"
    SMALLTHINKER = "smallthinker"
    DEEPSEEK7B = "deepseek-r1:7b"
    DEEPSEEK1_5B = "deepseek-r1:1.5b"


class Topic:
    """Topic is a wrapper class for a string that should be a valid topic"""

    def __init__(self, topic: "str | Topic") -> None:
        if isinstance(topic, Topic):
            self._topic = topic.value
        elif string.whitespace in topic:
            raise ValueError("Topics must not contain whitespace")
        else:
            self._topic = topic

    def __str__(self) -> str:
        return self._topic

    def __repr__(self) -> str:
        return self._topic

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self._topic == other._topic
        else:
            raise TypeError("Other is not of type Topic")

    def __hash__(self):
        return hash(str(self))

    @property
    def value(self) -> str:
        return self._topic

    @value.setter
    def value(self, value: str) -> None:
        self._eval_topic(value)
        self._topic = value

    @staticmethod
    def _eval_topic(topic: str) -> None:
        """evals the topic

        A topic is a none whitespace character containing string that describes a topic of a review.

        Args:
            topic: string that holds the topic

        Raises:
            ValueError: if topic does not fulfil the requirements for a topic
            this function raises a value error
        """
        if string.whitespace in topic:
            raise ValueError("Topics must not contain whitespace")


class OllamaClassifier:
    """OllamaClassifier classifies reviews with the help of ollama to a specific list of topics"""

    def __init__(
        self,
        model: Model,
        system_prompt: str,
        prompt_template: str,
        reviews: list[str],
        ids: list[int],
        topics: list[Topic],
        logger: Logger = getLogger(__name__),
        client: Client | None = None,
        options: Options | None = None,
    ) -> None:
        self._reviews = reviews
        self._topics = topics
        self._ids = ids
        self._model = model
        self._prompt_template = prompt_template
        self._system_prompt = system_prompt
        self._logger = logger
        self._options: Options = (
            self._make_default_options() if options is None else options
        )
        # options have to be defined before the client because client uses options
        self._client = (
            self._make_default_client(self._options) if client is None else client
        )

    def get_all_topic_eval(
        self, eval_answer_function: FunctionType | None = None
    ) -> dict[int, list[str]]:
        if eval_answer_function is None:
            eval_answer = self.evaluate_answer
        else:
            eval_answer = eval_answer_function

        res = {}
        
        print(f"loading {self._model} ..")
        for id, review in tqdm(zip(self._ids, self._reviews), total=len(self._ids)):
            self._logger.info(f"{colored('Review:', color='green')}\n{review}")
            answer = self.get_topic(review)
            self._logger.info(f"{colored('Answer:', color='green')}\n{answer}")
            topics = eval_answer(answer)
            self._logger.info(f"{colored('Topics:', color='green')}\n{topics}")
            if topics is None:
                self._logger.warning(f"{colored('No topics found', color='red')}")
            topics_list = [t.value for t in (topics if topics is not None else [])]
            res[id] = topics_list
        return res


    def get_topic_eval(self, review: str):
        answer = self.get_topic(review)
        return self.evaluate_answer(answer)

    def get_topic(self, review: str) -> str | Literal["RequestError", "None"]:
        prompt = self._build_prompt(review)
        self._logger.info(f"{colored("Full prompt:", color="green")}:\n{prompt}")
        msg: Message = Message(role="user", content=prompt)
        try:
            answer: ChatResponse = self._client.chat(
                model=self._model, messages=[msg], options=self._options
            )
        except RequestError:
            return "RequestError"

        return answer.message.content if answer.message.content is not None else "None"

    def evaluate_answer(self, answer: str) -> list[Topic] | None:
        """Evaluates the answer of the model

        Args:
            answer: this is the answer of the model as string

        Returns:
            Topic if the answer is valid else None
        """
        topics: set[Topic] = set()
        lower = answer.lower()

        # hopefully dodge the reasoning
        if "predicted_topics:" in lower:
            lower = lower.split("predicted_topics:")[1]
            self._logger.info(f"{colored("lower after split:", color="green")}: {lower}")

        generated_topics = self.generate_topic_options(self._topics)
        for k, v in generated_topics.items():
            if k in lower:
                topics.add(v)

        return list(topics) if bool(topics) else None

    @staticmethod
    def generate_topic_options(topics: list[Topic]) -> dict[str, Topic]:
        res = {}
        for topic in topics:
            if "_" in topic.value:
                res[topic.value.replace("_", " ")] = topic
                res[topic.value] = topic
            else:
                res[topic.value] = topic

        return res

    def _build_prompt(self, review: str) -> str:
        return self._prompt_template.replace("$Review$", review).replace(
            "$Topics$", ",".join([t.value for t in self._topics])
        )

    def _make_default_options(self):
        return Options(temperature=0.3)

    def _make_default_client(self, options: Options):
        client = Client()

        msg: Message = Message(role="system", content=self._system_prompt)
        client.chat(str(self._model), messages=[msg], options=options)

        return client


def read_review_csv(file: str, rrow: str = "review"):
    reviews = []
    with open(file, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)  # Use DictReader to access columns by name
        for row in reader:
            if rrow in row:  # Check if the 'review' column exists
                reviews.append(row[rrow])
    return reviews


def read_review_panda(
    file: str, columns: list[str] = ["recommendationid", "review"], n: int = 100
):
    csv = read_csv(file, compression="bz2", low_memory=False)

    print(csv.columns)
    sample = csv.sample(n=n)
    print(sample.index)

    reviews = sample[columns]

    return reviews


def ids_reviews_from_json(n: int = -1):
    ids: list[int] = []
    reviews: list[str] = []

    ann_mappings = lstudio_label_mapping_to_dict(JSON_MIN_PATH)

    # load the original dataset
    reviews_df = read_csv("../../data/reviews_100k.csv.bz2", low_memory=False)
    reviews_df["review"] = reviews_df["review"].astype(str)

    # update the dataset with the new annotations (all rows not covered will have NaN)
    reviews_labeled = update_df_review_labels(reviews_df, ann_mappings, mode="dummy")

    # drop all reviews which are not yet annotated
    ann_reviews = reviews_labeled.dropna()

    if n != -1:
        reviews = list(ann_reviews["review"])[:n]
        ids = list(ann_reviews["review_id"])[:n]
    else:
        reviews = list(ann_reviews["review"])
        ids = list(ann_reviews["review_id"])

    return ids, reviews


def setup_args():
    """Set up arguments for ollama script

    Returns:
        arguments Namespace
    """
    ap = ArgumentParser()
    ap.add_argument(
        "-v",
        "--prompt-version",
        type=int,
        default=1,
        help="Version of prompt and system prompt",
    )
    ap.add_argument(
        "-n",
        "--number",
        type=int,
        default=-1,
        help="number of reviews to annotate [default] -1 => all",
    )
    ap.add_argument(
        "-m",
        "--model",
        type=Model,
        choices=list(Model),
        default=Model.LLAMA3B,
        help="Model to use [default] LLAMA3B",
    )
    return ap.parse_args()


def main():
    args = setup_args()
    versions = {
        1: {
            "promptfile": f"{PROMPTDIR}prompt_v1.txt",
            "systemfile": f"{PROMPTDIR}system_v1.txt",
        },
        2: {
            "promptfile": f"{PROMPTDIR}prompt_v2.txt",
            "systemfile": f"{PROMPTDIR}system_v2.txt",
        },
        3: {
            "promptfile": f"{PROMPTDIR}prompt_v3.txt",
            "systemfile": f"{PROMPTDIR}system_v3.txt",
        },
    }
    basicConfig(level=INFO, filename="./ollama_log.txt", filemode="w")
    with open(versions[args.prompt_version]["systemfile"], "r", encoding='utf-8') as f:
        sys_prompt = f.read()
    with open(versions[args.prompt_version]["promptfile"], "r", encoding='utf-8') as f:
        prompt_template = f.read()

    ids, reviews = ids_reviews_from_json(n=args.number)
    print(f"info: {len(reviews)}")
    topics = [
        Topic(t)
        for t in [
            "gamemode",
            "bugs",
            "visuals",
            "sound",
            "hardware_requirements",
            "price",
            "gameplay",
            "story",
            "support",
            "online_play",
            "updates",
            "seasonal_content",
        ]
    ]
    o = OllamaClassifier(args.model, sys_prompt, prompt_template, reviews, ids, topics)
    data = o.get_all_topic_eval()
    json_file_name = f"./results/results-v{args.prompt_version}-{datetime.now().isoformat()}-n{args.number if args.number > 0 else "all"}-{str(args.model)}.json".replace(
        ":", "_"
    )
    print(json_file_name)
    with open(
        json_file_name,
        "w",
    ) as f:
        json.dump(data, f)


if __name__ == "__main__":
    main()
