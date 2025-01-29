import json
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, hamming_loss, jaccard_score, precision_score, recall_score, f1_score

class MultiLabelEvaluator:
    def __init__(self, annotations_path: str, results_path: str):
        self.annotations_path = annotations_path
        self.results_path = results_path
        self.true_labels = {}
        self.pred_labels = {}
        self.all_categories = set()
        self.all_review_ids = set()
        self.review_texts = {}
        
        self._load_data()
        self._prepare_data()
    
    def _load_data(self):
        """Lädt die JSON-Daten."""
        with open(self.annotations_path, "r", encoding="utf-8") as f:
            annotations_data = json.load(f)
        with open(self.results_path, "r", encoding="utf-8") as f:
            results_data = json.load(f)
        
        # Ground Truth aus den Annotationen extrahieren
        for entry in annotations_data:
            review_id = entry["data"]["review_id"]
            labels = set()
            if entry["annotations"]:
                for annotation in entry["annotations"]:
                    for result in annotation["result"]:
                        labels.update(result["value"]["choices"])
            self.true_labels[review_id] = labels
            self.review_texts[review_id] = entry["data"].get("review", "")
            
        # Vorhergesagte Labels extrahieren
        self.pred_labels = {int(k): set(v) for k, v in results_data.items()}
    
    def _prepare_data(self):
        """Erstellt die benötigten Datenstrukturen für die Evaluation."""
        self.all_review_ids = sorted(set(self.true_labels.keys()).union(set(self.pred_labels.keys())))
        self.all_categories = sorted(
            {label for labels in self.true_labels.values() for label in labels}.union(
                {label for labels in self.pred_labels.values() for label in labels}
            )
        )
    
    def evaluate(self):
        """Führt die Evaluation durch und gibt ein DataFrame mit den Ergebnissen zurück."""
        true_matrix = []
        pred_matrix = []
        correct_per_review = []
        
        for review_id in self.all_review_ids:
            true_set = self.true_labels.get(review_id, set())
            pred_set = self.pred_labels.get(review_id, set())
            
            true_vector = [1 if category in true_set else 0 for category in self.all_categories]
            pred_vector = [1 if category in pred_set else 0 for category in self.all_categories]
            
            true_matrix.append(true_vector)
            pred_matrix.append(pred_vector)
            
            if true_set:
                correct_count = len(true_set.intersection(pred_set)) / len(true_set)
            else:
                correct_count = 1.0 if not pred_set else 0.0
            
            correct_per_review.append(correct_count)
        
        # DataFrames erstellen
        df_true = pd.DataFrame(true_matrix, columns=self.all_categories, index=self.all_review_ids)
        df_pred = pd.DataFrame(pred_matrix, columns=self.all_categories, index=self.all_review_ids)
        
        # Berechnung der Metriken
        classification_metrics = classification_report(df_true, df_pred, target_names=self.all_categories, zero_division=0, output_dict=True)
        metrics_df = pd.DataFrame(classification_metrics).transpose()
        
        # Weitere Multilabel-Metriken
        overall_accuracy = accuracy_score(df_true.values.flatten(), df_pred.values.flatten())
        hamming = hamming_loss(df_true, df_pred)
        jaccard = jaccard_score(df_true, df_pred, average='samples')
        avg_correct_per_review = sum(correct_per_review) / len(correct_per_review)
        micro_f1 = f1_score(df_true, df_pred, average='micro')
        macro_f1 = f1_score(df_true, df_pred, average='macro')
        micro_precision = precision_score(df_true, df_pred, average='micro')
        macro_precision = precision_score(df_true, df_pred, average='macro')
        micro_recall = recall_score(df_true, df_pred, average='micro')
        macro_recall = recall_score(df_true, df_pred, average='macro')
        
        # Zusätzliche Metriken hinzufügen
        metrics_df.loc["Overall Accuracy"] = [overall_accuracy, "-", "-", "-"]
        metrics_df.loc["Hamming Loss"] = [hamming, "-", "-", "-"]
        metrics_df.loc["Jaccard Score"] = [jaccard, "-", "-", "-"]
        metrics_df.loc["Avg Correct per Review"] = [avg_correct_per_review, "-", "-", "-"]
        metrics_df.loc["Micro F1"] = [micro_f1, "-", "-", "-"]
        metrics_df.loc["Macro F1"] = [macro_f1, "-", "-", "-"]
        metrics_df.loc["Micro Precision"] = [micro_precision, "-", "-", "-"]
        metrics_df.loc["Macro Precision"] = [macro_precision, "-", "-", "-"]
        metrics_df.loc["Micro Recall"] = [micro_recall, "-", "-", "-"]
        metrics_df.loc["Macro Recall"] = [macro_recall, "-", "-", "-"]
        
        return metrics_df
    
    def review_metrics(self):
        """Erstellt einen DataFrame mit allen Reviews, deren Text, den gefundenen Topics und Multilabel-Metriken."""
        review_data = []
        for review_id in self.all_review_ids:
            true_set = self.true_labels.get(review_id, set())
            pred_set = self.pred_labels.get(review_id, set())
            review_text = self.review_texts.get(review_id, "")
            
            correctly_classified = len(true_set.intersection(pred_set))
            total_true = len(true_set)
            correctly_ratio = correctly_classified / total_true if total_true > 0 else 1.0 if not pred_set else 0.0
            
            union = len(true_set.union(pred_set))
            intersection = len(true_set.intersection(pred_set))
            jaccard = intersection / union if union > 0 else 1.0  
            
            review_data.append({
                "Review ID": review_id,
                "Review Text": review_text,
                "True Topics": list(true_set),
                "Predicted Topics": list(pred_set),
                "Correctly Classified Topics": correctly_classified,
                "Total Topics": total_true,
                "Accuracy per Review": correctly_ratio,
                "Jaccard Score": jaccard
            })
        
        return pd.DataFrame(review_data)
