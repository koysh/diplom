document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const messages = document.getElementById("chat-messages");
  const fileInput = document.getElementById("fileInput");

  let messagesArray = []; // Массив для хранения сообщений

  function scrollToBottom() {
    messages.scrollTop = messages.scrollHeight;
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    const input = document.getElementById("user-input");
    const userMessage = input.value.trim();

    if (!userMessage) return;

    // Добавляем сообщение пользователя в массив
    messagesArray.push({ role: "user", content: userMessage });

    // Отображаем сообщение пользователя в чате
    messages.innerHTML += `<p><strong>Вы:</strong> ${userMessage}</p>`;
    scrollToBottom();

    try {
        // Добавляем системное сообщение перед отправкой
        messagesArray.unshift({ 
            role: "system", 
            content: "Пожалуйста, учитывай, что содержимое файла было загружено и доступно для обсуждения." 
        });

        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ messages: messagesArray }), // Отправляем весь массив сообщений
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Ошибка при отправке сообщения:", errorText);
            throw new Error("Ошибка при отправке сообщения");
        }

        const data = await response.json();
        const aiMessage = data.response;

        // Добавляем ответ ИИ в массив
        messagesArray.push({ role: "assistant", content: aiMessage });
        console.log("Массив сообщений перед отправкой:", messagesArray);

        // Отображаем ответ ИИ в чате
        const escapedAiMessage = aiMessage.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        messages.innerHTML += `<p><strong>AI:</strong> ${escapedAiMessage}</p>`;
    } catch (error) {
        console.error("Ошибка обработки запроса:", error);
        messages.innerHTML += `<p><strong>Ошибка:</strong> ${error.message}</p>`;
    }

    input.value = ""; // Очищаем поле ввода
    scrollToBottom();
};

fileInput.onchange = async () => {
  const file = fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
      const response = await fetch("/upload", {
          method: "POST",
          body: formData,
      });

      if (!response.ok) {
          const errorText = await response.text();
          console.error("Ошибка загрузки файла:", errorText);
          throw new Error("Ошибка загрузки файла");
      }

      const data = await response.json();
      const analysis = data.analysis;
      const extractedText = data.extracted_text; // Получаем извлеченный текст

      // Логируем извлеченный текст
      console.log("Извлеченный текст:", extractedText);

      // Добавляем в массив сообщение о загруженном файле и его анализ
      messagesArray.push({ 
          role: "user", 
          content: `Загружен файл: ${file.name}`, 
          file_content: extractedText // Добавляем содержимое файла
      });
      messagesArray.push({ role: "assistant", content: analysis });

      // Логируем массив сообщений
      console.log("Массив сообщений перед отправкой:", messagesArray);

      // Отображаем анализ в чате
      const escapedAnalysis = analysis.replace(/</g, "&lt;").replace(/>/g, "&gt;");
      messages.innerHTML += `<p><strong>AI:</strong> ${escapedAnalysis}</p>`;
  } catch (error) {
      console.error("Ошибка обработки запроса:", error);
      messages.innerHTML += `<p><strong>Ошибка:</strong> ${error.message}</p>`;
  }

  scrollToBottom();
};

});