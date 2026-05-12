import streamlit as st
from scraper import find_legal_links
from resolver import resolve_company_input

TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]

st.set_page_config(
    page_title="FinePrint AI",
    page_icon="🕵️",
    layout="wide"
)

st.title("🕵️ FinePrint AI")
st.subheader("Know the catch before you click agree.")

st.write(
    "Enter a company name or website. FinePrint AI will search for terms, privacy, refund, cancellation, and subscription pages."
)

user_input = st.text_input(
    "Enter company name or website",
    placeholder="Example: DoorDash, Planet Fitness, Netflix, hellofresh.com"
)

if st.button("Find Company"):
    if not user_input:
        st.warning("Please enter a company name or website.")

    else:
        with st.spinner("Finding company website..."):
            resolved = resolve_company_input(
                user_input,
                TAVILY_API_KEY
            )

        if resolved["error"]:
            st.error(resolved["error"])

        elif resolved["type"] == "url":
            st.session_state["selected_url"] = resolved["url"]
            st.success(f"Using website: {resolved['url']}")

        else:
            options = resolved["options"]

            if not options:
                st.warning("No matching company websites found.")
            else:
                st.session_state["company_options"] = options
                st.success("Possible matches found. Choose one below.")


if "company_options" in st.session_state:
    selected_option = st.radio(
        "Select the correct company website:",
        st.session_state["company_options"],
        format_func=lambda option: f"{option['title']} — {option['url']}"
    )

    if st.button("Use This Website"):
        st.session_state["selected_url"] = selected_option["url"]
        st.success(f"Selected: {selected_option['url']}")


if "selected_url" in st.session_state:
    st.markdown("---")
    st.write("### Website Selected")
    st.write(st.session_state["selected_url"])

    if st.button("Scan Website"):
        with st.spinner("Scanning website for legal and policy pages..."):
            result = find_legal_links(st.session_state["selected_url"])

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
