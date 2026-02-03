# # import streamlit as st
# # import time
# # import re
# # import requests
# # import pandas as pd
# # import streamlit.components.v1 as components
# # import json
# # from app.services import azure_insights
# # import subprocess
# # import plotly.express as px
# # st.set_page_config(page_title="Diagnosis Bot")
# # import google.generativeai as genai

# # # Get application name from URL parameters
# # app_from_url = st.query_params.get('app', None)
# # env_from_url = st.query_params.get('env', None)

# # # Initialize conversation history
# # if 'conversation_history' not in st.session_state:
# #     st.session_state['conversation_history'] = []

# # # Display conversation history
# # for msg in st.session_state['conversation_history'][-10:]:
# #     if msg.startswith('User: '):
# #         st.chat_message("user").write(msg[6:])
# #     elif msg.startswith('Assistant: '):
# #         st.chat_message("assistant").write(msg[11:])

# # # Auto-set user input if parameters are provided
# # if app_from_url and env_from_url:
# #     user_input = f"run health check for {app_from_url} application in {env_from_url} environment"
# # else:
# #     user_input = None

# # # Initialize pending input and health check flag
# # if 'pending_input' not in st.session_state:
# #     st.session_state['pending_input'] = None
# # if 'health_check_completed' not in st.session_state:
# #     st.session_state['health_check_completed'] = False

# # st.image("src/ValueMomentum_logo.png", width=150)
# # st.markdown(
# #     '''<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 40px;">
# #         <h1 style="margin: 0; font-size: 3em; color: #34495e;">App Diagnosis Bot</h1>
# #          </div>''', unsafe_allow_html=True)

# # def extract_environment_and_app(user_input):
# #     text = user_input.lower()
# #     env_patterns = {
# #         'dev': ['dev', 'development'],
# #         'uat': ['uat', 'qa', 'test'],
# #         'prod': ['prod', 'production']
# #     }
# #     environment = None
# #     application = None
# #     for env_key, env_values in env_patterns.items():
# #         for env_val in env_values:
# #             if env_val in text:
# #                 environment = env_key
# #                 break
# #         if environment:
# #             break
# #     app_match = re.search(r'on\s+(\w+)\s+application', text)
# #     if app_match:
# #         application = app_match.group(1)
# #     else:
# #         app_match = re.search(r'(?:for|in)\s+(\w+)', text)
# #         if app_match:
# #             application = app_match.group(1)
# #     return environment, application

# # if user_input:
# #     # if user_input.lower() in ["hi", "hello", "hey"]:
# #     #     st.chat_message("assistant").write("Hello! How can I assist you with health checks today?")

# #     elif ("health check" in user_input.lower() or "check health" in user_input.lower()) and not st.session_state['health_check_completed']:
# #         environment, application = extract_environment_and_app(user_input)
# #         # Store in session state for AI context
# #         st.session_state['environment'] = environment
# #         st.session_state['application'] = application
# #         if environment and application:
# #             st.chat_message("assistant").write(f"Running Dependency validation for {application.title()} application on {environment.upper()} environment...")
# #             phases = ["DB Connection", "Dependencies", "Metrics"]
# #             phase_containers = []
# #             for phase in phases:
# #                 container = st.container()
# #                 with container:
# #                     col1, col2 = st.columns([2, 1])
# #                     with col1:
# #                         st.write(f"**{phase}**")
# #                     with col2:
# #                         status_placeholder = st.empty()
# #                     progress_placeholder = st.empty()
# #                 phase_containers.append((progress_placeholder, status_placeholder))
# #             # Load API endpoints from JSON file
# #             with open("api_endpoints.json", "r") as f:
# #                 api_endpoints = json.load(f)
# #             results = {}
# #             for phase, (progress_placeholder, status_placeholder) in zip(phases, phase_containers):
# #                 endpoint = api_endpoints[phase]
# #                 with progress_placeholder:
# #                     progress_bar = st.progress(0)
# #                     for j in range(101):
# #                         progress_bar.progress(j / 100)
# #                         time.sleep(0.01)
# #                 try:
# #                     response = requests.get(endpoint, timeout=5)
# #                     if response.status_code == 200:
# #                         data = response.json()
                        
# #                         with status_placeholder:
# #                             st.write("✅")
# #                             if phase == "DB Connection":
# #                                 db = data.get("data", {})
# #                                 details = db.get("details", {})
# #                                 status = data.get('status', 'N/A')
# #                                 st.write(f"Status: {status}")
# #                                 st.session_state['db_status'] = status
                               
# #                             elif phase == "Dependencies":
# #                                 api = data.get("data", {})
# #                                 details = api.get("details", {})
# #                                 api_info = f"APIs Tested: {details.get('apis_tested', 'N/A')}; APIs Passed: {details.get('apis_passed', 'N/A')}; APIs Failed: {details.get('apis_failed', 'N/A')}"
# #                                 st.write(api_info)
# #                                 st.session_state['api_status'] = api_info
                                
# #                             elif phase == "Metrics":
# #                                 metrics = data.get("data", {})
# #                                 metrics_info = f"Status: {metrics.get('status')}, Latency: {metrics.get('latency_ms', 'N/A'):.2f} ms"
# #                                 st.write(f"Status: {metrics.get('status')}")
# #                                 st.write(f"Latency: {metrics.get('latency_ms', 'N/A'):.2f} ms")
# #                                 st.session_state['metrics_status'] = metrics_info
                                
                           
# #                     else:
# #                         with status_placeholder:
# #                             st.write("❌")
                           
# #                 except Exception as e:
# #                     with status_placeholder:
# #                         st.write("❌")
                        
# #             st.subheader("CPU Usage ")
# #             output_placeholder = st.empty()
# #             status_placeholder = st.empty()
            
# #             try:
# #                 # status_placeholder.info("🔄 Starting PowerShell script...")
# #                 process = subprocess.Popen(
# #                     ["powershell", "-ExecutionPolicy", "Bypass", "-File", "upd_metrics.ps1"],
# #                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True
# #                 )
                
# #                 output_lines = []
# #                 while True:
# #                     line = process.stdout.readline()
# #                     if line:
# #                         output_lines.append(line.strip())
# #                         output_placeholder.code("\n".join(output_lines), language="powershell")
# #                         time.sleep(0.1)  # Small delay for live effect
# #                     elif process.poll() is not None:
# #                         break
                
# #                 # Store PowerShell output for AI context
# #                 st.session_state['powershell_output'] = "\n".join(output_lines[-10:])  # Last 10 lines
                
# #                 process.wait()
                
                        
# #             except FileNotFoundError:
# #                 status_placeholder.error("❌ metrics-2.ps1 not found")
# #             except Exception as e:
# #                status_placeholder.error(f"❌ Error running PowerShell script: {str(e)}")
            
# #             # Loading Azure Insights with progress indicator
# #             with st.spinner('Loading Azure Application Insights data...'):
# #                 st.info("Fetching operation metrics and user analytics...")
# #                 output = azure_insights.get_insights()
            
# #             # Display Operation Summary table
# #             if 'operation_summary' in output:
# #                 st.subheader("Operation Summary")
# #                 operations_df = pd.DataFrame(output['operation_summary'])
# #                 # Store Azure data for AI context
# #                 st.session_state['azure_data'] = str(operations_df.head().to_dict())
                
