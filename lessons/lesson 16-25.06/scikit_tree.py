import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# ========= Setup =========
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE"), temperature=0)

# ========= Define the state =========
class SupportState(TypedDict, total=False):
    message: str
    intent: str
    response: str

# ========= Node 1: Classify intent =========
def classify_intent(state: SupportState) -> SupportState:
    msg = state["message"].lower()
    if any(x in msg for x in ["error", "bug", "site", "login", "crash"]):
        intent = "technical"
    elif any(x in msg for x in ["refund", "invoice", "payment", "charged"]):
        intent = "billing"
    elif any(x in msg for x in ["lesson", "exercise", "explain", "understand"]):
        intent = "content"
    else:
        intent = "unknown"

    print(f"ðŸ§­ Intent classified as: {intent}")
    return {"intent": intent}

# ========= Node 2: Handle technical issues =========
def handle_technical(state: SupportState) -> SupportState:
    message = state["message"]
    prompt = f"""
    You are a technical support agent.
    The user said: {message}
    Provide clear steps to fix it.
    """
    resp = llm.invoke(prompt)
    return {"response": resp.content}

# ========= Node 3: Handle billing =========
def handle_billing(state: SupportState) -> SupportState:
    message = state["message"]
    prompt = f"""
    You are a billing assistant.
    The user said: {message}
    Explain politely how billing/refunds work and who to contact.
    """
    resp = llm.invoke(prompt)
    return {"response": resp.content}

# ========= Node 4: Handle content/help =========
def handle_content(state: SupportState) -> SupportState:
    message = state["message"]
    prompt = f"""
    You are a course tutor.
    The user said: {message}
    Give a short, friendly explanation to help them learn.
    """
    resp = llm.invoke(prompt)
    return {"response": resp.content}

# ========= Node 5: Fallback =========
def handle_unknown(state: SupportState) -> SupportState:
    message = state["message"]
    prompt = f"""
    You are a virtual assistant.
    The user said: {message}
    You are not sure what category this is.
    Ask them for clarification.
    """
    resp = llm.invoke(prompt)
    return {"response": resp.content}

# ========= Build the graph =========
graph = StateGraph(SupportState)

graph.add_node("classify", classify_intent)
graph.add_node("technical", handle_technical)
graph.add_node("billing", handle_billing)
graph.add_node("content", handle_content)
graph.add_node("unknown", handle_unknown)

# Entry point
graph.set_entry_point("classify")

# Branching edges â€” this is the *decision tree logic*
def route(state: SupportState):
    return state["intent"]

graph.add_conditional_edges(
    "classify",
    route,
    {
        "technical": "technical",
        "billing": "billing",
        "content": "content",
        "unknown": "unknown",
    },
)

# Each handler goes to END
for node in ["technical", "billing", "content", "unknown"]:
    graph.add_edge(node, END)

# Compile
app = graph.compile()

# ========= Run a few tests =========
if __name__ == "__main__":
    examples = [
        "I keep getting a login error on the website.",
        "I was double charged for the Python course.",
        "I don't understand how RAG works in the AI lesson.",
        "Hello, I just want to say thanks!",
    ]

    for msg in examples:
        print("\nðŸŸ© NEW MESSAGE:", msg)
        result = app.invoke({"message": msg})
        print("ðŸ’¬ Final Response:", result["response"])


# -----------------------------------------------
# Loan Decision Tree Visualization with scikit-learn
# -----------------------------------------------
import matplotlib.pyplot as plt
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
import numpy as np


# Features: [monthly_income, credit_score]
X = np.array([
    [2000, 550],   # low income, poor credit
    [3000, 600],   # low income, medium credit
    [7000, 720],   # high income, good credit
    [8000, 680],   # high income, medium credit
    [4000, 750],   # medium income, good credit
])

# Labels: 0 = reject, 1 = approve
y = np.array([0, 0, 1, 1, 1])


clf = DecisionTreeClassifier(max_depth=3, random_state=42)
clf.fit(X, y)

plt.figure(figsize=(10, 6))
tree.plot_tree(
    clf,
    feature_names=["Monthly Income", "Credit Score"],
    class_names=["Reject", "Approve"],
    filled=True,
    rounded=True,
    fontsize=10
)
plt.title("Loan Decision Tree (scikit-learn)")
plt.show()

