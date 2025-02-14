from datetime import datetime
import json, sys
from logging import INFO, basicConfig
import pandas as pd

sys.path.append("scripts")
from ollama_topic_classification import OllamaClassifier, Topic, setup_args

PROMPTDIR = "./assets/"

def _sample_reviews(n: int = 1000) -> tuple[int, pd.DataFrame]:
    # load the original dataset
    reviews_df = pd.read_csv("../../data/reviews_100k_cleaned_new.csv.bz2", low_memory=False)
    reviews_df["review"] = reviews_df["review"].astype(str)
    
    samples = reviews_df.sample(n = n)
    
    return (list(samples["review_id"]), list(samples["review"]))

if __name__ == "__main__":
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

    ids, reviews = _sample_reviews(n=args.number)
    print(f"info: Prepared {len(reviews)} (id, review) pairs")
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
    json_file_name = f"./results/annotations-v{args.prompt_version}-{datetime.now().isoformat()}-n{args.number if args.number > 0 else "all"}-{str(args.model)}.json".replace(
        ":", "_"
    )
    print(json_file_name)
    with open(
        json_file_name,
        "w",
    ) as f:
        json.dump(data, f)