# #                 business_functions = ['Report Incident', 'Policy Search', 'New Claim', 'Submit Claim', 
# #                                     'Claims Dashboard', 'Payments', 'Policy Verification', 'Insured Details', 
# #                                     'Incident Details', 'Claims Summary']
                
                
# #                 chart_data = operations_df[['Operation Name', 'Successful Requests', 'Failed Requests']].head(10).copy()
# #                 chart_data['Business Function'] = business_functions[:len(chart_data)]
# #                 chart_data = chart_data.melt(id_vars=['Business Function'], 
# #                                            value_vars=['Successful Requests', 'Failed Requests'],
# #                                            var_name='Request Type', value_name='Count')
                
# #                 fig = px.bar(chart_data, x='Business Function', y='Count', color='Request Type',
# #                            title='Successful vs Failed Requests by Page',
# #                            color_discrete_map={'Successful Requests': '#2E8B57', 'Failed Requests': '#DC143C'},
# #                            text='Count')
# #                 fig.update_traces(textposition='inside', textangle=0)
# #                 fig.update_xaxes(tickangle=45)
# #                 st.plotly_chart(fig, use_container_width=True)
            
            
# #             time.sleep(1)
# #             col1, col2, col3 = st.columns([2, 1, 2])
            
# #             st.chat_message("assistant").write(f"✅ Validation Completed for {application.title()} on {environment.upper()}!")
            
# #             # Store health check completion in conversation and set flag
# #             st.session_state['conversation_history'].append(f"User: {user_input}")
# #             st.session_state['conversation_history'].append(f"Assistant: Health check completed for {application} on {environment}")
# #             st.session_state['health_check_completed'] = True
            
# #             with col2:
# #                 if st.button("Root Cause Analysis"):
# #                     components.html('<script>window.open("https://teams.microsoft.com/l/app/f6405520-7907-4464-8f6e-9889e2fb7d8f?source=app-header-share-entrypoint&templateInstanceId=19a6974b-869b-465b-b040-5da5fdab88d6&environment=Default-13085c86-4bcb-460a-a6f0-b373421c6323", "_blank")</script>', height=0)
# #         elif environment:
# #             st.chat_message("assistant").write(f"I found the environment ({environment.upper()}) but couldn't identify the application. Please specify the application name.")
# #         elif application:
# #             st.chat_message("assistant").write(f"I found the application ({application.title()}) but couldn't identify the environment. Please specify: Dev, UAT, or Prod.")
# #         else:
# #             st.chat_message("assistant").write("Please specify both the environment (Dev/UAT/Prod) and application name for the smoke test.")


# #     elif user_input:
# #         # Handle general queries with Gemini
# #         st.chat_message("user").write(user_input)
# #         try:
# #             genai.configure(api_key="AIzaSyBvBnlgt1z0JUG7mW-qCOwT4MMOaUSjrao")
# #             model = genai.GenerativeModel('gemini-pro')
            
# #             context = f"""
# # Health Check Context:
# # - Environment: {st.session_state.get('environment', 'N/A')}
# # - Application: {st.session_state.get('application', 'N/A')}
# # - DB Status: {st.session_state.get('db_status', 'N/A')}
# # - API Status: {st.session_state.get('api_status', 'N/A')}
# # - Metrics Status: {st.session_state.get('metrics_status', 'N/A')}

# # Previous Conversation:
# # {chr(10).join(st.session_state['conversation_history'][-6:])}
# # """
            
# #             with st.spinner('Thinking...'):
# #                 prompt = f"{context}\n\nUser: {user_input}\n\nAssistant:"
# #                 response = model.generate_content(prompt)
# #                 st.chat_message("assistant").write(response.text)
                
# #                 # Store conversation
# #                 st.session_state['conversation_history'].append(f"User: {user_input}")
# #                 st.session_state['conversation_history'].append(f"Assistant: {response.text}")
# #         except Exception as e:
# #             st.error(f"Error: {str(e)}")

# # # Always show chat input at the bottom for follow-up questions
# # user_input_new = st.chat_input("Ask questions about the health check results...")
# # if user_input_new:
# #     # Set the new input and rerun to process it
# #     st.session_state['pending_input'] = user_input_new
# #     st.rerun()

# # # Handle pending input from chat (follow-up questions)
# # if 'pending_input' in st.session_state and st.session_state['pending_input']:
# #     user_input = st.session_state['pending_input']
# #     st.session_state['pending_input'] = None
    
# #     # Always handle as general query with Gemini (no health check)
# #     st.chat_message("user").write(user_input)
# #     try:
# #         genai.configure(api_key="AIzaSyBvBnlgt1z0JUG7mW-qCOwT4MMOaUSjrao")
# #         model = genai.GenerativeModel('gemini-2.5-flash')
        
# #         context = f"""
# # Health Check Context:
# # - Environment: {st.session_state.get('environment', 'N/A')}
# # - Application: {st.session_state.get('application', 'N/A')}
# # - DB Status: {st.session_state.get('db_status', 'N/A')}
# # - API Status: {st.session_state.get('api_status', 'N/A')}
# # - Metrics Status: {st.session_state.get('metrics_status', 'N/A')}

# # Previous Conversation:
# # {chr(10).join(st.session_state['conversation_history'][-6:])}
# # """
        
# #         with st.spinner('Thinking...'):
# #             prompt = f"{context}\n\nUser: {user_input}\n\nAssistant:"
# #             response = model.generate_content(prompt)
# #             st.chat_message("assistant").write(response.text)
            
# #             # Store conversation
# #             st.session_state['conversation_history'].append(f"User: {user_input}")
# #             st.session_state['conversation_history'].append(f"Assistant: {response.text}")
# #     except Exception as e:
# #         st.error(f"Error: {str(e)}")



# import streamlit as st
# import time
# import re
# import requests
# import pandas as pd
# import streamlit.components.v1 as components
# import json
# from app.services import azure_insights
# import subprocess
# import plotly.express as px
# st.set_page_config(page_title="Diagnosis Bot")
# import google.generativeai as genai

# # Initialize all session state variables first
# if 'conversation_history' not in st.session_state:
#     st.session_state['conversation_history'] = []
# if 'pending_input' not in st.session_state:
#     st.session_state['pending_input'] = None
# if 'health_check_completed' not in st.session_state:
#     st.session_state['health_check_completed'] = False
# if 'auto_input_processed' not in st.session_state:
#     st.session_state['auto_input_processed'] = False
# if 'health_check_data' not in st.session_state:
#     st.session_state['health_check_data'] = None

# # Get application name from URL parameters
# app_from_url = st.query_params.get('app', None)
# env_from_url = st.query_params.get('env', None)

# st.image("src/ValueMomentum_logo.png", width=150)
# st.markdown(
#     '''<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 40px;">
#         <h1 style="margin: 0; font-size: 3em; color: #34495e;">App Diagnosis Bot</h1>
#          </div>''', unsafe_allow_html=True)

# def extract_environment_and_app(user_input):
#     text = user_input.lower()
#     env_patterns = {
#         'dev': ['dev', 'development'],
#         'uat': ['uat', 'qa', 'test'],
#         'prod': ['prod', 'production']
#     }
#     environment = None
#     application = None
#     for env_key, env_values in env_patterns.items():
#         for env_val in env_values:
#             if env_val in text:
#                 environment = env_key
#                 break
#         if environment:
#             break
#     app_match = re.search(r'on\s+(\w+)\s+application', text)
#     if app_match:
#         application = app_match.group(1)
#     else:
#         app_match = re.search(r'(?:for|in)\s+(\w+)', text)
#         if app_match:
#             application = app_match.group(1)
#     return environment, application

