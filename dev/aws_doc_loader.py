import os
from dotenv import load_dotenv

from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.tools import tool
from langchain.docstore.document import Document

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ.get("OPENAI_KEY")

loader = PyPDFLoader('AWS_Docs/AWS-Certified-Cloud-Practitioner_Sample-Questions.pdf')
pages = loader.load_and_split()

faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
retriever = faiss_index.as_retriever(k=2)

@tool("AWS_question_search", return_direct=True)
def search_api(query: str) -> list[Document]:
    """Searches the API for the query."""
    return retriever.invoke(query)

# docs = search_api("How will the community be engaged?")
# for doc in docs:
#     print(str(doc.metadata["page"]) + ":", doc.page_content)
    
    
############### AGENT STUFF BELOW ###############


from langchain.agents.agent_toolkits import create_conversational_retrieval_agent, create_retriever_tool
from langchain.tools import DuckDuckGoSearchRun
from langchain.chat_models import ChatOpenAI


# Create retriever tool
retriever_tool = create_retriever_tool(retriever, 
                                       "aws_question_retriever", 
                                       "This tool searched for AWS Cloud practitioner exam practice questions") 

# Create web search tool
web_tool = DuckDuckGoSearchRun(name="Search")

# List of tools
tools = [retriever_tool, web_tool]

# Chat model 
llm = ChatOpenAI()  

# Create agent
agent = create_conversational_retrieval_agent(llm, tools)

from langchain.callbacks import StdOutCallbackHandler

# Create callback handler
callback = StdOutCallbackHandler() 

# Query agent
response = agent.run([{"role": "user", "content": "What is AWS Bedrock?"}], callbacks=[callback])

print(response)