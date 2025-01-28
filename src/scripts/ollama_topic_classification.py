#!/usr/bin/env python3

import csv
import json
import string
from enum import StrEnum
from logging import INFO, Logger, basicConfig, getLogger
from types import FunctionType
from typing import Literal

from annotations import lstudio_label_mapping_to_dict, update_df_review_labels
from ollama import ChatResponse, Client, Message, Options, RequestError
from pandas import read_csv
from termcolor import colored

SYSTEM_FILE = "./assets/system_multilabel.txt"
PROMPT_TEMPLATE = "./assets/multilabel.txt"
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
        for id, review in zip(self._ids, self._reviews):
            self._logger.info(f"{colored("Review:", color="green")}\n{review}")
            answer = self.get_topic(review)
            topics = eval_answer(answer)
            topics_list = [t.value for t in (topics if topics is not None else [])]
            res[id] = topics_list
        return res

    def get_topic_eval(self, review: str):
        answer = self.get_topic(review)
        return self.evaluate_answer(answer)

    def get_topic(self, review: str) -> str | Literal["RequestError", "None"]:
        prompt = self._build_prompt(review)
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
        topics: list[Topic] = []
        for t in self._topics:
            if t.value in answer:
                topics.append(t)

        return topics if topics != [] else None

    def _build_prompt(self, review: str) -> str:
        return self._prompt_template.replace("$Review$", review).replace(
            "$Topics$", ",".join([t.value for t in self._topics])
        )

    def _make_default_options(self):
        return Options(temperature=0.3)

    def _make_default_client(self, options: Options):
        client = Client()

        msg: Message = Message(role="system", content=self._system_prompt)
        client.chat(self._model, messages=[msg], options=options)

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
    print(reviews_labeled.dropna())
    ann_reviews = reviews_labeled.dropna()

    if n != -1:
        reviews = list(ann_reviews["review"])[:n]
        ids = list(ann_reviews["review_id"])[:n]
    else:
        reviews = list(ann_reviews["review"])
        ids = list(ann_reviews["review_id"])

    return ids, reviews


def main():
    basicConfig(level=INFO, filename="./ollama_log.txt")
    with open(SYSTEM_FILE, "r") as f:
        sys_prompt = f.read()
    with open(PROMPT_TEMPLATE, "r") as f:
        prompt_template = f.read()
    # id_reviews = read_review_panda(f"{DATA_DIR}{RAW_DATA_FILE}", n=10)
    # reviews = list(id_reviews["review"])
    # ids = list(id_reviews["recommendationid"])

    ids, reviews = ids_reviews_from_json()
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
    o = OllamaClassifier(
        Model.LLAMA3B, sys_prompt, prompt_template, reviews, ids, topics
    )
    data = o.get_all_topic_eval()
    with open("results.json", "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    main()
