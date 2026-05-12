import streamlit as st

from resolver import resolve_company_input
from scanner import scan_for_policy_pages


TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]


st.set_page_config(
    page_title="FinePrint AI",
    page_icon="🕵️",
    layout="wide"
)

st.title("🕵️ FinePrint AI")
st.subheader("Know the catch before you click agree.")

st.write(
    "Enter a company name or website. FinePrint AI will find policy pages even when the company blocks scraping."
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
            resolved = resolve_company_input(user_input, TAVILY_API_KEY)

        if resolved["error"]:
            st.error(resolved["error"])

        elif resolved["type"] == "url":
            st.session_state["selected_url"] = resolved["url"]
            st.session_state["selected_company"] = user_input
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
        st.session_state["selected_company"] = selected_option["title"]
        st.success(f"Selected: {selected_option['url']}")


if "selected_url" in st.session_state:
    st.markdown("---")
    st.write("### Website Selected")
    st.write(st.session_state["selected_url"])

    if st.button("Scan Website"):
        with st.spinner("Scanning homepage first. If blocked, using Tavily fallback search..."):
            result = scan_for_policy_pages(
                company_name=st.session_state.get("selected_company", user_input),
                website_url=st.session_state["selected_url"],
                tavily_api_key=TAVILY_API_KEY
            )

        if result["cleaned_url"]:
            st.info(f"Cleaned URL used for scan: {result['cleaned_url']}")

        if result["homepage_error"]:
            st.warning(
                "Homepage scraping was blocked or failed, so FinePrint AI used fallback search instead."
            )
            st.caption(result["homepage_error"])

        links = result["links"]

        if not links:
            st.warning("No legal or policy pages found yet.")
        else:
            st.success(f"Found {len(links)} possible policy pages.")

            for link in links:
                st.markdown("---")
                st.write(f"**Category:** {link['category'].title()}")
                st.write(f"**Title:** {link['title']}")
                st.write(f"**Source:** {link['source']}")
                st.write(f"**URL:** {link['url']}")
                if link.get("snippet"):
                    st.write(f"**Snippet:** {link['snippet']}")