# def display_health_check_results(health_data):
#     """Display stored health check results with progress bars"""
#     st.chat_message("assistant").write(f"Running Dependency validation for **{health_data['application'].title().upper()}** application on **{health_data['environment'].upper()}** environment...")
    
#     # Display phase results with progress bars
#     for phase_name, phase_data in health_data['phases'].items():
#         container = st.container()
#         with container:
#             col1, col2 = st.columns([2, 1])
#             with col1:
#                 st.write(f"**{phase_name}**")
#             with col2:
#                 if phase_data['status'] == 'success':
#                     st.write("✅")
#                     if phase_name == "DB Connection":
#                         st.write(f"Status: {phase_data['details']}")
#                     elif phase_name == "Dependencies":
#                         st.write(phase_data['details'])
#                     elif phase_name == "Metrics":
#                         st.write(f"Status: {phase_data['status_text']}")
#                         st.write(f"Latency: {phase_data['latency']}")
#                 else:
#                     st.write("❌")
            
#             # Add progress bar placeholder for visual consistency
#             progress_placeholder = st.empty()
#             with progress_placeholder:
#                 progress_bar = st.progress(100)  # Show completed progress bar
    
#     # Display CPU Usage
#     if 'powershell_output' in health_data:
#         st.subheader("CPU Usage")
#         st.code(health_data['powershell_output'], language="powershell")
    
#     # Display Azure Insights
#     if 'azure_data' in health_data:
#         st.subheader("Operation Summary")
#         operations_df = pd.DataFrame(health_data['azure_data'])
        
#         business_functions = ['Report Incident', 'Policy Search', 'New Claim', 'Submit Claim', 
#                             'Claims Dashboard', 'Payments', 'Policy Verification', 'Insured Details', 
#                             'Incident Details', 'Claims Summary']
        
#         chart_data = operations_df[['Operation Name', 'Successful Requests', 'Failed Requests']].head(10).copy()
#         chart_data['Business Function'] = business_functions[:len(chart_data)]
#         chart_data = chart_data.melt(id_vars=['Business Function'], 
#                                    value_vars=['Successful Requests', 'Failed Requests'],
#                                    var_name='Request Type', value_name='Count')
        
#         fig = px.bar(chart_data, x='Business Function', y='Count', color='Request Type',
#                    title='Successful vs Failed Requests by Page',
#                    color_discrete_map={'Successful Requests': '#2E8B57', 'Failed Requests': '#DC143C'},
#                    text='Count')
#         fig.update_traces(textposition='inside', textangle=0)
#         fig.update_xaxes(tickangle=45)
#         st.plotly_chart(fig, use_container_width=True, key=f"display_chart_{health_data['application']}_{health_data['environment']}")
    
#     if not st.session_state['auto_input_processed']:
#         st.chat_message("assistant").write(f"✅ Validation Completed for {health_data['application'].title()} on {health_data['environment'].upper()}!")


# def run_health_check(user_input, environment, application):
#     """Run the health check process and store results"""
#     st.chat_message("assistant").write(f"Running Dependency validation for **{application.title().upper()}** application on **{environment.upper()}** environment...")
    
#     # Initialize health check data structure
#     health_data = {
#         'environment': environment,
#         'application': application,
#         'phases': {},
#         'powershell_output': '',
#         'azure_data': None
#     }
    
#     phases = ["DB Connection", "Dependencies", "Metrics"]
#     phase_containers = []
#     for phase in phases:
#         container = st.container()
#         with container:
#             col1, col2 = st.columns([2, 1])
#             with col1:
#                 st.write(f"**{phase}**")
#             with col2:
#                 status_placeholder = st.empty()
#             progress_placeholder = st.empty()
#         phase_containers.append((progress_placeholder, status_placeholder))
    
#     # Load API endpoints from JSON file
#     with open("api_endpoints.json", "r") as f:
#         api_endpoints = json.load(f)
    
#     for phase, (progress_placeholder, status_placeholder) in zip(phases, phase_containers):
#         endpoint = api_endpoints[phase]
#         with progress_placeholder:
#             progress_bar = st.progress(0)
#             for j in range(101):
#                 progress_bar.progress(j / 100)
#                 time.sleep(0.01)
#         try:
#             response = requests.get(endpoint, timeout=5)
#             if response.status_code == 200:
#                 data = response.json()
                
#                 with status_placeholder:
#                     st.write("✅")
#                     if phase == "DB Connection":
#                         db = data.get("data", {})
#                         status = data.get('status', 'N/A')
#                         st.write(f"Status: {status}")
#                         st.session_state['db_status'] = status
#                         health_data['phases'][phase] = {
#                             'status': 'success',
#                             'details': status
#                         }
                       
#                     elif phase == "Dependencies":
#                         api = data.get("data", {})
#                         details = api.get("details", {})
#                         api_info = f"APIs Tested: {details.get('apis_tested', 'N/A')}; APIs Passed: {details.get('apis_passed', 'N/A')}; APIs Failed: {details.get('apis_failed', 'N/A')}"
#                         st.write(api_info)
#                         st.session_state['api_status'] = api_info
#                         health_data['phases'][phase] = {
#                             'status': 'success',
#                             'details': api_info
#                         }
                        
#                     elif phase == "Metrics":
#                         metrics = data.get("data", {})
#                         metrics_info = f"Status: {metrics.get('status')}, Latency: {metrics.get('latency_ms', 'N/A'):.2f} ms"
#                         st.write(f"Status: {metrics.get('status')}")
#                         st.write(f"Latency: {metrics.get('latency_ms', 'N/A'):.2f} ms")
#                         st.session_state['metrics_status'] = metrics_info
#                         health_data['phases'][phase] = {
#                             'status': 'success',
#                             'status_text': metrics.get('status'),
#                             'latency': f"{metrics.get('latency_ms', 'N/A'):.2f} ms"
#                         }
#             else:
#                 with status_placeholder:
#                     st.write("❌")
#                 health_data['phases'][phase] = {'status': 'failed'}
                   
#         except Exception as e:
#             with status_placeholder:
#                 st.write("❌")
#             health_data['phases'][phase] = {'status': 'failed'}
                
#     # CPU Usage section
#     st.subheader("CPU Usage")
#     output_placeholder = st.empty()
#     status_placeholder = st.empty()
    
#     try:
#         process = subprocess.Popen(
#             ["powershell", "-ExecutionPolicy", "Bypass", "-File", "upd_metrics.ps1"],
#             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True
#         )
        
#         output_lines = []
#         while True:
#             line = process.stdout.readline()
#             if line:
#                 output_lines.append(line.strip())
#                 output_placeholder.code("\n".join(output_lines), language="powershell")
#                 time.sleep(0.1)
#             elif process.poll() is not None:
#                 break
        
#         powershell_output = "\n".join(output_lines)
#         st.session_state['powershell_output'] = powershell_output
#         health_data['powershell_output'] = powershell_output
#         process.wait()
                
#     except FileNotFoundError:
#         status_placeholder.error("❌ metrics-2.ps1 not found")
#     except Exception as e:
#        status_placeholder.error(f"❌ Error running PowerShell script: {str(e)}")
    
#     # Loading Azure Insights with progress indicator
#     with st.spinner('Loading Azure Application Insights data...'):
#         st.info("Fetching operation metrics and user analytics...")
#         output = azure_insights.get_insights()
    
