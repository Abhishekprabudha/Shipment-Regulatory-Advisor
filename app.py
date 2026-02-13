import streamlit as st
import hashlib

from utils.pdf_loader import pdf_to_text_from_bytes
from utils.retrieval import chunk_text, build_inverted_index, top_k
from utils.ear746_advisor import advisory_from_ear746
from utils.plotting import plot_risk_gauge, plot_risk_breakdown


# ---------------- Page Config ----------------
st.set_page_config(page_title="Regulated Shipping Advisor (EAR 746)", layout="wide")
st.title("🧭 Regulated Shipping Advisor — EAR Part 746 (Demo)")
st.caption("Upload EAR Part 746 (PDF) → SHIP/HOLD/DO_NOT_SHIP + evidence + Q&A + risk graphs. Demo only (not legal advice).")

# ---------------- Demo Product Catalog ----------------
PRODUCT_CATALOG = [
    {"name": "Lithium-ion Batteries (UN3480)", "unit_value": 35.0},
    {"name": "Lithium batteries in equipment (UN3481)", "unit_value": 45.0},
    {"name": "Encrypted Wi-Fi Router", "unit_value": 120.0},
    {"name": "Drone Flight Controller Module", "unit_value": 900.0},
    {"name": "Industrial Chemical Reagent (Dual-use)", "unit_value": 250.0},
    {"name": "Medical Device Consumables", "unit_value": 80.0},
    {"name": "Satellite Communication Component", "unit_value": 1500.0},
    {"name": "High-power RF Amplifier", "unit_value": 2200.0},
]

# ---------------- Upload Regulatory Base ----------------
uploaded_pdf = st.file_uploader("📄 Upload EAR Part 746 (PDF)", type=["pdf"])
if not uploaded_pdf:
    st.info("Upload the EAR Part 746 PDF to continue.")
    st.stop()

# Read bytes once
pdf_bytes = uploaded_pdf.getvalue()
pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

# ---------------- Session Cache ----------------
if "ear_cache" not in st.session_state:
    st.session_state.ear_cache = {}

cache = st.session_state.ear_cache

# Only rebuild if the uploaded PDF changed
if cache.get("hash") != pdf_hash:
    with st.spinner("Parsing PDF (cached after first parse)…"):
        # Cap pages for Streamlit Cloud stability; tune 25–60 based on PDF size.
        ear_text = pdf_to_text_from_bytes(pdf_bytes, max_pages=45)

    with st.spinner("Building retrieval index (capped for memory)…"):
        chunks = chunk_text(ear_text, chunk_size=900, overlap=150)

        # Cap chunk count to avoid memory spikes
        MAX_CHUNKS = 900
        if len(chunks) > MAX_CHUNKS:
            chunks = chunks[:MAX_CHUNKS]

        index = build_inverted_index(chunks, max_unique_tokens_per_chunk=250)

    cache["hash"] = pdf_hash
    cache["text"] = ear_text
    cache["chunks"] = chunks
    cache["index"] = index

ear_text = cache["text"]
ear_chunks = cache["chunks"]
ear_index = cache["index"]

# ---------------- UI Layout ----------------
left, right = st.columns([1, 1])

with left:
    st.subheader("📦 Shipment Details")

    destination = st.selectbox(
        "Destination Country",
        [
            "United Arab Emirates",
            "India",
            "Germany",
            "Singapore",
            "Cuba",
            "Iran",
            "Syria",
            "Russia",
            "Belarus",
            "North Korea",
            "Crimea",
            "Donetsk",
            "Luhansk",
        ],
    )

    product = st.selectbox("Product", [p["name"] for p in PRODUCT_CATALOG])
    default_uv = next(p["unit_value"] for p in PRODUCT_CATALOG if p["name"] == product)

    qty = st.number_input("Quantity", min_value=0.0, value=10.0, step=1.0)
    unit_value = st.number_input("Unit Value (USD)", min_value=0.0, value=float(default_uv), step=5.0)

    run = st.button("🔎 Generate Advisory", type="primary")


with right:
    st.subheader("🧾 Compliance Advisory (EAR 746-only)")

    if run:
        adv = advisory_from_ear746(
            destination=destination,
            product=product,
            quantity=qty,
            unit_value=unit_value,
            ear746_text=ear_text,
        )

        # Decision banner
        if adv.decision == "SHIP":
            st.success(f"Decision: {adv.decision} ✅")
        elif adv.decision == "HOLD":
            st.warning(f"Decision: {adv.decision} ⏸️")
        else:
            st.error(f"Decision: {adv.decision} ⛔")

        st.metric("Risk Score", adv.risk_score)

        # ---- Graphs ----
        st.markdown("### 📈 Risk Visualization")
        g1, g2 = st.columns([1, 1])

        with g1:
            fig_gauge = plot_risk_gauge(adv.risk_score, max_score=100)
            st.pyplot(fig_gauge, clear_figure=True)

        with g2:
            fig_break = plot_risk_breakdown(adv.components)
            st.pyplot(fig_break, clear_figure=True)

        # Interpretation
        st.markdown("### Risk Interpretation")
        if adv.risk_score >= 80:
            st.write("**High risk**: treat as no-go until compliance clearance and authorizations are documented.")
        elif adv.risk_score >= 45:
            st.write("**Medium risk**: place on hold; perform compliance checks (classification, end-use/end-user).")
        else:
            st.write("**Low risk**: proceed with standard screening and documentation.")

        # Reasons
        st.markdown("### Reasons")
        for r in adv.reasons:
            st.write("•", r)

        # Evidence snippets (fast retrieval)
        st.markdown("### Evidence snippets (from uploaded PDF)")
        hits = top_k(f"{destination} Part 746", ear_chunks, ear_index, k=3)
        if hits:
            for score, snippet in hits:
                st.write(f"**Match score:** {score}")
                st.write(snippet[:550] + "…")
                st.write("---")
        else:
            st.info("No strong snippet match found for this query.")
    else:
        st.info("Fill shipment details and click **Generate Advisory**.")


# ---------------- Q&A ----------------
st.divider()
st.subheader("💬 Ask Questions (EAR 746 only)")

q = st.text_input("Ask", "What does Part 746 say about Cuba?")
if st.button("Search Regulation"):
    hits = top_k(q, ear_chunks, ear_index, k=4)
    if not hits:
        st.warning("No strong match found. Try keywords like '746.1', 'embargo', 'Cuba', 'Iran', 'Syria', 'Russia'.")
    else:
        for score, snippet in hits:
            st.write(f"**Match score:** {score}")
            st.write(snippet[:800] + "…")
            st.write("---")
