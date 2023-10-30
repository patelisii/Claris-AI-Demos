import streamlit as st

from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun

from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.environ.get("OPENAI_KEY")

with st.sidebar:
    pass

st.title("🤖 AWS Cloud Practitioner Search")

"""
Ask me about any AWS Service and I will tell you all about it using up to date information. 
"""

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful tutor for the AWS Cloud Practitioner exam. Your job is to teach the user about the AWS Service they are asking about. When teaching about an AWS Service, always relate how the service is relevant to the AWS Cloud Practitioner Exam. If you don't know the answer to something, you look it up."},
        {"role": "assistant", "content": "Hi, I'm a chatbot who can help you learn about AWS Services. What would you like to learn about today?"}
    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="Who won the Women's U.S. Open in 2018?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True)
    search = DuckDuckGoSearchRun(name="Search")
    search_agent = initialize_agent([search], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True, verbose=True)
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)