#     # Display Operation Summary table
#     if 'operation_summary' in output:
#         st.subheader("Operation Summary")
#         operations_df = pd.DataFrame(output['operation_summary'])
#         st.session_state['azure_data'] = operations_df.to_dict('records')
#         health_data['azure_data'] = operations_df.to_dict('records')
        
#         business_functions = ['Report Incident', 'Policy Search', 'New Claim', 'Submit Claim', 
#                             'Claims Dashboard', 'Payments', 'Policy Verification', 'Insured Details', 
#                             'Incident Details', 'Claims Summary']
        
#         chart_data = operations_df[['Operation Name', 'Successful Requests', 'Failed Requests']].head(10).copy()
#         chart_data['Business Function'] = business_functions[:len(chart_data)]
#         chart_data = chart_data.melt(id_vars=['Business Function'], 
#                                    value_vars=['Successful Requests', 'Failed Requests'],
#                                    var_name='Request Type', value_name='Count')
        
#         fig = px.bar(chart_data, x='Business Function', y='Count', color='Request Type',
#                    title='Successful vs Failed Requests by Page',
#                    color_discrete_map={'Successful Requests': '#2E8B57', 'Failed Requests': '#DC143C'},
#                    text='Count')
#         fig.update_traces(textposition='inside', textangle=0)
#         fig.update_xaxes(tickangle=45)
#         st.plotly_chart(fig, use_container_width=True, key=f"run_chart_{application}_{environment}_{int(time.time())}")
    
#     time.sleep(1)
#     col1, col2, col3 = st.columns([2, 1, 2])
    
#     st.chat_message("assistant").write(f"✅ Validation Completed for **{application.title().upper()}** on **{environment.upper()}**!")
    
#     # Store health check data and completion
#     st.session_state['health_check_data'] = health_data
#     if not st.session_state['auto_input_processed']:
#         st.session_state['conversation_history'].append(f"User: {user_input}")
#     st.session_state['conversation_history'].append(f"Assistant: Health check completed for **{application.upper()}** on **{environment.upper()}**")
#     st.session_state['health_check_completed'] = True
    
#     # with col2:
#     #     if st.button("Root Cause Analysis"):
#     #         components.html('<script>window.open("https://teams.microsoft.com/l/app/f6405520-7907-4464-8f6e-9889e2fb7d8f?source=app-header-share-entrypoint&templateInstanceId=19a6974b-869b-465b-b040-5da5fdab88d6&environment=Default-13085c86-4bcb-460a-a6f0-b373421c6323", "_blank")</script>', height=0)

# # Display stored health check results if available
# if st.session_state['health_check_data']:
#     display_health_check_results(st.session_state['health_check_data'])

# # Display conversation history (after health check visuals)
# for msg in st.session_state['conversation_history'][-10:]:
#     if msg.startswith('User: '):
#         st.chat_message("user").write(msg[6:])
#     elif msg.startswith('Assistant: '):
#         st.chat_message("assistant").write(msg[11:])

# # Process URL parameters only once
# if app_from_url and env_from_url and not st.session_state['auto_input_processed']:
#     user_input = f"run health check for {app_from_url} application in {env_from_url} environment"
#     st.session_state['auto_input_processed'] = True
    
#     environment, application = extract_environment_and_app(user_input)
#     st.session_state['environment'] = environment
#     st.session_state['application'] = application
    
#     if environment and application:
#         run_health_check(user_input, environment, application)
#         st.rerun()

# # Handle pending input from chat
# if st.session_state['pending_input']:
#     user_input_pending = st.session_state['pending_input']
#     st.session_state['pending_input'] = None
    
#     # Check if it's a health check request
#     if ("health check" in user_input_pending.lower() or "check health" in user_input_pending.lower()):
#         environment, application = extract_environment_and_app(user_input_pending)
#         st.session_state['environment'] = environment
#         st.session_state['application'] = application
        
#         if environment and application:
#             st.session_state['health_check_completed'] = False
#             run_health_check(user_input_pending, environment, application)
#             st.rerun()
#         elif environment:
#             st.chat_message("assistant").write(f"I found the environment ({environment.upper()}) but couldn't identify the application. Please specify the application name.")
#             st.session_state['conversation_history'].append(f"User: {user_input_pending}")
#             st.session_state['conversation_history'].append(f"Assistant: I found the environment ({environment.upper()}) but couldn't identify the application. Please specify the application name.")
#         elif application:
#             st.chat_message("assistant").write(f"I found the application ({application.title()}) but couldn't identify the environment. Please specify: Dev, UAT, or Prod.")
#             st.session_state['conversation_history'].append(f"User: {user_input_pending}")
#             st.session_state['conversation_history'].append(f"Assistant: I found the application ({application.title()}) but couldn't identify the environment. Please specify: Dev, UAT, or Prod.")
#         else:
#             st.chat_message("assistant").write("Please specify both the environment (Dev/UAT/Prod) and application name for the smoke test.")
#             st.session_state['conversation_history'].append(f"User: {user_input_pending}")
#             st.session_state['conversation_history'].append(f"Assistant: Please specify both the environment (Dev/UAT/Prod) and application name for the smoke test.")
#     else:
#         # Handle as general query with Gemini
#         st.chat_message("user").write(user_input_pending)
#         try:
#             genai.configure(api_key="AIzaSyBvBnlgt1z0JUG7mW-qCOwT4MMOaUSjrao")
#             model = genai.GenerativeModel('gemini-2.5-flash')
            
#             context = f"""
# Health Check Context:
# - Environment: {st.session_state.get('environment', 'N/A')}
# - Application: {st.session_state.get('application', 'N/A')}

# - Logs :{st.session_state.get('powershell_output','N/A')}

# Previous Conversation:
# {chr(10).join(st.session_state['conversation_history'][-6:])}
# """
# #- DB Status: {st.session_state.get('db_status', 'N/A')}
# # - API Status: {st.session_state.get('api_status', 'N/A')}
# # - Metrics Status: {st.session_state.get('metrics_status', 'N/A')}
            
#             with st.spinner('Thinking...'):
#                 prompt = f"{context}\n\nUser: {user_input_pending}\n\nAssistant:"
#                 response = model.generate_content(prompt)
#                 st.chat_message("assistant").write(response.text)
                
#                 # Store conversation
#                 st.session_state['conversation_history'].append(f"User: {user_input_pending}")
#                 st.session_state['conversation_history'].append(f"Assistant: {response.text}")
#         except Exception as e:
#             st.error(f"Error: {str(e)}")

# # Always show chat input at the bottom for follow-up questions
# user_input_new = st.chat_input("Ask questions about the health check results...")
# if user_input_new:
#     # Set the new input and rerun to process it
#     st.session_state['pending_input'] = user_input_new
#     st.rerun()


# import streamlit as st
# import time
# import re
# import requests
# import pandas as pd
# import streamlit.components.v1 as components
# import json
# from app.services import azure_insights
# import subprocess
# import plotly.express as px
# st.set_page_config(page_title="Diagnosis Bot")
# import google.generativeai as genai

# # Initialize all session state variables first
# if 'conversation_history' not in st.session_state:
#     st.session_state['conversation_history'] = []
# if 'pending_input' not in st.session_state:
#     st.session_state['pending_input'] = None
# if 'health_check_completed' not in st.session_state:
#     st.session_state['health_check_completed'] = False
# if 'auto_input_processed' not in st.session_state:
#     st.session_state['auto_input_processed'] = False
# # CHANGED: Store multiple health checks instead of just one
# if 'health_check_history' not in st.session_state:
#     st.session_state['health_check_history'] = []

