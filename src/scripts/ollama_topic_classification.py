#!/usr/bin/env python3

import csv
import string
from enum import StrEnum
from logging import Logger, getLogger
from types import FunctionType
from typing import Literal

from termcolor import colored

from ollama import ChatResponse, Client, Message, Options, RequestError

SYSTEM_FILE = "./prompts/system_prompt_classifying1.txt"
PROMPT_TEMPLATE = "./prompts/classification_prompt1.txt"


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
        topics: list[Topic],
        logger: Logger = getLogger(__name__),
        client: Client | None = None,
        options: Options | None = None,
    ) -> None:
        self._reviews = reviews
        self._topics = topics
        self._model = model
        self._prompt_template = prompt_template
        self._system_prompt = system_prompt
        self._logger = logger
        self._options = self._make_default_options() if Options is None else options
        # options have to be defined before the client because client uses options
        self._client = (
            self._make_default_client(self._options) if client is None else client
        )

    def get_all_topic_eval(
        self, eval_answer_function: FunctionType | None = None
    ) -> list[Topic | None]:
        if eval_answer_function is None:
            eval_answer = self.evaluate_answer
        else:
            eval_answer = eval_answer_function

        res = []
        for review in self._reviews:
            answer = self.get_topic(review)
            res.append(eval_answer(answer))
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

    def evaluate_answer(self, answer: str) -> Topic | None:
        """Evaluates the answer of the model

        Args:
            answer: this is the answer of the model as string

        Returns:
            Topic if the answer is valid else None
        """
        topic: Topic | None = None
        for t in self._topics:
            if t.value in answer:
                if topic is not None and topic != t:
                    self._logger.warning(
                        f"{colored("There was a second topic found in answer:", "red")}\n{answer}"
                    )
                    continue
                topic = t

        return topic

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


def read_review_panda(file: str, rrow: str = "review", n: int = 100):
    from pandas import read_csv

    csv = read_csv(file, compression="bz2", low_memory=False)

    reviews_series = csv[rrow]
    reviews = list(reviews_series[:n])

    return reviews


def main():
    with open(SYSTEM_FILE, "r") as f:
        sys_prompt = f.read()
    with open(PROMPT_TEMPLATE, "r") as f:
        prompt_template = f.read()
    reviews = read_review_panda("./static/reviews_100k_raw.csv.bz2", "review", 20)
    print(f"info: {len(reviews)}")
    topics = [
        Topic(t)
        for t in [
            "Gameplay",
            "Graphics",
            "Story",
            "Multiplayer",
            "Bugs",
            "Performance",
        ]
    ]
    o = OllamaClassifier(Model.LLAMA3B, sys_prompt, prompt_template, reviews, topics)
    print(o.get_all_topic_eval())


if __name__ == "__main__":
    main()
