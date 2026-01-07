import React, { useEffect, useRef } from "react";
import { Message } from "../types";

interface Props {
  messages: Message[];
}

export default function MessageList({ messages }: Props) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight;
  }, [messages]);

  return (
    <div className="message-list" ref={ref}>
      {messages.map((m) => (
        <div key={m.id} className={`message ${m.self ? "self" : "other"}`}>
          <div className="meta">
            <div className="author">{m.author}</div>
            <div className="time">{m.timestamp}</div>
          </div>
          <div className="bubble">{m.text}</div>
        </div>
      ))}
    </div>
  );
}