# # Get application name from URL parameters
# app_from_url = st.query_params.get('app', None)
# env_from_url = st.query_params.get('env', None)

# st.image("src/ValueMomentum_logo.png", width=150)
# st.markdown(
#     '''<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 40px;">
#         <h1 style="margin: 0; font-size: 3em; color: #34495e;">App Diagnosis Bot</h1>
#          </div>''', unsafe_allow_html=True)

# def extract_environment_and_app(user_input):
#     text = user_input.lower()
#     env_patterns = {
#         'dev': ['dev', 'development'],
#         'uat': ['uat', 'qa', 'test'],
#         'prod': ['prod', 'production']
#     }
#     environment = None
#     application = None
#     for env_key, env_values in env_patterns.items():
#         for env_val in env_values:
#             if env_val in text:
#                 environment = env_key
#                 break
#         if environment:
#             break
#     app_match = re.search(r'on\s+(\w+)\s+application', text)
#     if app_match:
#         application = app_match.group(1)
#     else:
#         app_match = re.search(r'(?:for|in)\s+(\w+)', text)
#         if app_match:
#             application = app_match.group(1)
#     return environment, application

# def display_health_check_results(health_data, show_completion_message=True):
#     """Display stored health check results with progress bars"""
#     st.chat_message("assistant").write(f"Running Dependency validation for **{health_data['application'].title().upper()}** application on **{health_data['environment'].upper()}** environment...")
    
#     # Display phase results with progress bars
#     for phase_name, phase_data in health_data['phases'].items():
#         container = st.container()
#         with container:
#             col1, col2 = st.columns([2, 1])
#             with col1:
#                 st.write(f"**{phase_name}**")
#             with col2:
#                 if phase_data['status'] == 'success':
#                     st.write("✅")
#                     if phase_name == "DB Connection":
#                         st.write(f"Status: {phase_data['details']}")
#                     elif phase_name == "Dependencies":
#                         st.write(phase_data['details'])
#                     elif phase_name == "Metrics":
#                         st.write(f"Status: {phase_data['status_text']}")
#                         st.write(f"Latency: {phase_data['latency']}")
#                 else:
#                     st.write("❌")
            
#             # Add progress bar placeholder for visual consistency
#             progress_placeholder = st.empty()
#             with progress_placeholder:
#                 progress_bar = st.progress(100)  # Show completed progress bar
    
#     # Display CPU Usage
#     if 'powershell_output' in health_data:
#         st.subheader("CPU Usage")
#         st.code(health_data['powershell_output'], language="powershell")
    
#     # Display Azure Insights
#     if 'azure_data' in health_data:
#         st.subheader("Operation Summary")
#         operations_df = pd.DataFrame(health_data['azure_data'])
        
#         business_functions = ['Report Incident', 'Policy Search', 'New Claim', 'Submit Claim', 
#                             'Claims Dashboard', 'Payments', 'Policy Verification', 'Insured Details', 
#                             'Incident Details', 'Claims Summary']
        
#         chart_data = operations_df[['Operation Name', 'Successful Requests', 'Failed Requests']].head(10).copy()
#         chart_data['Business Function'] = business_functions[:len(chart_data)]
#         chart_data = chart_data.melt(id_vars=['Business Function'], 
#                                    value_vars=['Successful Requests', 'Failed Requests'],
#                                    var_name='Request Type', value_name='Count')
        
#         fig = px.bar(chart_data, x='Business Function', y='Count', color='Request Type',
#                    title='Successful vs Failed Requests by Page',
#                    color_discrete_map={'Successful Requests': '#2E8B57', 'Failed Requests': '#DC143C'},
#                    text='Count')
#         fig.update_traces(textposition='inside', textangle=0)
#         fig.update_xaxes(tickangle=45)
#         # CHANGED: Use timestamp to ensure unique key for each chart
#         chart_key = f"display_chart_{health_data['application']}_{health_data['environment']}_{health_data.get('timestamp', int(time.time()))}"
#         st.plotly_chart(fig, use_container_width=True, key=chart_key)
    
#     if show_completion_message:
#         st.chat_message("assistant").write(f"✅ Validation Completed for {health_data['application'].title()} on {health_data['environment'].upper()}!")


# def run_health_check(user_input, environment, application):
#     """Run the health check process and store results"""
#     st.chat_message("assistant").write(f"Running Dependency validation for **{application.title().upper()}** application on **{environment.upper()}** environment...")
    
#     # CHANGED: Add timestamp to health check data
#     health_data = {
#         'environment': environment,
#         'application': application,
#         'timestamp': int(time.time()),
#         'phases': {},
#         'powershell_output': '',
#         'azure_data': None
#     }
    
#     phases = ["DB Connection", "Dependencies", "Metrics"]
#     phase_containers = []
#     for phase in phases:
#         container = st.container()
#         with container:
#             col1, col2 = st.columns([2, 1])
#             with col1:
#                 st.write(f"**{phase}**")
#             with col2:
#                 status_placeholder = st.empty()
#             progress_placeholder = st.empty()
#         phase_containers.append((progress_placeholder, status_placeholder))
    
#     # Load API endpoints from JSON file
#     with open("api_endpoints.json", "r") as f:
#         api_endpoints = json.load(f)
    
#     for phase, (progress_placeholder, status_placeholder) in zip(phases, phase_containers):
#         endpoint = api_endpoints[phase]
#         with progress_placeholder:
#             progress_bar = st.progress(0)
#             for j in range(101):
#                 progress_bar.progress(j / 100)
#                 time.sleep(0.01)
#         try:
#             response = requests.get(endpoint, timeout=5)
#             if response.status_code == 200:
#                 data = response.json()
                
#                 with status_placeholder:
#                     st.write("✅")
#                     if phase == "DB Connection":
#                         db = data.get("data", {})
#                         status = data.get('status', 'N/A')
#                         st.write(f"Status: {status}")
#                         st.session_state['db_status'] = status
#                         health_data['phases'][phase] = {
#                             'status': 'success',
#                             'details': status
#                         }
                       
#                     elif phase == "Dependencies":
#                         api = data.get("data", {})
#                         details = api.get("details", {})
#                         api_info = f"APIs Tested: {details.get('apis_tested', 'N/A')}; APIs Passed: {details.get('apis_passed', 'N/A')}; APIs Failed: {details.get('apis_failed', 'N/A')}"
#                         st.write(api_info)
#                         st.session_state['api_status'] = api_info
#                         health_data['phases'][phase] = {
#                             'status': 'success',
#                             'details': api_info
#                         }
                        
#                     elif phase == "Metrics":
#                         metrics = data.get("data", {})
#                         metrics_info = f"Status: {metrics.get('status')}, Latency: {metrics.get('latency_ms', 'N/A'):.2f} ms"
#                         st.write(f"Status: {metrics.get('status')}")
#                         st.write(f"Latency: {metrics.get('latency_ms', 'N/A'):.2f} ms")
#                         st.session_state['metrics_status'] = metrics_info
#                         health_data['phases'][phase] = {
#                             'status': 'success',
#                             'status_text': metrics.get('status'),
#                             'latency': f"{metrics.get('latency_ms', 'N/A'):.2f} ms"
#                         }
#             else:
#                 with status_placeholder:
#                     st.write("❌")
#                 health_data['phases'][phase] = {'status': 'failed'}
                   
