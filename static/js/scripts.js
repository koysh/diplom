document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const messages = document.getElementById("chat-messages");
    const fileInput = document.getElementById("fileInput");

    form.onsubmit = async (e) => {
        e.preventDefault();
        const input = document.getElementById("user-input");
        const userMessage = input.value.trim();

        if (userMessage) {
            messages.innerHTML += `<p><strong>Вы:</strong> ${userMessage}</p>`;

            const response = await fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: userMessage }),
            });

            const data = await response.json();
            messages.innerHTML += `<p><strong>AI:</strong> ${data.response}</p>`;
            input.value = "";
            messages.scrollTop = messages.scrollHeight;
        }
    };

    fileInput.onchange = async () => {
        const file = fileInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch("/upload", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            messages.innerHTML += `<p><strong>AI:</strong> ${data.message}</p>`;
        }
    };

    document.getElementById("chat-form").onsubmit = async (e) => {
        e.preventDefault(); 
    
        const input = document.getElementById("user-input");
        const userMessage = input.value.trim();
        if (!userMessage) return;
    
        const messages = document.getElementById("chat-messages");
        const userMessageElem = document.createElement("p");
        userMessageElem.innerHTML = `<strong>Вы:</strong> ${userMessage}`;
        messages.appendChild(userMessageElem);
    
        const formData = new FormData();
        formData.append("question", userMessage);
    
        try {
            const response = await fetch("/ask", {
                method: "POST",
                body: formData, 
            });
    
            if (response.ok) {
                const data = await response.json();
                const aiMessageElem = document.createElement("p");
                aiMessageElem.innerHTML = `<strong>AI:</strong> ${data.response}`;
                messages.appendChild(aiMessageElem);
            } else {
                throw new Error("Ошибка ответа сервера");
            }
        } catch (error) {
            console.error(error);
            const errorElem = document.createElement("p");
            errorElem.innerHTML = `<strong>AI:</strong> Произошла ошибка`;
            messages.appendChild(errorElem);
        }
    
        input.value = "";
        messages.scrollTop = messages.scrollHeight;
    };
    
});

function logout() {
    alert("Выход из системы...");
}
