document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const chatBox = document.getElementById('messages');

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const userInput = document.getElementById('user-input').value;
        if (userInput.trim() === "") return;

        // Добавляем сообщение пользователя в чат
        const userMessage = document.createElement('li');
        userMessage.className = 'user-message';
        userMessage.textContent = userInput;
        chatBox.appendChild(userMessage);

        // Отправляем запрос на сервер для ответа ИИ
        fetch('/ask_ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: userInput }),
        })
        .then(response => response.json())
        .then(data => {
            // Добавляем ответ ИИ в чат
            const aiMessage = document.createElement('li');
            aiMessage.className = 'ai-message';
            aiMessage.textContent = data.answer;
            chatBox.appendChild(aiMessage);
        });

        document.getElementById('user-input').value = '';
    });
});
