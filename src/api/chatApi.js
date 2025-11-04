// src/api/chatApi.js

export async function sendMessageToBackend(message) {
  if (!message || !message.trim()) {
    return { reply: "Please type a valid message." };
  }

  try {
    // Set a timeout for fetch (optional, 10s)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 40000);

    const response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      console.error("Backend returned error:", response.statusText);
      return { reply: "Server error. Please try again." };
    }

    const data = await response.json();

    if (!data.reply) {
      return { reply: "No reply received from backend." };
    }

    return data; // { reply: "..." }
  } catch (err) {
    if (err.name === "AbortError") {
      console.error("Request timed out");
      return { reply: "Server took too long to respond." };
    }
    console.error("Backend error:", err);
    return { reply: "Server error. Please try again." };
  }
}
