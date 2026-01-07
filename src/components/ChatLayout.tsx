import React from "react";
import { Message } from "../types";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import VerifyButton from "./VerifyButton";

interface Props {
  title?: string;
  messages: Message[];
  onSend: (text: string) => void;
}

export default function ChatLayout({
  title = "Chat",
  messages,
  onSend,
}: Props) {
  return (
    <div className="app-root">
      <header className="chat-header">
        <div className="chat-header-left">
          <h1>{title}</h1>
        </div>
        <div className="chat-header-right">
          <VerifyButton />
        </div>
      </header>

      <main className="chat-main">
        <MessageList messages={messages} />
      </main>

      <footer className="chat-footer">
        <MessageInput onSend={onSend} />
      </footer>
    </div>
  );
}
