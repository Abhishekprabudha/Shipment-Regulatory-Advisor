import json
import streamlit as st
from bs4 import BeautifulSoup

from utils.downloader import download_if_needed
from utils.advisor import build_advisory
from utils.retrieval import chunk_text, retrieve_top_snippets

# ---------------- Page config ----------------
st.set_page_config(page_title="Regulated Shipping Advisor", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 1rem; }
.small { font-size: 0.9rem; opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🧭 Regulated Shipping Advisor (Demo)</h1>", unsafe_allow_html=True)
st.markdown("<div class='small' style='text-align:center;'>Not legal advice. Demo for regulated-destination + commodity risk screening.</div>", unsafe_allow_html=True)

# ---------------- Load demo data ----------------
with open("data/sample_shipments.json", "r", encoding="utf-8") as f:
    shipments = json.load(f)

with open("data/policy_config.json", "r", encoding="utf-8") as f:
    policy = json.load(f)

# ---------------- Download regulatory sources ----------------
with st.spinner("Refreshing US regulatory sources (cached)…"):
    reg_paths = download_if_needed(cache_dir="data/regdocs", max_age_hours=24)

# Build retrieval corpus (HTML -> text -> chunks)
def html_to_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text(" ", strip=True)

bis_text = html_to_text(reg_paths["bis_part_746_html"])
ofac_text = html_to_text(reg_paths["ofac_country_info_html"])

corpus_chunks = []
for ch in chunk_text(bis_text):
    corpus_chunks.append(("BIS eCFR 15 CFR Part 746", ch))
for ch in chunk_text(ofac_text):
    corpus_chunks.append(("OFAC Sanctions Programs & Country Info", ch))

# ---------------- UI layout ----------------
left, right = st.columns([1, 1])

# ===== LEFT: Shipment selection form =====
with left:
    st.subheader("📦 Shipment Setup")

    ship_ids = [s["shipment_id"] for s in shipments]
    ship_id = st.selectbox("1) Choose a shipment", ship_ids)

    shipment = next(s for s in shipments if s["shipment_id"] == ship_id)

    st.write("**Item:**", shipment["item_name"])
    st.write("**HS Code:**", shipment["hs_code"])
    st.write("**Category:**", shipment["category"])
    st.write("**Description:**", shipment["description"])

    destination = st.selectbox(
        "2) Destination country",
        ["United Arab Emirates", "Singapore", "Germany", "India", "Cuba", "Iran", "North Korea", "Syria", "Russia"]
    )

    qty = st.number_input(f"3) Quantity ({shipment['unit']})", min_value=0.0, value=float(shipment["default_qty"]), step=1.0)
    unit_value = st.number_input("4) Unit value (USD)", min_value=0.0, value=float(shipment["unit_value_usd"]), step=5.0)

    run = st.button("🔎 Generate Advisory", type="primary")

# ===== RIGHT: Advisory + Q&A =====
with right:
    st.subheader("🧾 Advisory Output")

    container = st.container(height=420)

    with container:
        if run:
            result = build_advisory(
                shipment=shipment,
                destination=destination,
                qty=qty,
                unit_value=unit_value,
                policy=policy
            )

            if result.decision == "SHIP":
                st.success(f"Decision: {result.decision} ✅")
            elif result.decision == "HOLD":
                st.warning(f"Decision: {result.decision} ⏸️")
            else:
                st.error(f"Decision: {result.decision} ⛔")

            st.metric("Risk score", result.risk_score)

            st.markdown("**Why this was flagged**")
            for r in result.reasons:
                st.write("•", r)

            st.markdown("**Recommended next steps**")
            for n in result.next_steps:
                st.write("•", n)

            st.divider()
            st.caption("Regulatory sources cached from BIS eCFR Part 746 and OFAC program list (refreshed every 24h).")

        else:
            st.info("Select shipment + destination, then click **Generate Advisory**.")

    st.subheader("💬 Ask the Advisor (retrieval-based)")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.write(msg)

    q = st.chat_input("Ask: 'Is Cuba restricted?'  'What does Part 746 cover?'  'OFAC country list?'")
    if q:
        st.session_state.chat.append(("user", q))
        with st.chat_message("user"):
            st.write(q)

        hits = retrieve_top_snippets(q, corpus_chunks, k=4)

        answer_lines = []
        if not hits:
            answer_lines.append("I couldn’t find a strong match in the cached regulatory text. Try using different keywords (e.g., 'Cuba', 'Iran', 'Part 746', 'license').")
        else:
            answer_lines.append("Top relevant regulatory snippets (for demo):\n")
            for src, snippet, score in hits:
                answer_lines.append(f"**Source:** {src}  (match score: {score})")
                answer_lines.append(f"— {snippet[:420]}…\n")

        final = "\n".join(answer_lines)

        st.session_state.chat.append(("assistant", final))
        with st.chat_message("assistant"):
            st.write(final)
