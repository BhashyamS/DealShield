import streamlit as st

from resolver import resolve_company_input
from scanner import scan_for_policy_pages
from extractor import extract_policy_bundle
from analyzer import analyze_consumer_risk


TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]


st.set_page_config(
    page_title="FinePrint AI",
    page_icon="🕵️",
    layout="wide"
)

st.title("🕵️ FinePrint AI")
st.subheader("Know the catch before you click agree.")

st.write(
    "Enter a company name or website. FinePrint AI finds policy pages, extracts important terms, and creates a consumer risk report."
)

user_input = st.text_input(
    "Enter company name or website",
    placeholder="Example: DoorDash, Planet Fitness, Netflix, hellofresh.com"
)

if st.button("Find Company"):
    if not user_input:
        st.warning("Please enter a company name or website.")
    else:
        with st.spinner("Finding the official company website..."):
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

        st.session_state["scan_result"] = result

    if "scan_result" in st.session_state:
        result = st.session_state["scan_result"]

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

            with st.expander("View discovered policy pages"):
                for link in links:
                    st.markdown("---")
                    st.write(f"**Category:** {link['category'].title()}")
                    st.write(f"**Title:** {link['title']}")
                    st.write(f"**Source:** {link['source']}")
                    st.write(f"**URL:** {link['url']}")
                    if link.get("snippet"):
                        st.write(f"**Snippet:** {link['snippet']}")

            if st.button("Generate Consumer Risk Report"):
                with st.spinner("Extracting policy text and analyzing consumer risk with Gemini..."):
                    policy_bundle = extract_policy_bundle(links)
                    risk_report = analyze_consumer_risk(
                        company_name=st.session_state.get("selected_company", user_input),
                        website_url=st.session_state["selected_url"],
                        policy_bundle=policy_bundle,
                        gemini_api_key=GEMINI_API_KEY
                    )

                st.session_state["policy_bundle"] = policy_bundle
                st.session_state["risk_report"] = risk_report

    if "risk_report" in st.session_state:
        report = st.session_state["risk_report"]

        st.markdown("---")
        st.write("## 🛡️ FinePrint AI Risk Report")

        if report.get("error"):
            st.error(report["error"])
            if report.get("raw_text"):
                with st.expander("Raw AI output"):
                    st.write(report["raw_text"])
        else:
            score = report.get("risk_score", 0)
            label = report.get("risk_level", "Unknown")

            st.metric("Consumer Risk Score", f"{score}/100", label)

            st.write("### Quick Summary")
            st.write(report.get("summary", "No summary available."))

            membership_options = report.get("membership_options", [])
            if membership_options:
                st.write("### Membership / Subscription Options")
                st.dataframe(membership_options, use_container_width=True)
            else:
                st.write("### Membership / Subscription Options")
                st.info("No clear membership or subscription options were found in the available policy text.")

            all_fees = report.get("all_fees", [])
            if all_fees:
                st.write("### Fee Table")
                st.dataframe(all_fees, use_container_width=True)
            else:
                st.write("### Fee Table")
                st.info("No specific fee amounts were found in the available policy text.")

            st.write("### Key Red Flags")
            red_flags = report.get("red_flags", [])
            if red_flags:
                for flag in red_flags:
                    st.warning(flag)
            else:
                st.success("No major red flags detected from the available policy text.")

            st.write("### Hidden Cost / Subscription Findings")
            findings = report.get("billing_findings", [])
            if findings:
                for item in findings:
                    st.write(f"- {item}")
            else:
                st.write("No specific billing findings detected.")

            st.write("### Cancellation / Refund Findings")
            cancellation = report.get("cancellation_refund_findings", [])
            if cancellation:
                for item in cancellation:
                    st.write(f"- {item}")
            else:
                st.write("No specific cancellation or refund findings detected.")

            st.write("### Recommended Action")
            st.info(report.get("recommended_action", "Review the policy pages carefully before signing up."))

            limitations = report.get("evidence_limitations", "")
            if limitations:
                with st.expander("Evidence limitations"):
                    st.write(limitations)

            st.caption("Not legal advice. This report summarizes available public policy text and search snippets.")
