# BGE + DBSCAN Log Anomaly Explorer

Minimalist tool for log anomaly detection:
- Semantic embeddings: BGE-M3 (Hugging Face)
- Clustering: DBSCAN (cosine distance)
- Explanations (optional): OpenAI
- UI: Streamlit
- Email notifications: SMTP

## Quick Start (Local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`.

## Usage
- Left sidebar: choose embedding model, DBSCAN parameters, (optional) OpenAI key and SMTP settings
- Upload .txt/.log/.jsonl file or paste text
- Click "Detect anomalies"
- Anomalies (-1) block: unusual log lines, get brief explanation (OpenAI)
- "Send anomalies by email" button sends anomaly list to specified addresses

## Environment Variables (Optional)
- `OPENAI_API_KEY`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_FROM`

Copy `.env.example` to `.env` and fill your values.

## Docker

Build and run:
```bash
docker build -t bge-dbscan-app .
docker run --rm -p 8501:8501 --env-file .env bge-dbscan-app
```

Or with inline env vars:
```bash
docker run --rm -p 8501:8501 \
  -e OPENAI_API_KEY=sk-... \
  -e EMAIL_HOST=smtp.gmail.com -e EMAIL_PORT=587 \
  -e EMAIL_USER=you@gmail.com -e EMAIL_PASSWORD=app-pass \
  -e EMAIL_FROM="Log Anomaly <you@gmail.com>" \
  bge-dbscan-app
```

Open `http://localhost:8501`.

## Structure
```
.
├── app.py                    # Streamlit UI
├── requirements.txt
├── .env.example              # Environment template
└── src
    ├── embeddings/bge.py     # BGE loading and encoding
    ├── clustering/dbscan.py  # DBSCAN and grouping
    ├── io/parse.py           # file reading + parsing
    ├── explainers/openai_explainer.py
    └── email/service.py      # SMTP + HTML email
```

## Parameter Tips
- Embeddings are sensitive to `eps` (for cosine): start with `0.3`. If too noisy — increase to `0.4-0.5`. If too few anomalies — decrease to `0.15-0.25`.
- `min_samples` 3–5 usually works well.