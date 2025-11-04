import React, { useState, useRef, useEffect } from "react";
import { sendMessageToBackend } from "../api/chatApi";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const synth = useRef(window.speechSynthesis);
  const recognitionRef = useRef(null);
  const [listening, setListening] = useState(false);
  const [voiceLang, setVoiceLang] = useState("te-IN"); // Telugu default

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.lang = voiceLang;
      rec.interimResults = false;
      rec.maxAlternatives = 1;
      rec.onresult = (e) => { setText(e.results[0][0].transcript); setListening(false); };
      rec.onend = () => setListening(false);
      recognitionRef.current = rec;
    }
  }, []);

  useEffect(() => {
    if (recognitionRef.current) recognitionRef.current.lang = voiceLang;
  }, [voiceLang]);

  const startListening = () => {
    if (recognitionRef.current) { setListening(true); recognitionRef.current.start(); }
  };

  const speak = (txt) => {
    if (!synth.current) return;
    synth.current.cancel();
    const utter = new SpeechSynthesisUtterance(txt);
    utter.lang = voiceLang;
    synth.current.speak(utter);
  };

  const handleSend = async () => {
    if (!text.trim()) return;
    const userMsg = { sender: "user", message: text };
    setMessages(prev => [...prev, userMsg]);
    setText("");
    const data = await sendMessageToBackend(userMsg.message);
    const botMsg = { sender: "bot", message: data.reply };
    setMessages(prev => [...prev, botMsg]);
    speak(data.reply);
  };

  return (
    <div>
      <h2> Chatbot</h2>
      <div>
        <label>Language: </label>
        <select value={voiceLang} onChange={e => setVoiceLang(e.target.value)}>
          <option value="te-IN">Telugu</option>
          <option value="en-IN">English</option>
        </select>
      </div>

      <div style={{ height: 300, overflowY: "auto", border: "1px solid #ddd", margin: "10px 0" }}>
        {messages.map((m, i) => (
          <div key={i} style={{ textAlign: m.sender === "user" ? "right" : "left" }}>
            <b>{m.sender}:</b> {m.message}
          </div>
        ))}
      </div>

      <input value={text} onChange={e => setText(e.target.value)} placeholder="Type or speak your message" />
      <button onClick={handleSend}>Send</button>
      <button onClick={startListening} disabled={listening}>{listening ? "Listening..." : "Voice"}</button>
    </div>
  );
}
