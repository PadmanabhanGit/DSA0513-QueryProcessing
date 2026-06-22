import os
import joblib
import numpy as np
from config import MODEL_PATH


class Predictor:
    def __init__(self, model_path: str = MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self._load()

    def _load(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
            except Exception:
                self.model = None
        else:
            self.model = None

    def predict(self, stats: dict) -> float:
        """Predict execution time (ms) given query stats.
        Falls back to a simple heuristic if model is unavailable.
        """
        features = [
            stats.get("query_length", 0),
            stats.get("joins", 0),
            stats.get("conditions", 0),
            stats.get("group_by_count", 0),
            stats.get("order_by_count", 0),
        ]
        X = np.array(features).reshape(1, -1)
        if self.model is not None:
            try:
                pred = float(self.model.predict(X)[0])
                return max(pred, 0.0)
            except Exception:
                pass

        # heuristic fallback
        return float(5 + features[0] * 0.5 + features[1] * 50 + features[2] * 20 + features[3] * 40 + features[4] * 30)


if __name__ == "__main__":
    from models.analyzer import QueryAnalyzer
    p = Predictor()
    s = QueryAnalyzer.analyze("SELECT * FROM employees WHERE salary>70000")
    print(p.predict(s))
