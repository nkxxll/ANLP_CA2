import pandas as pd
from torch.utils.data import Dataset

class SteamReviewDataset(Dataset):
    """Minimal PyTorch Dataloader for our dataset, see also https://pytorch.org/tutorials/beginner/basics/data_tutorial.html

    Args:
        fi_path (str): Path to csv
        target (str):  Desired label column of the df
        shuffle (bool): Randomize review sequence order

    Returns:
        _type_: _description_
    """
    reviews_df: pd.DataFrame
    target: str
    
    def __init__(self, fi_path: str = None, target:str = "voted_up", shuffle: bool = False):
        self.reviews_df = pd.read_csv(fi_path, low_memory=False)
        self.reviews_df["review"] = self.reviews_df["review"].astype(str)
        
        if shuffle:
            self.reviews_df = self.reviews_df.sample(frac=1).reset_index(drop=True)
            
        self.target = target
        
        print(f"Loaded {len(self):,} reviews")

    def __len__(self):
        return len(self.reviews_df)

    def __getitem__(self, idx: int):
        review = self.reviews_df["review"].iloc[idx]
        target = self.reviews_df[self.target].iloc[idx]
        return review, target
    
    def __getitems__(self, idxs: list):
        idx = self.reviews_df.index.isin(idxs)
        reviews = self.reviews_df["review"][idx]
        targets = self.reviews_df[self.target][idx]
        return reviews.to_list(), targets.to_list()