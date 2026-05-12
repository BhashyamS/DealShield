import streamlit as st
from scraper import find_legal_links


st.set_page_config(
    page_title="FinePrint AI",
    page_icon="🕵️",
    layout="wide"
)

st.title("🕵️ FinePrint AI")
st.subheader("Know the catch before you click agree.")

st.write(
    "Paste a company website below. FinePrint AI will search for terms, privacy, refund, cancellation, and subscription pages."
)

url = st.text_input(
    "Enter company website URL",
    placeholder="https://example.com"
)

if st.button("Scan Website"):
    if not url:
        st.warning("Please enter a website URL.")
    else:
        with st.spinner("Scanning website for legal and policy pages..."):
            result = find_legal_links(url)

        if result["error"]:
            st.error(result["error"])
        else:
            links = result["links"]

            if not links:
                st.warning("No legal or policy pages found on the homepage.")
            else:
                st.success(f"Found {len(links)} possible policy pages.")

                for link in links:
                    st.markdown("---")
                    st.write(f"**Category:** {link['category'].title()}")
                    st.write(f"**Page Text:** {link['text']}")
                    st.write(f"**URL:** {link['url']}")
