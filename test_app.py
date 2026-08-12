import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/api/v1/query"

st.title("eVitals RPM Manual - RAG Tester")

query = st.text_input("Ask a question about the eVitals RPM Manual:")

if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching and generating answer..."):
            try:
                response = requests.post(API_URL, json={"query": query})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.subheader("Answer:")
                    st.write(data.get("answer"))
                    
                    st.subheader("Sources used:")
                    sources = data.get("sources", [])
                    if sources:
                        for idx, source in enumerate(sources):
                            module = source.get('module') or 'N/A'
                            task = source.get('task') or 'N/A'
                            subtask = source.get('subtask') or 'N/A'
                            st.markdown(f"**{idx+1}.** Module: `{module}` | Task: `{task}` | Subtask: `{subtask}`")
                    else:
                        st.info("No sources retrieved.")
                        
                elif response.status_code == 503:
                    st.error("Knowledge base not initialized. Please run `python ingest.py` first.")
                else:
                    st.error(f"Error from API: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the API. Is the FastAPI server running?")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
