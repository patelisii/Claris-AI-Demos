import streamlit as st

from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun


st.title("🤖 AWS Cloud Practitioner Tutor")

"""
Hello, I am a tutor to help you study for the AWS Cloud Practitioner Exam! Please choose a page on the left to get started.
"""

