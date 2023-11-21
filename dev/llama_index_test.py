import os
from dotenv import load_dotenv

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ.get("OPENAI_KEY")

from llama_index import StorageContext, load_index_from_storage

# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="vector_store")

# load index
index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine(k=2)
response = query_engine.query("What was Laura Russo's federal income tax witheld?")
print(response)
