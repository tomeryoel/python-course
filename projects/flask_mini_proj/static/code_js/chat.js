const chatForm = document.getElementById("chat-form");
const questionInput = document.getElementById("question-input");
const chatBox = document.getElementById("chat-box");
const clearBtn = document.getElementById("clear-btn");
const retrievedContextBox = document.getElementById("retrieved-context");

function addMessage(text, role) {
    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");

    if (role === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("assistant-message");
    }

    messageDiv.textContent = text;

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const question = questionInput.value.trim();

    if (question === "") {
        return;
    }

    addMessage(question, "user");

    questionInput.value = "";

    addMessage("Thinking...", "assistant");

    retrievedContextBox.textContent = "Retrieving relevant context...";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        const thinkingMessages = document.querySelectorAll(".assistant-message");
        const lastAssistantMessage = thinkingMessages[thinkingMessages.length - 1];

        if (!response.ok) {
            lastAssistantMessage.textContent = data.error || "Something went wrong.";
            retrievedContextBox.textContent = "No context available because the request failed.";
            return;
        }

        lastAssistantMessage.textContent = data.answer;

        if (data.retrieved_context) {
            retrievedContextBox.textContent = data.retrieved_context;
        } else {
            retrievedContextBox.textContent = "No retrieved context returned.";
        }

    } catch (error) {
        const thinkingMessages = document.querySelectorAll(".assistant-message");
        const lastAssistantMessage = thinkingMessages[thinkingMessages.length - 1];

        lastAssistantMessage.textContent = "Server error. Please try again.";
        retrievedContextBox.textContent = "No context available because the server failed.";

        console.error(error);
    }
});

clearBtn.addEventListener("click", async function () {
    await fetch("/api/clear", {
        method: "POST"
    });

    chatBox.innerHTML = "";
    retrievedContextBox.textContent = "No retrieved context yet.";

    addMessage(
        "Conversation memory cleared.",
        "assistant"
    );
});