#         except Exception as e:
#             with status_placeholder:
#                 st.write("❌")
#             health_data['phases'][phase] = {'status': 'failed'}
                
#     # CPU Usage section
#     st.subheader("CPU Usage")
#     output_placeholder = st.empty()
#     status_placeholder = st.empty()
    
#     try:
#         process = subprocess.Popen(
#             ["powershell", "-ExecutionPolicy", "Bypass", "-File", "upd_metrics.ps1"],
#             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True
#         )
        
#         output_lines = []
#         while True:
#             line = process.stdout.readline()
#             if line:
#                 output_lines.append(line.strip())
#                 output_placeholder.code("\n".join(output_lines), language="powershell")
#                 time.sleep(0.1)
#             elif process.poll() is not None:
#                 break
        
#         powershell_output = "\n".join(output_lines)
#         st.session_state['powershell_output'] = powershell_output
#         health_data['powershell_output'] = powershell_output
#         process.wait()
                
#     except FileNotFoundError:
#         status_placeholder.error("❌ metrics-2.ps1 not found")
#     except Exception as e:
#        status_placeholder.error(f"❌ Error running PowerShell script: {str(e)}")
    
#     # Loading Azure Insights with progress indicator
#     with st.spinner('Loading Azure Application Insights data...'):
#         st.info("Fetching operation metrics and user analytics...")
#         output = azure_insights.get_insights()
    
#     # Display Operation Summary table
#     if 'operation_summary' in output:
#         st.subheader("Operation Summary")
#         operations_df = pd.DataFrame(output['operation_summary'])
#         st.session_state['azure_data'] = operations_df.to_dict('records')
#         health_data['azure_data'] = operations_df.to_dict('records')
        
#         business_functions = ['Report Incident', 'Policy Search', 'New Claim', 'Submit Claim', 
#                             'Claims Dashboard', 'Payments', 'Policy Verification', 'Insured Details', 
#                             'Incident Details', 'Claims Summary']
        
#         chart_data = operations_df[['Operation Name', 'Successful Requests', 'Failed Requests']].head(10).copy()
#         chart_data['Business Function'] = business_functions[:len(chart_data)]
#         chart_data = chart_data.melt(id_vars=['Business Function'], 
#                                    value_vars=['Successful Requests', 'Failed Requests'],
#                                    var_name='Request Type', value_name='Count')
        
#         fig = px.bar(chart_data, x='Business Function', y='Count', color='Request Type',
#                    title='Successful vs Failed Requests by Page',
#                    color_discrete_map={'Successful Requests': '#2E8B57', 'Failed Requests': '#DC143C'},
#                    text='Count')
#         fig.update_traces(textposition='inside', textangle=0)
#         fig.update_xaxes(tickangle=45)
#         st.plotly_chart(fig, use_container_width=True, key=f"run_chart_{application}_{environment}_{health_data['timestamp']}")
    
#     time.sleep(1)
#     col1, col2, col3 = st.columns([2, 1, 2])
    
#     st.chat_message("assistant").write(f"✅ Validation Completed for **{application.title().upper()}** on **{environment.upper()}**!")
    
#     # CHANGED: Append to health check history instead of replacing
#     st.session_state['health_check_history'].append(health_data)
    
#     if not st.session_state['auto_input_processed']:
#         st.session_state['conversation_history'].append(f"User: {user_input}")
#     st.session_state['conversation_history'].append(f"Assistant: Health check completed for **{application.upper()}** on **{environment.upper()}**")
#     st.session_state['health_check_completed'] = True

# # CHANGED: Display all stored health check results
# if st.session_state['health_check_history']:
#     for idx, health_data in enumerate(st.session_state['health_check_history']):
#         # Add separator between health checks if there are multiple
#         if idx > 0:
#             st.markdown("---")
#         # Don't show completion message for historical checks, only for the most recent
#         show_completion = (idx == len(st.session_state['health_check_history']) - 1)
#         display_health_check_results(health_data, show_completion_message=show_completion)

# # Display conversation history (after health check visuals)
# for msg in st.session_state['conversation_history'][-10:]:
#     if msg.startswith('User: '):
#         st.chat_message("user").write(msg[6:])
#     elif msg.startswith('Assistant: '):
#         st.chat_message("assistant").write(msg[11:])

# # Process URL parameters only once
# if app_from_url and env_from_url and not st.session_state['auto_input_processed']:
#     user_input = f"run health check for {app_from_url} application in {env_from_url} environment"
#     st.session_state['auto_input_processed'] = True
    
#     environment, application = extract_environment_and_app(user_input)
#     st.session_state['environment'] = environment
#     st.session_state['application'] = application
    
#     if environment and application:
#         run_health_check(user_input, environment, application)
#         st.rerun()

# # Handle pending input from chat
# if st.session_state['pending_input']:
#     user_input_pending = st.session_state['pending_input']
#     st.session_state['pending_input'] = None
    
#     # Check if it's a health check request
#     if ("health check" in user_input_pending.lower() or "check health" in user_input_pending.lower()):
#         environment, application = extract_environment_and_app(user_input_pending)
#         st.session_state['environment'] = environment
#         st.session_state['application'] = application
        
#         if environment and application:
#             st.session_state['health_check_completed'] = False
#             run_health_check(user_input_pending, environment, application)
#             st.rerun()
#         elif environment:
#             st.chat_message("assistant").write(f"I found the environment ({environment.upper()}) but couldn't identify the application. Please specify the application name.")
#             st.session_state['conversation_history'].append(f"User: {user_input_pending}")
#             st.session_state['conversation_history'].append(f"Assistant: I found the environment ({environment.upper()}) but couldn't identify the application. Please specify the application name.")
#         elif application:
#             st.chat_message("assistant").write(f"I found the application ({application.title()}) but couldn't identify the environment. Please specify: Dev, UAT, or Prod.")
#             st.session_state['conversation_history'].append(f"User: {user_input_pending}")
#             st.session_state['conversation_history'].append(f"Assistant: I found the application ({application.title()}) but couldn't identify the environment. Please specify: Dev, UAT, or Prod.")
#         else:
#             st.chat_message("assistant").write("Please specify both the environment (Dev/UAT/Prod) and application name for the smoke test.")
#             st.session_state['conversation_history'].append(f"User: {user_input_pending}")
#             st.session_state['conversation_history'].append(f"Assistant: Please specify both the environment (Dev/UAT/Prod) and application name for the smoke test.")
#     else:
#         # Handle as general query with Gemini
#         st.chat_message("user").write(user_input_pending)
#         try:
#             genai.configure(api_key="AIzaSyBvBnlgt1z0JUG7mW-qCOwT4MMOaUSjrao")
#             model = genai.GenerativeModel('gemini-2.5-flash')
            
#             # CHANGED: Build context from all health checks
#             health_checks_context = ""
#             for hc in st.session_state['health_check_history']:
#                 health_checks_context += f"\n- {hc['application'].upper()} on {hc['environment'].upper()}"
            
#             context = f"""
# Health Check Context:
# - Current Environment: {st.session_state.get('environment', 'N/A')}
# - Current Application: {st.session_state.get('application', 'N/A')}
# - All Health Checks Performed:{health_checks_context}

# - Latest Logs: {st.session_state.get('powershell_output','N/A')}

# Previous Conversation:
# {chr(10).join(st.session_state['conversation_history'][-6:])}
# """
            
