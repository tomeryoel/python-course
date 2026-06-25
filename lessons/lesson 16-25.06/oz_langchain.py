import os

# hard-coded key
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY_HERE"

from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_classic.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS


def main():
    loader = TextLoader("docs/ai_notes.txt", encoding="utf-8")
    docs = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])
    vectorstore = FAISS.from_documents(splits, embeddings)

    qa = RetrievalQA.from_chain_type(
        llm=OpenAI(api_key=os.environ["OPENAI_API_KEY"]),
        retriever=vectorstore.as_retriever(),
    )

    query = "Explain the difference between LangChain and RAG"
    print(qa.run(query))


if __name__ == "__main__":
    main()






    
