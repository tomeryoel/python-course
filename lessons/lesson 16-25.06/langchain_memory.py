import os

# ðŸ” demo only â€“ put your real key here or load from env
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY_HERE"

from langchain_openai import OpenAI
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationBufferMemory

# LLM
llm = OpenAI(api_key=os.environ["OPENAI_API_KEY"], temperature=0)

# Memory (keeps ALL turns)
memory = ConversationBufferMemory(return_messages=True)

# Conversation chain
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True,  # shows the prompt being sent
)

print("Chat started. Type 'exit' to stop.\n")

while True:
    user_msg = input("You: ")
    if user_msg.lower() in ("exit", "quit", "q"):
        print("Bye")
        break

    # send to chain
    reply = conversation.predict(input=user_msg)
    print("Bot:", reply)

    # show current memory
    print("\n--- MEMORY NOW ---")
    mem_vars = memory.load_memory_variables({})
    # mem_vars["history"] is a list of messages (because return_messages=True)
    for m in mem_vars["history"]:
        role = m.type  # 'human' or 'ai'
        print(f"{role.upper()}: {m.content}")
    print("------------------\n")