#             with st.spinner('Thinking...'):
#                 prompt = f"{context}\n\nUser: {user_input_pending}\n\nAssistant:"
#                 response = model.generate_content(prompt)
#                 st.chat_message("assistant").write(response.text)
                
#                 # Store conversation
#                 st.session_state['conversation_history'].append(f"User: {user_input_pending}")
#                 st.session_state['conversation_history'].append(f"Assistant: {response.text}")
#         except Exception as e:
#             st.error(f"Error: {str(e)}")

# # Always show chat input at the bottom for follow-up questions
# user_input_new = st.chat_input("Ask questions about the health check results...")
# if user_input_new:
#     # Set the new input and rerun to process it
#     st.session_state['pending_input'] = user_input_new
#     st.rerun()

import streamlit as st
import time
import re
import requests
import pandas as pd
import streamlit.components.v1 as components
import json
from app.services import azure_insights
import subprocess
import plotly.express as px
st.set_page_config(page_title="Diagnosis Bot")
import google.generativeai as genai

# Initialize all session state variables first
if 'conversation_history' not in st.session_state:
    st.session_state['conversation_history'] = []
if 'pending_input' not in st.session_state:
    st.session_state['pending_input'] = None
if 'health_check_completed' not in st.session_state:
    st.session_state['health_check_completed'] = False
if 'auto_input_processed' not in st.session_state:
    st.session_state['auto_input_processed'] = False
# CHANGED: Store multiple health checks instead of just one
if 'health_check_history' not in st.session_state:
    st.session_state['health_check_history'] = []

# Get application name from URL parameters
app_from_url = st.query_params.get('app', None)
env_from_url = st.query_params.get('env', None)

st.image("src/ValueMomentum_logo.png", width=150)
st.markdown(
    '''<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 40px;">
        <h1 style="margin: 0; font-size: 3em; color: #34495e;">App Diagnosis Bot</h1>
         </div>''', unsafe_allow_html=True)

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

def display_health_check_results(health_data):
    """Display stored health check results with progress bars"""
    st.chat_message("assistant").write(f"Running Dependency validation for **{health_data['application'].title().upper()}** application on **{health_data['environment'].upper()}** environment...")
    
    # Display phase results with progress bars
    for phase_name, phase_data in health_data['phases'].items():
        container = st.container()
        with container:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{phase_name}**")
            with col2:
                if phase_data['status'] == 'success':
                    st.write("✅")
                    if phase_name == "DB Connection":
                        st.write(f"Status: {phase_data['details']}")
                    elif phase_name == "Dependencies":
                        st.write(phase_data['details'])
                    elif phase_name == "Metrics":
                        st.write(f"Status: {phase_data['status_text']}")
                        st.write(f"Latency: {phase_data['latency']}")
                else:
                    st.write("❌")
            
            # Add progress bar placeholder for visual consistency
            progress_placeholder = st.empty()
            with progress_placeholder:
                progress_bar = st.progress(100)  # Show completed progress bar
    
    # Display CPU Usage
    if 'powershell_output' in health_data:
        st.subheader("CPU Usage")
        st.code(health_data['powershell_output'], language="powershell")
    
    # Display Azure Insights
    if 'azure_data' in health_data:
        st.subheader("Operation Summary")
        operations_df = pd.DataFrame(health_data['azure_data'])
        
        business_functions = ['Report Incident', 'Policy Search', 'New Claim', 'Submit Claim', 
                            'Claims Dashboard', 'Payments', 'Policy Verification', 'Insured Details', 
                            'Incident Details', 'Claims Summary']
        
        chart_data = operations_df[['Operation Name', 'Successful Requests', 'Failed Requests']].head(10).copy()
        chart_data['Business Function'] = business_functions[:len(chart_data)]
        chart_data = chart_data.melt(id_vars=['Business Function'], 
                                   value_vars=['Successful Requests', 'Failed Requests'],
                                   var_name='Request Type', value_name='Count')
        
        fig = px.bar(chart_data, x='Business Function', y='Count', color='Request Type',
                   title='Successful vs Failed Requests by Page',
                   color_discrete_map={'Successful Requests': '#2E8B57', 'Failed Requests': '#DC143C'},
                   text='Count')
        fig.update_traces(textposition='inside', textangle=0)
        fig.update_xaxes(tickangle=45)
        # CHANGED: Use timestamp to ensure unique key for each chart
        chart_key = f"display_chart_{health_data['application']}_{health_data['environment']}_{health_data.get('timestamp', int(time.time()))}"
        st.plotly_chart(fig, use_container_width=True, key=chart_key)
    
    # CHANGED: Always show completion message immediately after the health check display
    st.chat_message("assistant").write(f"✅ Validation Completed for {health_data['application'].title().upper()} on {health_data['environment'].upper()}!")


