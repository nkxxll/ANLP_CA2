import json
from argparse import ArgumentParser
from datetime import datetime
from sys import stderr

from multilabel_classification_evaluator import MultiLabelEvaluator
from ollama_topic_classification import Model
from sklearn.metrics import accuracy_score, hamming_loss
from sklearn.preprocessing import MultiLabelBinarizer

JSON_PATH = "../../data/lstudio_annotations.json"
JSON_MIN_PATH = "../../data/lstudio_min_annotations.json"

def setup_args():
    ap = ArgumentParser()
    ap.add_argument("-f", "--file", type=str, help="File to evaluate")
    ap.add_argument("-f2", "--file2", type=str, help="optional file two if you want to compare one eval with another")

    return ap.parse_args()

def get_model(file):
    for model in Model:
        if model.value in file:
            if model == Model.LLAMA3B:
                if Model.LLAMA1B.value in file:
                    return Model.LLAMA1B.value
            return model.value
    return "nomodel"

def model_v_model(file: str, file2: str):
    model1 = get_model(file)
    model2 = get_model(file2)

    with open(file, "r") as f:
        data1 = json.load(f)

    with open(file2, "r") as f:
        data2 = json.load(f)

    # evaluate accuracy_score and hamming_loss for the both the models
    evaluator = MultiLabelBinarizer(classes=[
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
        ])

    bin1 = evaluator.fit_transform([data1[key] for key in data1.keys()])
    bin2 = evaluator.transform([data2[key] for key in data2.keys()])

    acc1 = accuracy_score(bin1, bin2)
    ham1 = hamming_loss(bin1, bin2)

    same_count = 0
    total = 0
    for key in data1.keys():
        if sorted(data1[key]) == sorted(data2[key]):
            same_count += 1
        total += 1

    json_file = f"./eval/eval_{model1}_vs_{model2}_{datetime.now().isoformat().replace(":", "_")}.json"
    # with open(json_file, "w") as f:
    #     f.write(json.dumps({"total": total, "same_count": same_count, "accuracy": acc1, "hamming_loss": ham1}))
    print({"total": total, "same_count": same_count, "accuracy": acc1, "hamming_loss": ham1})


def main():
    args = setup_args()
    if args.file2:
        model_v_model(args.file, args.file2)
    else:
        evaluator = MultiLabelEvaluator(JSON_PATH , args.file)
        df = evaluator.evaluate()
        json = df.to_json()
        model = get_model(args.file)
        json_file = f"./eval/eval_{model}_{datetime.now().isoformat().replace(":", "_")}.json"
        if not json:
            print(df)
            print("JSON parsing failed", file=stderr)
            exit(1)
        with open(json_file, "w") as f:
            f.write(json)


if __name__ == "__main__":
    main()
