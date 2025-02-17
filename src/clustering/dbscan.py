from typing import Dict, List, Tuple
import numpy as np
from sklearn.cluster import DBSCAN


def cluster_cosine(embeddings: np.ndarray, eps: float, min_samples: int) -> np.ndarray:
    if embeddings.size == 0:
        return np.array([])
    return DBSCAN(eps=eps, min_samples=min_samples, metric="cosine").fit_predict(embeddings)


def split_clusters(labels: np.ndarray) -> Tuple[Dict[int, List[int]], List[int]]:
    clusters: Dict[int, List[int]] = {}
    for i, lbl in enumerate(labels):
        clusters.setdefault(int(lbl), []).append(i)
    anomalies = clusters.pop(-1, []) if -1 in clusters else []
    return clusters, anomalies

