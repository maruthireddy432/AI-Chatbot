// src/App.js

import React, { useState, useEffect, useRef } from "react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
import { sendMessageToBackend } from "./api/chatApi";
import { Send, Mic, User, Bot, CornerDownLeft, Settings } from 'lucide-react';
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! How can I help you today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const { transcript, listening, resetTranscript } = useSpeechRecognition();

  if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
    return <p>Browser does not support voice recognition</p>;
  }

  const startListening = () => {
    resetTranscript();
    SpeechRecognition.startListening({ continuous: true, language: "en-US" });
  };

  const stopListening = async () => {
    SpeechRecognition.stopListening();
    if (transcript) {
      await sendMessage(transcript);
      resetTranscript();
    }
  };

  const sendMessage = async (voiceMessage = null) => {
    const messageText = voiceMessage || input;
    if (!messageText.trim()) return;

    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const newMessage = { sender: "user", text: messageText, timestamp };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setIsTyping(true);

    try {
      const data = await sendMessageToBackend(messageText);
      let botResponseContent;
      
      // Handle both string and object responses from backend
      if (typeof data.reply === 'string') {
        botResponseContent = JSON.parse(data.reply);
      } else {
        botResponseContent = data.reply;
      }

      const botTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const botMessage = { sender: "bot", text: botResponseContent, timestamp: botTimestamp };
      setMessages((prev) => [...prev, botMessage]);

    } catch (err) {
      const errorTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const botMessage = { 
        sender: "bot", 
        text: [{ type: 'paragraph', content: 'Server error. Please try again.' }], 
        timestamp: errorTimestamp 
      };
      setMessages((prev) => [...prev, botMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const renderBotMessage = (messageContent) => {
    if (!Array.isArray(messageContent)) {
      return <p>{String(messageContent)}</p>;
    }
    return messageContent.map((block, index) => {
      switch (block.type) {
        case 'header':
          return <h3 key={index} className="bot-msg-header">{block.content}</h3>;
        case 'section':
          return (
            <div key={index} className="bot-msg-section">
              <h4>{block.title}</h4>
              <ul>
                {block.items.map((item, i) => (
                  <li key={i}><strong>{item.scheme}</strong>: {item.description}</li>
                ))}
              </ul>
            </div>
          );
        case 'paragraph':
          return <p key={index}>{block.content}</p>;
        default:
          return null;
      }
    });
  };

  return (
    <div className="app-container">
      <div className="chat-header">
        <div className="bot-info">
          <div className="bot-avatar">
            <Bot size={24} />
          </div>
          <div className="bot-status">
            <p className="bot-name">AI Chatbot</p>
            <span className="status-indicator online"></span>
            <span className="status-text">Online</span>
          </div>
        </div>
        <div className="header-icons">
          <Settings size={20} />
        </div>
      </div>

      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message-wrapper ${msg.sender}`}>
            <div className={`chat-message`}>
              <div className="message-content">
                {msg.sender === 'bot' ? renderBotMessage(msg.text) : msg.text}
              </div>
              <div className="message-timestamp">{msg.timestamp}</div>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="chat-message-wrapper bot">
            <div className="chat-message typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
        />
        <button 
          onClick={() => sendMessage()} 
          className="send-btn"
          disabled={!input.trim()}
        >
          <Send size={20} />
        </button>
        <button onClick={listening ? stopListening : startListening} className={`mic-btn ${listening ? 'active' : ''}`}>
          <Mic size={20} />
        </button>
      </div>
    </div>
  );
}

export default App;