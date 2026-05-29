import streamlit as st
import pandas as pd
from financial_agent import analyze_spending_query

def render_ai_agent(filtered_df: pd.DataFrame) -> None:
    """
    Renders the Conversational AI Financial Agent view, including a persistent
    chat history interface, query inputs, quick prompt suggestions, and connection
    status indications.

    Parameters:
        filtered_df (pd.DataFrame): The filtered transaction database slice.
    """
    st.markdown("Interact with an AI agent to analyze your transaction records, spending behaviors, and budgets.")
    
    # Initialize chat history in session state if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "👋 Hello! I am your AI Financial Agent. Ask me questions about your spending, categories, or coffee habits!"
            }
        ]
        
    # Check Gemini API status
    api_key = st.session_state.get("gemini_api_key", "").strip()
    
    # ---------------------------------------------------------
    # Render Status Banner
    # ---------------------------------------------------------
    col_status1, col_status2 = st.columns([3, 1])
    with col_status1:
        if api_key:
            st.success("🔮 **Gemini AI Active**: LLM analysis enabled (using provided API Key).")
        else:
            st.info("🤖 **Local Engine Active**: Processing queries locally using pandas mathematical queries. (Add Gemini API Key in Settings for natural language summaries).")
            
    with col_status2:
        # Clear Chat button
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": "👋 Hello! I am your AI Financial Agent. Ask me questions about your spending, categories, or coffee habits!"
                }
            ]
            st.rerun()

    # ---------------------------------------------------------
    # Display Suggestion Prompts
    # ---------------------------------------------------------
    st.markdown("##### 💡 Try asking:")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    suggestions = [
        "What is my highest spend category?",
        "How much do I spend on coffee at Starbucks & Owl Night Cafe?",
        "Show me my category breakdown"
    ]
    
    # Helper to submit suggestions
    clicked_prompt = None
    with col_s1:
        if st.button(suggestions[0], use_container_width=True):
            clicked_prompt = suggestions[0]
    with col_s2:
        if st.button(suggestions[1], use_container_width=True):
            clicked_prompt = suggestions[1]
    with col_s3:
        if st.button(suggestions[2], use_container_width=True):
            clicked_prompt = suggestions[2]

    # ---------------------------------------------------------
    # Render Chat History
    # ---------------------------------------------------------
    st.markdown("---")
    
    # Loop and print previous chat entries
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])
            
    # ---------------------------------------------------------
    # Process New Input Query
    # ---------------------------------------------------------
    # Accept user typing OR clicked buttons
    user_query = st.chat_input("Ask a question about your spending habits...")
    if clicked_prompt:
        user_query = clicked_prompt
        
    if user_query:
        # 1. Print user message
        with st.chat_message("user"):
            st.markdown(user_query)
            
        # Append to log
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # 2. Get AI Agent response
        with st.spinner("Analyzing transaction data..."):
            response_text = analyze_spending_query(
                df=filtered_df,
                query=user_query,
                api_key=api_key
            )
            
        # Print assistant response
        with st.chat_message("assistant"):
            st.markdown(response_text)
            
        # Append to log
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
        
        # Rerun to refresh history window
        st.rerun()
