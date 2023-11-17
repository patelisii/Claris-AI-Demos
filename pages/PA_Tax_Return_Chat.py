import streamlit as st

import os
from dotenv import load_dotenv

from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.tools import tool
from langchain.docstore.document import Document

from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent, create_retriever_tool
from langchain.tools import DuckDuckGoSearchRun
from langchain.chat_models import ChatOpenAI

from langchain.callbacks import StreamlitCallbackHandler

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ.get("OPENAI_KEY")

loader = PyPDFLoader('tax_docs/pa_tax_return.pdf')
pages = loader.load_and_split()

faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
retriever = faiss_index.as_retriever(k=2)

@tool("AWS_question_search", return_direct=True)
def search_api(query: str) -> list[Document]:
    """Searches the API for the query."""
    return retriever.invoke(query)

# Create retriever tool
retriever_tool = create_retriever_tool(retriever, 
                                       "PA Tax Return Instructions", 
                                       "This tool searched through the Pennsylvania Tax Return Instructions released by the government.") 

# Create web search tool
web_tool = DuckDuckGoSearchRun(name="Web search for if the user asks specifically about recent or future changes to policies.")

# List of tools
tools = [retriever_tool, web_tool]


with st.sidebar:
    pass

st.title("🤖 PA Tax Law Search")

"""
Ask me about any Tax Policies and I will tell you all about it using up to date information. 
"""

if "taxchat_messages" not in st.session_state:
    st.session_state["taxchat_messages"] = [
        {"role": "system", "content": "You are a helpful assistant who answers questions about PA tax law. "},
        {"role": "assistant", "content": "Hi, I'm a chatbot who can help you learn about PA tax laws. What would you like to learn about today?"}
    ]

for msg in st.session_state.taxchat_messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What are the main components of a 2023 PA tax return?"):
    st.session_state.taxchat_messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", streaming=True)
    search_agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True, verbose=True)
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = search_agent.run(st.session_state.taxchat_messages, callbacks=[st_cb])
        st.session_state.taxchat_messages.append({"role": "assistant", "content": response})
        st.write(response)