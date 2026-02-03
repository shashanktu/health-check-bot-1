import streamlit as st
import time
import re
import requests
import pandas as pd
import streamlit.components.v1 as components
from PIL import Image

st.set_page_config(page_title="Smoke Test Bot")

# Add a container for logo and title with centered alignment
st.markdown(
    '''<div style="width: 100vw; min-height: 40vh; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 40px;">
        <img src="src/logo.png" alt="ValueMomentum Logo" style="width:180px; margin-bottom: 20px;" />
        <h1 style="margin: 0; font-size: 3em; color: #34495e; width: 100%; text-align: center;"> App Diagnosis Bot </h1>
        <div style="font-size: 1.2em; color: #567; margin-top: 10px; width: 100%; text-align: center;">Automated Smoke Testing & Validation Platform</div>
    </div>''', unsafe_allow_html=True)
# st.write("Welcome to the Smoke Test Bot!")

def extract_environment_and_app(user_input):
    text = user_input.lower()
    env_patterns = {
        'dev': ['dev', 'development'],
        'uat': ['uat', 'qa', 'test'],
        'prod': ['prod', 'production']
    }
    environment = None
    application = None
    for env_key, env_values in env_patterns.items():
        for env_val in env_values:
            if env_val in text:
                environment = env_key
                break
        if environment:
            break
    app_match = re.search(r'on\s+(\w+)\s+application', text)
    if app_match:
        application = app_match.group(1)
    else:
        app_match = re.search(r'(?:for|in)\s+(\w+)', text)
        if app_match:
            application = app_match.group(1)
    return environment, application

user_input = st.chat_input("Hi! How Can I Help you...")

