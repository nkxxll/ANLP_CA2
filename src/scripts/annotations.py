import json
import sys

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