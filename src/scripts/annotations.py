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
    df: pd.DataFrame, labels: dict, mode: str = "dummy"
) -> pd.DataFrame:
    """updates dataset dataframe by left joining the one hot encoded annotation label columns (uncovered will be NaN)"""

    if mode == "dummy":
        dummy_cols = get_one_hot_labels_df_(labels)
        dummy_cols.reset_index(names="review_id", inplace=True)
        # print(dummy_cols)

        # join review df with encoded labels
        return pd.merge(df, dummy_cols, on="review_id", how="left")
    elif mode == "strlist":
        NotImplementedError("TODO")
    else:
        raise ValueError(f"Unknown mode '{mode}'")


def get_one_hot_labels_df_(labels: dict) -> pd.DataFrame:
    """builds dataframe from dict containing labels (values) per id (key) by one hot encoding them into columns"""

    # get unique labels
    all_labels = set(
        [l for label in labels.values() for l in label]
    )  # flatten list of all unique labels
    print(f"mapping {len(all_labels)} unique labels: {', '.join(all_labels)}")

    # for each label, create a hot one encoded column
    dummy_cols = pd.DataFrame(
        {
            label: [1 if label in labels[key] else 0 for key in labels]
            for label in all_labels
        },
        index=labels.keys(),
    )
    return dummy_cols

