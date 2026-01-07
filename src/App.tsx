import React, { useState } from "react";
import ChatLayout from "./components/ChatLayout";
import { Message } from "./types";

const now = () => new Date().toLocaleTimeString();

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    { id: "1", author: "Alice", text: "Hi there!", timestamp: now() },
    {
      id: "2",
      author: "You",
      text: "Hello! I'm trying the chat layout.",
      timestamp: now(),
      self: true,
    },
  ]);

  const handleSend = (text: string) => {
    const m: Message = {
      id: Date.now().toString() + Math.random().toString(36).slice(2),
      author: "You",
      text,
      timestamp: now(),
      self: true,
    };
    setMessages((s) => [...s, m]);
  };

  return (
    <ChatLayout title="Basic Chat" messages={messages} onSend={handleSend} />
  );
}
