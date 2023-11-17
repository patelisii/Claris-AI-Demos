import streamlit as st

from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun


st.title("Claris AI Demos")

"""
Welcome to Claris AI's Demo Hub. Visit https://clarisai.webflow.io to get your custom demo made today!
"""

