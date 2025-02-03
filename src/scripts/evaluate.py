from argparse import ArgumentParser
from datetime import datetime
from sys import stderr

from multilabel_classification_evaluator import MultiLabelEvaluator
from ollama_topic_classification import Model

JSON_PATH = "../../data/lstudio_annotations.json"
JSON_MIN_PATH = "../../data/lstudio_min_annotations.json"

def setup_args():
    ap = ArgumentParser()
    ap.add_argument("-f", "--file", type=str, help="File to evaluate")

    return ap.parse_args()

def get_model(file):
    for model in Model:
        if model.value in file:
            if model == Model.LLAMA3B:
                if Model.LLAMA1B.value in file:
                    return Model.LLAMA1B.value
            return model.value
    return "nomodel"

def main():
    args = setup_args()
    evaluator = MultiLabelEvaluator(JSON_PATH , args.file)
    df = evaluator.evaluate()
    json = df.to_json()
    model = get_model(args.file)
    json_file = f"eval_{model}_{datetime.now().isoformat().replace(":", "_")}.json"
    if not json:
        print(df)
        print("JSON parsing failed", file=stderr)
        exit(1)
    with open(json_file, "w") as f:
        f.write(json)


if __name__ == "__main__":
    main()
