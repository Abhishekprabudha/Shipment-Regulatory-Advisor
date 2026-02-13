import streamlit as st

from utils.pdf_loader import pdf_to_text
from utils.retrieval import chunk_text, top_k
from utils.ear746_advisor import advisory_from_ear746


# ---------------- Page Config ----------------
st.set_page_config(page_title="Regulated Shipping Advisor (EAR 746)", layout="wide")
st.title("🧭 Regulated Shipping Advisor — EAR Part 746 (Demo)")
st.caption("Upload EAR Part 746 (PDF) → get SHIP/HOLD/DO_NOT_SHIP advisory + evidence snippets + Q&A. Demo only (not legal advice).")


# ---------------- Upload Regulatory Base ----------------
uploaded_pdf = st.file_uploader("📄 Upload EAR Part 746 Regulatory Document (PDF)", type=["pdf"])

if not uploaded_pdf:
    st.info("Please upload the EAR Part 746 PDF to continue.")
    st.stop()


# ---------------- Parse PDF ----------------
with st.spinner("Reading and parsing EAR Part 746 PDF..."):
    ear_text = pdf_to_text(uploaded_pdf)
    ear_chunks = chunk_text(ear_text)


# ---------------- UI Layout ----------------
left, right = st.columns([1, 1])


# ===== LEFT: Shipment Inputs =====
with left:
    st.subheader("📦 Shipment Details (Demo Inputs)")

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

    product = st.text_input("Product / Item", "Lithium-ion Batteries")
    quantity = st.number_input("Quantity", min_value=0.0, value=10.0, step=1.0)
    unit_value = st.number_input("Unit value (USD)", min_value=0.0, value=35.0, step=5.0)

    run = st.button("🔎 Generate Advisory", type="primary")


# ===== RIGHT: Advisory Output =====
with right:
    st.subheader("🧾 Compliance Advisory (EAR 746-only)")

    if run:
        advisory = advisory_from_ear746(
            destination=destination,
            product=product,
            quantity=quantity,
            unit_value=unit_value,
            ear746_text=ear_text,
        )

        # Decision banner
        if advisory.decision == "SHIP":
            st.success(f"Decision: {advisory.decision} ✅")
        elif advisory.decision == "HOLD":
            st.warning(f"Decision: {advisory.decision} ⏸️")
        else:
            st.error(f"Decision: {advisory.decision} ⛔")

        st.metric("Risk Score", advisory.risk_score)

        # Reasons
        st.markdown("### Reasons")
        for r in advisory.reasons:
            st.write("•", r)

        # Evidence snippets (keyword retrieval)
        st.markdown("### Supporting regulation snippets (from uploaded PDF)")
        query = f"{destination} {product} Part 746 license"
        hits = top_k(query, ear_chunks, k=3)
        if hits:
            for score, snippet in hits:
                st.write(f"**Match score:** {score}")
                st.write(snippet[:550] + "…")
                st.write("---")
        else:
            st.info("No strong snippet match found for this query. Try different keywords.")
    else:
        st.info("Fill shipment details and click **Generate Advisory**.")


# ---------------- Q&A (Retrieval) ----------------
st.divider()
st.subheader("💬 Ask Questions (EAR 746 only)")

question = st.text_input("Ask a question about Part 746", "What does Part 746 say about Cuba?")

ask = st.button("Search Regulation Text")

if ask:
    hits = top_k(question, ear_chunks, k=4)
    if not hits:
        st.warning("No strong match found. Try terms like '746.1', 'embargo', 'Cuba', 'Iran', 'Syria', 'Russia', 'Belarus'.")
    else:
        for score, snippet in hits:
            st.write(f"**Match score:** {score}")
            st.write(snippet[:800] + "…")
            st.write("---")