if user_input:
    if user_input.lower() in ["hi", "hello", "hey"]:
        st.chat_message("assistant").write("Hello! How can I assist you with smoke tests today?")
    elif "smoke test" in user_input.lower() or "test" in user_input.lower():
        environment, application = extract_environment_and_app(user_input)
        if environment and application:
            st.chat_message("assistant").write(f"Running Dependency validation for {application.title()} application on {environment.upper()} environment...")
            # --- Gemini test generation UI (commented out for now) ---
            # st.subheader("Generate Playwright Test with Gemini")
            # requirements = st.text_area("Enter requirements or failure log for new test case:")
            # filename = st.text_input("Test file to overwrite (e.g. tests/TagAI/tagaitests.spec.ts):", value="tests/TagAI/tagaitests.spec.ts")
            # if st.button("Generate and Save Test with Gemini"):
            #     gen_resp = requests.post("http://localhost:8000/genai/generate-test", json={"requirements": requirements, "filename": filename})
            #     if gen_resp.ok and gen_resp.json().get("status") == "success":
            #         st.success(f"Test file {filename} generated and saved.")
            #         st.code(gen_resp.json().get("code", ""), language="typescript")
            #     else:
            #         st.error(f"Gemini test generation failed: {gen_resp.text}")
            # --- Existing smoke test workflow ...existing code...
            # phases = ["DB Connection", "API Response", "Metrics", "Secrets Check"]
            phases = ["DB Connection", "API Response", "Metrics"]
            phase_containers = []
            for phase in phases:
                container = st.container()
                with container:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**{phase}**")
                    with col2:
                        status_placeholder = st.empty()
                    progress_placeholder = st.empty()
                phase_containers.append((progress_placeholder, status_placeholder))
            api_endpoints = {
                "DB Connection": "http://localhost:8000/test/db",
                "Dependencies": "http://localhost:8000/test/apis", 
                "Metrics": "http://localhost:8000/test/metrics",
                # "Secrets Check": "http://localhost:8000/test/secrets"
            }
            results = {}
            for phase, (progress_placeholder, status_placeholder) in zip(phases, phase_containers):
                endpoint = api_endpoints[phase]
                with progress_placeholder:
                    progress_bar = st.progress(0)
                    for j in range(101):
                        progress_bar.progress(j / 100)
                        time.sleep(0.01)
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        # st.code(response.json())
                        with status_placeholder:
                            st.write("✅")
                            if phase == "DB Connection":
                                # st.write(f"Message: {data.get('message', 'No message field in response')}")
                                db = data.get("data", {})
                                details = db.get("details", {})
                                # st.write(f"Status: {db.get('status', 'N/A')}")
                                # st.write(f"Latency: {db.get('latency_ms', 'N/A'):.2f} ms")
                                st.write(f"Connection: {details.get('status', 'N/A')}")
                                # st.write(f"Query: {details.get('query_status', 'N/A')}")
                                # st.write(f"Result: {details.get('query_result_summary', 'N/A')}")
                                results[phase] = {
                                    "Status": db.get('status', 'N/A'),
                                    "Latency (ms)": db.get('latency_ms', 'N/A'),
                                    "Details": f"Conn: {details.get('connection_status', 'N/A')}, Query: {details.get('query_status', 'N/A')}"
                                }
                            elif phase == "API Response":
                                api = data.get("data", {})
                                details = api.get("details", {})
                                st.write(f"APIs Tested: {details.get('apis_tested', 'N/A')}: \n APIs Passed: {details.get('apis_passed', 'N/A')}")
                                # st.write(f"Status: {api.get('status', 'N/A')}")
                                # st.write(f"Latency: {api.get('latency_ms', 'N/A'):.2f} ms")
                                # st.write(f"APIs Passed: {details.get('apis_passed', 'N/A')}/{details.get('apis_tested', 'N/A')}")
                                # for r in details.get('api_results', []):
                                #     st.write(f"{r.get('name', 'N/A')}: {r.get('status', 'N/A')} ({r.get('latency_ms', 'N/A'):.2f} ms)")
                                results[phase] = {
                                    "Status": api.get('status', 'N/A'),
                                    "Latency (ms)": api.get('latency_ms', 'N/A'),
                                    "Details": f"Passed: {details.get('apis_passed', 'N/A')}/{details.get('apis_tested', 'N/A')}"
                                }
                            elif phase == "Metrics":
                                metrics = data.get("data", {})
                                st.write(f"Status: {metrics.get('status')}")
                                st.write(f"Latency: {metrics.get('latency_ms', 'N/A'):.2f} ms")
                                results[phase] = {
                                    "Status": metrics.get('status'),
                                    "Latency (ms)": metrics.get('latency_ms', 'N/A'),
                                    "Details": "-"
                                }
                            # elif phase == "Secrets Check":
                            #     # Show error or pending message
                            #     st.write("❌ Permissions not set. Check later.")
                            #     results[phase] = {
                            #         "Status": "ERROR",
                            #         "Latency (ms)": "-",
                            #         "Details": "Permissions not set"
                            #     }
                    else:
                        with status_placeholder:
                            st.write("❌")
                            results[phase] = {
                                "Status": "ERROR",
                                "Latency (ms)": "-",
                                "Details": "API error"
                            }
                except Exception as e:
                    with status_placeholder:
                        st.write("❌")
                        results[phase] = {
                            "Status": "ERROR",
                            "Latency (ms)": "-",
                            "Details": str(e)
                        }
            st.chat_message("assistant").write(f"✅ Validation Completed for {application.title()} on {environment.upper()}!")
            # Show summary table
            # st.subheader("Dependencies Check Summary")
            
            # summary_df = pd.DataFrame.from_dict(results, orient="index")
            # st.table(summary_df)
            # Integration with backend: fetch commit info from backend endpoint
            commit_url = "http://localhost:8000/commits/latest"
            try:
                commit_response = requests.get(commit_url, timeout=5)
                if commit_response.status_code == 200:
                    details = commit_response.json()
                    st.chat_message("assistant").write(
                        f"Below are the latest commit details:\n- Author: {details['author']}\n- Date: {details['date']}\n- Message: {details['message']}\n- Files Changed: {details['files_changed']}"
                    )
                else:
                    st.chat_message("assistant").write("Could not fetch commit details.")
            except Exception as e:
                st.chat_message("assistant").write("Error fetching commit details.")
            # --- Run test impact analysis only on changed file from latest commit ---
            test_impact_filename = "tests/TagAI/tagaitests.spec.ts"  # Default file if Gemini UI is commented out
            st.chat_message("assistant").write(f"Undergoing Test Impact Analysis on changed file: {test_impact_filename} ...")
            import time
            st.info(f"Starting backend Playwright test impact analysis on {test_impact_filename}...")
            start_resp = requests.post("http://localhost:8000/run-test-impact", json={"filename": test_impact_filename})
            if start_resp.ok and start_resp.json().get("status") == "started":
                st.success("Test Impact Analysis started in backend.")
                # Wait 1 minute, then fetch report regardless of process status
                time.sleep(60)
                report_url = "http://localhost:8000/playwright-report/index.html"
                import os
                if os.path.exists(r"playwright-report/index.html"):
                    # if st.button("Check Report Preview"):
                    #     st.session_state.show_report = True
                        st.write("**Test Report**")
                        file_path = "C:\\Users\\backofficeuser\\Pictures\\smoke-bot\\playwright-report\\index.html"
                        with open(file_path, "r", encoding="utf-8") as f:
                            html_content = f.read()
                        components.html(html_content, height=700, scrolling=True)

                    # if st.session_state.get("show_report", False):
                    #     st.chat_message("assistant").write(f"✅ Test Impact Analysis completed. Report embedded below.")
                        
                else:
                    st.error("Playwright tests did not generate a report.")
            else:
                st.error("Failed to start backend test impact analysis.")
        elif environment:
            st.chat_message("assistant").write(f"I found the environment ({environment.upper()}) but couldn't identify the application. Please specify the application name.")
        elif application:
            st.chat_message("assistant").write(f"I found the application ({application.title()}) but couldn't identify the environment. Please specify: Dev, UAT, or Prod.")
        else:
            st.chat_message("assistant").write("Please specify both the environment (Dev/UAT/Prod) and application name for the smoke test.")
    else:
        st.chat_message("assistant").write("I'm sorry, I didn't understand that. Could you please rephrase?")
