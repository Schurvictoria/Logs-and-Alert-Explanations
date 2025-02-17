from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
import streamlit as st


@st.cache_resource(show_spinner=False)
def load_embedder(model_name: str, device: str) -> SentenceTransformer:
    return SentenceTransformer(model_name, device=device)


def encode(model: SentenceTransformer, texts: List[str], batch_size: int) -> np.ndarray:
    if not texts:
        return np.empty((0, 0))
    return model.encode(texts, batch_size=batch_size, show_progress_bar=False, convert_to_numpy=True)

