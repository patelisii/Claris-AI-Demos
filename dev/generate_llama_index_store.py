import os
from dotenv import load_dotenv

from llama_index import VectorStoreIndex, SimpleDirectoryReader

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.environ.get("OPENAI_KEY")

documents = SimpleDirectoryReader("tax_docs").load_data()


from llama_index.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
)
from llama_index.text_splitter import TokenTextSplitter

text_splitter = TokenTextSplitter(
    separator=" ", chunk_size=512, chunk_overlap=128
)
title_extractor = TitleExtractor(nodes=5)
qa_extractor = QuestionsAnsweredExtractor(questions=3)

# assume documents are defined -> extract nodes
from llama_index.ingestion import IngestionPipeline

pipeline = IngestionPipeline(
    transformations=[text_splitter, title_extractor, qa_extractor]
)

nodes = pipeline.run(
    documents=documents,
    in_place=True,
    show_progress=True,
)

from llama_index import ServiceContext, VectorStoreIndex
from llama_index.llms import OpenAI

service_context = ServiceContext.from_defaults(
    llm=OpenAI(model="gpt-3.5-turbo", temperature=0.2)
)

index = VectorStoreIndex(nodes, service_context=service_context)



# index.storage_context.persist(persist_dir="vector_store")

query_engine = index.as_query_engine(k=1)
response = query_engine.query("What was April Hensley's federal income tax witheld?")
print(response)
print(response.source_nodes)