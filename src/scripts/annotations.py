import json
import sys

import numpy as np
import pandas as pd


def lstudio_label_mapping_to_dict(json_path: str) -> dict[int, list[str]]:
    """Helper function to load annotaed labels from label studio JSON-MIN export file to dict"""

    with open(json_path, "r") as fi:
        items = json.load(fi)

    print(f"loaded {len(items)} annotated reviews from '{json_path}'")

    mappings: dict = {}

    for i in items:
        # If no label selected, "tag" key will be missing
        try:
            # if multiple labels, it will be another nested dict, else str
            if "choices" in i["tag"]:
                mappings[i["review_id"]] = i["tag"]["choices"]
            else:
                mappings[i["review_id"]] = [i["tag"]]
        except KeyError as e:
            print(f"No tags found for review id {i['review_id']}", file=sys.stderr)

    return mappings


def update_df_review_labels(
    df: pd.DataFrame, labels: dict, mode: str = "dummy", dropna: bool = False
) -> tuple[pd.DataFrame, list[str]]:
    """updates dataset dataframe by left joining the one hot encoded annotation label columns (uncovered will be NaN)"""

    if mode == "dummy":
        dummy_cols, all_labels = get_one_hot_labels_df_(labels)
        dummy_cols.reset_index(names="review_id", inplace=True)

        # join review df with encoded labels
        dummified_df = pd.merge(df, dummy_cols, on="review_id", how="left")
        if dropna:
            dummified_df.dropna(
                inplace=True,
                ignore_index=True,
                how="all",
                subset=all_labels,
            )
        return dummified_df, list(all_labels)

    elif mode == "strlist":
        NotImplementedError("TODO")
    else:
        raise ValueError(f"Unknown mode '{mode}'")


def get_one_hot_labels_df_(labels: dict) -> tuple[pd.DataFrame, set[str]]:
    """builds dataframe from dict containing labels (values) per id (key) by one hot encoding them into columns"""
    # see https://discuss.pytorch.org/t/multi-label-classification-in-pytorch/905/44

    # get unique labels
    all_labels = set(
        [l for label in labels.values() for l in label]
    )  # flatten list of all unique labels

    # for each label, create a hot one encoded column
    dummy_cols = pd.DataFrame(
        {
            label: [1 if label in labels[key] else 0 for key in labels]
            for label in all_labels
        },
        index=labels.keys(),
    )

    return dummy_cols, all_labels
