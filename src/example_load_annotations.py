import json
import sys

import pandas as pd

sys.path.append("scripts")
from scripts import lstudio_label_mapping_to_dict, update_df_review_labels

# demonstration how loading the annotations from label studio works

if __name__ == "__main__":
    # get dict from labels json
    ann_mappings: dict = lstudio_label_mapping_to_dict("../data/lstudio_annotations.json")

    # load the original dataset
    reviews_df = pd.read_csv("../data/reviews_100k.csv.bz2", low_memory=False)
    reviews_df["review"] = reviews_df["review"].astype(str)
    
    json_annotations_fi = [
    ]
    
    json_annotations = []
    
    
    for ann in json_annotations:
        with open(ann, "r", encoding="utf8") as fi:
            ann_mappings.update(json.load(fi))

    print(ann_mappings)
    # # update the dataset with the new annotations (all rows not covered will have NaN)
    # reviews_labeled = update_df_review_labels(reviews_df, ann_mappings, mode="dummy")

    # print(reviews_labeled)

    # # drop all reviews which are not yet annotated
    # print(reviews_labeled.dropna())

