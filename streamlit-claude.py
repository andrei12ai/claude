import streamlit as st
import anthropic
from typing import List

# Initialize the page configuration
st.set_page_config(page_title="Chat with Claude", layout="wide")

# Initialize session state for message history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

def initialize_client():
    """Initialize the Anthropic client with API key."""
    if 'api_key' not in st.session_state:
        st.session_state.api_key = None
        st.session_state.client = None

def create_client(api_key: str):
    """Create Anthropic client with the provided API key."""
    try:
        st.session_state.client = anthropic.Anthropic(api_key=api_key)
        st.session_state.api_key = api_key
        return True
    except Exception as e:
        st.error(f"Error initializing client: {str(e)}")
        return False

def get_claude_response(messages: List[dict]) -> str:
    """Get a response from Claude using the messages API."""
    try:
        response = st.session_state.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1024,
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        st.error(f"Error getting response: {str(e)}")
        return None

# Initialize the Anthropic client
initialize_client()

# Main app layout
st.title("💬 Chat with Claude")

# API key input section
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Anthropic API key", type="password")
    if api_key and api_key != st.session_state.api_key:
        if create_client(api_key):
            st.success("API key configured successfully!")

# Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to ask Claude?"):
    if not st.session_state.client:
        st.error("Please configure your API key first!")
    else:
        # Add user message to state and display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get Claude's response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            messages_for_claude = [
                {"role": m["role"], "content": m["content"]} 
                for m in st.session_state.messages
            ]
            response = get_claude_response(messages_for_claude)
            
            if response:
                message_placeholder.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Add a button to clear chat history
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()
