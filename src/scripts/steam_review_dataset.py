import pandas as pd
import sentencepiece as spm
import torch
from torch.utils.data import Dataset


class SteamReviewDataset(Dataset):
    def __init__(
        self,
        data: pd.DataFrame,
        tokenizer: spm.SentencePieceProcessor,
        max_len: int = 200,
        padding: bool = True,
        topic_mode: bool = False,
        topics: list[str] = None,
    ):
        """
        Args:
            data: DataFrame mit den Reviews und Labels.
            tokenizer: SentencePiece-Tokenizer.
            max_len: Maximale Länge der Sequenzen (Padding/Truncation).
            padding: Padding ja/nein.
        """
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.padding_char = self.tokenizer.pad_id()
        self.padding = padding
        self.topic_mode = topic_mode
        self.topics = topics

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx: int):
        """
        Holt ein einzelnes Datenbeispiel.
        Args:
            idx: Index des Beispiels.
        Returns:
            tokens: Tokenisierte Review.
            label: Label des Beispiels
        """
        row = self.data.iloc[idx]
        review = row["review"]

        if self.topic_mode and self.topics is not None:
            label = self.data[self.topics].iloc[idx].values
        else:
            label = row["voted_up"]

        tokens = self.tokenizer.encode(review, out_type=int)

        # Padding und Truncation
        if self.padding:
            if len(tokens) > self.max_len:
                tokens = tokens[: self.max_len]
            else:
                tokens = tokens + [self.padding_char] * (self.max_len - len(tokens))
        # print(f"tokens = {tokens}, label(s) = {label}")
        return torch.tensor(tokens), torch.tensor(label, dtype=torch.float32)
