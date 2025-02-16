from urllib.request import urlretrieve
from tqdm import tqdm

# This script will download the project data required to run the notebooks and scripts from the HSMA clousi.
# RUN FROM PROJECT ROOT DIR!

downloads = [
    ("https://clousi.hs-mannheim.de/index.php/s/5aTQFo4xd9A9aay/download", "data/reviews_100k_cleaned_new.csv.bz2"),
]

if __name__ == "__main__":
    print("Now downloading project data ...")
    for (url, path) in tqdm(downloads):
        urlretrieve(url, path)
    print("done!")