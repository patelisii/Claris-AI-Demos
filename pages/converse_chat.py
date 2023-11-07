import streamlit as st

from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.tools import DuckDuckGoSearchRun

from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent

from langchain.tools.render import render_text_description
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain import hub
from langchain.agents import AgentExecutor


from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.environ.get("OPENAI_KEY")

def create_agent():
    
    search = DuckDuckGoSearchRun(name="Search")
    tools = [
        Tool(
            name="Current Search",
            func=search.run,
            description="useful for when you need to answer questions about current events or the current state of the world",
        ),
    ]
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)

    prompt = hub.pull("hwchase17/react-chat")

    llm_with_stop = llm.bind(stop=["\nObservation"])

    agent = (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_stop
        | ReActSingleInputOutputParser()
    )

    memory = ConversationBufferMemory(memory_key="chat_history")
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)
    
    return agent_executor

with st.sidebar:
    pass

st.title("🤖 AWS Cloud Practitioner Converse")

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

    search_agent = create_agent()

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = search_agent.invoke({"input": st.session_state.messages[-1]})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)