def run_health_check(user_input, environment, application):
    """Run the health check process and store results"""
    st.chat_message("assistant").write(f"Running Dependency validation for **{application.title().upper()}** application on **{environment.upper()}** environment...")
    
    # CHANGED: Add timestamp to health check data
    health_data = {
        'environment': environment,
        'application': application,
        'timestamp': int(time.time()),
        'phases': {},
        'powershell_output': '',
        'azure_data': None
    }
    
    phases = ["DB Connection", "Dependencies", "Metrics"]
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
    
    # Load API endpoints from JSON file
    with open("api_endpoints.json", "r") as f:
        api_endpoints = json.load(f)
    
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
                
                with status_placeholder:
                    st.write("✅")
                    if phase == "DB Connection":
                        db = data.get("data", {})
                        status = data.get('status', 'N/A')
                        st.write(f"Status: {status}")
                        st.session_state['db_status'] = status
                        health_data['phases'][phase] = {
                            'status': 'success',
                            'details': status
                        }
                       
                    elif phase == "Dependencies":
                        api = data.get("data", {})
                        details = api.get("details", {})
                        api_info = f"APIs Tested: {details.get('apis_tested', 'N/A')}; APIs Passed: {details.get('apis_passed', 'N/A')}; APIs Failed: {details.get('apis_failed', 'N/A')}"
                        st.write(api_info)
                        st.session_state['api_status'] = api_info
                        health_data['phases'][phase] = {
                            'status': 'success',
                            'details': api_info
                        }
                        
                    elif phase == "Metrics":
                        metrics = data.get("data", {})
                        metrics_info = f"Status: {metrics.get('status')}, Latency: {metrics.get('latency_ms', 'N/A'):.2f} ms"
                        st.write(f"Status: {metrics.get('status')}")
                        st.write(f"Latency: {metrics.get('latency_ms', 'N/A'):.2f} ms")
                        st.session_state['metrics_status'] = metrics_info
                        health_data['phases'][phase] = {
                            'status': 'success',
                            'status_text': metrics.get('status'),
                            'latency': f"{metrics.get('latency_ms', 'N/A'):.2f} ms"
                        }
            else:
                with status_placeholder:
                    st.write("❌")
                health_data['phases'][phase] = {'status': 'failed'}
                   
        except Exception as e:
            with status_placeholder:
                st.write("❌")
            health_data['phases'][phase] = {'status': 'failed'}
                
    # CPU Usage section
    st.subheader("CPU Usage")
    output_placeholder = st.empty()
    status_placeholder = st.empty()
    
    try:
        if application.lower() == "infinity":

            process = subprocess.Popen(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", "infinity_metrics.ps1"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True
            )
            
            output_lines = []
            while True:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                    output_placeholder.code("\n".join(output_lines), language="powershell")
                    time.sleep(0.1)
                elif process.poll() is not None:
                    break
            
            powershell_output = "\n".join(output_lines)
            st.session_state['powershell_output'] = powershell_output
            health_data['powershell_output'] = powershell_output
            process.wait()
        else:
            process = subprocess.Popen(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", "upd_metrics.ps1"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True
            )
            
            output_lines = []
            while True:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                    output_placeholder.code("\n".join(output_lines), language="powershell")
                    time.sleep(0.1)
                elif process.poll() is not None:
                    break
            
            powershell_output = "\n".join(output_lines)
            st.session_state['powershell_output'] = powershell_output
            health_data['powershell_output'] = powershell_output
            process.wait()

                    
        # except FileNotFoundError:
        #     status_placeholder.error("❌ metrics-2.ps1 not found")
    except Exception as e:
            status_placeholder.error(f"❌ Error running PowerShell script: {str(e)}")
    
    # Loading Azure Insights with progress indicator
    with st.spinner('Loading Azure Application Insights data...'):
        st.info("Fetching operation metrics and user analytics...")
        output = azure_insights.get_insights()
    
    # Display Operation Summary table
    if 'operation_summary' in output:
        st.subheader("Operation Summary")
        operations_df = pd.DataFrame(output['operation_summary'])
        st.session_state['azure_data'] = operations_df.to_dict('records')
        health_data['azure_data'] = operations_df.to_dict('records')
        
        business_functions = ['Report Incident', 'Policy Search', 'New Claim', 'Submit Claim', 
                            'Claims Dashboard', 'Payments', 'Policy Verification', 'Insured Details', 
                            'Incident Details', 'Claims Summary']
        
        chart_data = operations_df[['Operation Name', 'Successful Requests', 'Failed Requests']].head(10).copy()
        chart_data['Business Function'] = business_functions[:len(chart_data)]
        chart_data = chart_data.melt(id_vars=['Business Function'], 
                                   value_vars=['Successful Requests', 'Failed Requests'],
                                   var_name='Request Type', value_name='Count')
        
        fig = px.bar(chart_data, x='Business Function', y='Count', color='Request Type',
                   title='Successful vs Failed Requests by Page',
                   color_discrete_map={'Successful Requests': '#2E8B57', 'Failed Requests': '#DC143C'},
                   text='Count')
        fig.update_traces(textposition='inside', textangle=0)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True, key=f"run_chart_{application}_{environment}_{health_data['timestamp']}")
    
    time.sleep(1)
    col1, col2, col3 = st.columns([2, 1, 2])
    
    st.chat_message("assistant").write(f"✅ Validation Completed for **{application.title().upper()}** on **{environment.upper()}**!")
    
    # CHANGED: Append to health check history instead of replacing
    st.session_state['health_check_history'].append(health_data)
    
    # CHANGED: Only add the user input to conversation history, not the completion message
    # The completion message is now part of the health check display itself
    if not st.session_state['auto_input_processed']:
        st.session_state['conversation_history'].append(f"User: {user_input}")
    st.session_state['health_check_completed'] = True

# CHANGED: Display all stored health check results
if st.session_state['health_check_history']:
    for idx, health_data in enumerate(st.session_state['health_check_history']):
        # Add separator between health checks if there are multiple
        if idx > 0:
            st.markdown("---")
        display_health_check_results(health_data)

# Display conversation history (after health check visuals) - but exclude health check queries
for msg in st.session_state['conversation_history'][-10:]:
    # Skip displaying user queries that triggered health checks - they're shown in the health check display
    if msg.startswith('User: ') and ('health check' in msg.lower() or 'check health' in msg.lower()):
        continue
    
    if msg.startswith('User: '):
        st.chat_message("user").write(msg[6:])
    elif msg.startswith('Assistant: '):
        st.chat_message("assistant").write(msg[11:])

# Process URL parameters only once
if app_from_url and env_from_url and not st.session_state['auto_input_processed']:
    user_input = f"run health check for {app_from_url} application in {env_from_url} environment"
    st.session_state['auto_input_processed'] = True
    
    environment, application = extract_environment_and_app(user_input)
    st.session_state['environment'] = environment
    st.session_state['application'] = application
    
    if environment and application:
        run_health_check(user_input, environment, application)
        st.rerun()

# Handle pending input from chat
if st.session_state['pending_input']:
    user_input_pending = st.session_state['pending_input']
    st.session_state['pending_input'] = None
    
    # Check if it's a health check request
    if ("health check" in user_input_pending.lower() or "check health" in user_input_pending.lower()):
        environment, application = extract_environment_and_app(user_input_pending)
        st.session_state['environment'] = environment
        st.session_state['application'] = application
        
        if environment and application:
            st.session_state['health_check_completed'] = False
            run_health_check(user_input_pending, environment, application)
            st.rerun()
        elif environment:
            st.chat_message("assistant").write(f"I found the environment ({environment.upper()}) but couldn't identify the application. Please specify the application name.")
            st.session_state['conversation_history'].append(f"User: {user_input_pending}")
            st.session_state['conversation_history'].append(f"Assistant: I found the environment ({environment.upper()}) but couldn't identify the application. Please specify the application name.")
        elif application:
            st.chat_message("assistant").write(f"I found the application ({application.title()}) but couldn't identify the environment. Please specify: Dev, UAT, or Prod.")
            st.session_state['conversation_history'].append(f"User: {user_input_pending}")
            st.session_state['conversation_history'].append(f"Assistant: I found the application ({application.title()}) but couldn't identify the environment. Please specify: Dev, UAT, or Prod.")
        else:
            st.chat_message("assistant").write("Please specify both the environment (Dev/UAT/Prod) and application name for the smoke test.")
            st.session_state['conversation_history'].append(f"User: {user_input_pending}")
            st.session_state['conversation_history'].append(f"Assistant: Please specify both the environment (Dev/UAT/Prod) and application name for the smoke test.")
    else:
        # Handle as general query with Gemini
        st.chat_message("user").write(user_input_pending)
        try:
            genai.configure(api_key="AIzaSyBvBnlgt1z0JUG7mW-qCOwT4MMOaUSjrao")
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # CHANGED: Build context from all health checks
            health_checks_context = ""
            for hc in st.session_state['health_check_history']:
                health_checks_context += f"\n- {hc['application'].upper()} on {hc['environment'].upper()}"
            
            context = f"""
Health Check Context:
- Current Environment: {st.session_state.get('environment', 'N/A')}
- Current Application: {st.session_state.get('application', 'N/A')}
- All Health Checks Performed:{health_checks_context}

- Latest Logs: {st.session_state.get('powershell_output','N/A')}

Previous Conversation:
{chr(10).join(st.session_state['conversation_history'][-6:])}
"""
            
            with st.spinner('Thinking...'):
                prompt = f"{context}\n\nUser: {user_input_pending}\n\nAssistant:"
                response = model.generate_content(prompt)
                st.chat_message("assistant").write(response.text)
                
                # Store conversation
                st.session_state['conversation_history'].append(f"User: {user_input_pending}")
                st.session_state['conversation_history'].append(f"Assistant: {response.text}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Always show chat input at the bottom for follow-up questions
user_input_new = st.chat_input("Ask questions about the health check results...")
if user_input_new:
    # Set the new input and rerun to process it
    st.session_state['pending_input'] = user_input_new
    st.rerun()