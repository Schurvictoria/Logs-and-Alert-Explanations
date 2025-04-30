import os
from typing import List

import numpy as np
import pandas as pd
import streamlit as st

from src.io.parse import parse_lines, read_upload
from src.embeddings.bge import load_embedder, encode
from src.clustering.dbscan import cluster_cosine, split_clusters
from src.explainers.openai_explainer import explain as explain_openai
from src.email.service import send_email, build_anomaly_html


st.set_page_config(page_title="BGE + DBSCAN Log Anomalies", layout="wide")
st.title("BGE-M3 + DBSCAN: Log Anomaly Explorer")

with st.sidebar:
    st.subheader("Embedding & DBSCAN")
    model_name = st.text_input("Embedding model", value="BAAI/bge-m3")
    device = st.selectbox("Device", ["cpu", "cuda"], index=0)
    eps = st.number_input("DBSCAN eps (cosine)", min_value=0.01, max_value=1.0, value=0.30, step=0.01)
    min_samples = st.number_input("min_samples", min_value=1, max_value=50, value=3, step=1)
    batch_size = st.number_input("Batch size", min_value=1, max_value=64, value=8, step=1)

    st.subheader("OpenAI")
    openai_api_key = st.text_input("API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    model_openai = st.text_input("Model", value="gpt-4o-mini")

    st.subheader("Email")
    smtp_host = st.text_input("SMTP host", value=os.getenv("EMAIL_HOST", "smtp.gmail.com"))
    smtp_port = st.number_input("SMTP port", min_value=1, max_value=65535, value=int(os.getenv("EMAIL_PORT", "587")))
    smtp_user = st.text_input("SMTP user", value=os.getenv("EMAIL_USER", ""))
    smtp_pass = st.text_input("SMTP password", value=os.getenv("EMAIL_PASSWORD", ""), type="password")
    from_addr = st.text_input("From", value=os.getenv("EMAIL_FROM", "log-anomaly@example.com"))
    to_addrs_text = st.text_area("To (comma separated)", value=os.getenv("EMAIL_TO", ""), height=60)
    include_ai = st.checkbox("Include AI explanation in email", value=True)


def _parse_recipients(text: str) -> List[str]:
    return [t.strip() for t in (text or "").split(",") if t.strip()]


col_left, col_right = st.columns(2)
with col_left:
    uploaded = st.file_uploader("Upload logs (.txt or .jsonl)", type=["txt", "log", "jsonl"])
    raw_text = st.text_area(
        "Paste logs (one line per entry or JSONL)",
        height=240,
        placeholder="2025-08-01T12:00:00Z ERROR database timeout\n{\"timestamp\":\"...\",\"level\":\"ERROR\",\"message\":\"DB pool exhausted\"}",
    )

with col_right:
    st.write("Example lines:")
    st.code(
        """
2025-08-01T12:00:01Z ERROR database timeout on users table
{"level":"ERROR","message":"DB pool exhausted","service":"api"}
2025-08-01T12:00:03Z INFO request ok /health
        """.strip(),
        language="text",
    )


if st.button("Detect anomalies", type="primary", use_container_width=True):
    text_input = read_upload(uploaded) if uploaded else raw_text
    logs = parse_lines(text_input)
    if not logs:
        st.warning("No logs provided.")
        st.stop()

    with st.spinner("Loading embedder..."):
        model = load_embedder(model_name, device)

    with st.spinner("Embedding logs..."):
        X = encode(model, logs, batch_size=batch_size)

    with st.spinner("Clustering with DBSCAN (cosine)..."):
        labels = cluster_cosine(X, eps=eps, min_samples=min_samples)

    clusters, anomalies_idx = split_clusters(labels)

    st.success(f"Clusters: {len(clusters)} | Anomalies: {len(anomalies_idx)}")

    if anomalies_idx:
        anom_msgs = [logs[i] for i in anomalies_idx]
        st.subheader("Anomalies (-1)")
        st.dataframe(pd.DataFrame({"message": anom_msgs}).head(50), use_container_width=True)

        if st.toggle("Explain anomalies with OpenAI"):
            with st.spinner("Asking OpenAI..."):
                explanation = explain_openai(openai_api_key, model_openai, anom_msgs)
            st.markdown(explanation)

        to_list = _parse_recipients(to_addrs_text)
        if to_list and st.button("Send anomalies by email", use_container_width=True):
            html = build_anomaly_html("Detected anomalies", anom_msgs)
            if include_ai:
                ai_text = explain_openai(openai_api_key, model_openai, anom_msgs)
                html += f"<hr><pre style='white-space:pre-wrap'>{ai_text}</pre>"
            ok = send_email(
                host=smtp_host,
                port=int(smtp_port),
                user=smtp_user,
                password=smtp_pass,
                from_addr=from_addr,
                to_addrs=to_list,
                subject="Log Anomalies",
                html=html,
            )
            if ok:
                st.success("Email sent")
            else:
                st.error("Email failed")

    st.subheader("Clusters")
    for lbl, idxs in sorted(clusters.items(), key=lambda x: -len(x[1])):
        with st.expander(f"Cluster {lbl} • {len(idxs)} logs"):
            sample = [logs[i] for i in idxs[:10]]
            st.write("Sample:")
            for s in sample:
                st.text("• " + s)

    st.download_button(
        "Download labels as CSV",
        data=pd.DataFrame({"text": logs, "label": labels}).to_csv(index=False).encode("utf-8"),
        file_name="labels.csv",
        mime="text/csv",
        use_container_width=True,
    )


st.caption("Run: streamlit run app.py")

