from pathlib import Path

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredExcelLoader,
)

docs = []

folder_path = Path("C:/Users/tomershi/Documents/new_documents_for_py")


def get_loader(file_path):
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return PyPDFLoader(str(file_path))

    elif suffix == ".docx":
        return Docx2txtLoader(str(file_path))

    elif suffix == ".txt":
        return TextLoader(str(file_path), encoding="utf-8")

    elif suffix in [".xlsx", ".xls"]:
        return UnstructuredExcelLoader(str(file_path))

    else:
        return None


for file_path in folder_path.iterdir():
    if file_path.is_file():
        print(f"Checking file: {file_path.name}")

        loader = get_loader(file_path)

        if loader is None:
            print(f"Skipping unsupported file type: {file_path.name}")
            continue

        loaded_docs = loader.load()
        docs.extend(loaded_docs)

        print(f"Loaded: {file_path.name} | chunks: {len(loaded_docs)}")


print(f"\nTotal loaded documents/chunks: {len(docs)}")

for d in docs[:3]:
    print("----")
    print(d.page_content[:200])




#     import os

# os.environ["OPENAI_API_KEY"] = "[Credentials]"

# from langchain_openai import OpenAI, OpenAIEmbeddings
# from langchain_classic.chains import RetrievalQA
# from langchain_text_splitters import CharacterTextSplitter
# from langchain_community.vectorstores import FAISS


# splitter = CharacterTextSplitter(
#     chunk_size=500,
#     chunk_overlap=50
# )

# splits = splitter.split_documents(docs)

# print(f"Created {len(splits)} text chunks")

# embeddings = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])

# vectorstore = FAISS.from_documents(splits, embeddings)

# qa = RetrievalQA.from_chain_type(
#     llm=OpenAI(api_key=os.environ["OPENAI_API_KEY"]),
#     retriever=vectorstore.as_retriever(),
# )

# query = "What happened in the phishing email investigation?"
# answer = qa.run(query)

# print("\nQuestion:")
# print(query)

# print("\nAnswer:")
# print(answer)