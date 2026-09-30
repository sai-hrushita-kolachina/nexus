import { Menu, Sparkles } from "lucide-react";
import { useRef, useEffect } from "react";

import { useChat } from "../../context/ChatContext";

import Message from "../Message/Message";
import MessageInput from "../MessageInput/MessageInput";
import TypingIndicator from "../TypingIndicator/TypingIndicator";
import EmptyState from "../EmptyState/EmptyState";

import "./ChatWindow.css";


export default function ChatWindow({ onMenuClick }) {

  const {
    messages,
    loading,
    sendUserMessage,
  } = useChat();

  const bottomRef = useRef(null);

  useEffect(() => {

    if (messages.length === 0) {

      const container = document.querySelector(".messages-container");

      if (container) {
        container.scrollTop = 0;
      }

      return;
    }

    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages, loading]);

  return (
    <main className="chat-main">

      <header className="chat-header">

        <button
          className="mobile-menu-button"
          onClick={onMenuClick}
        >
          <Menu size={20} />
        </button>

        <div className="chat-title">

          <div className="chat-title-icon">
            <Sparkles size={17} />
          </div>

          <div>
            <strong>Nexus</strong>
            <span>Your AI assistant</span>
          </div>

        </div>

        <div className="connection-status">
          <span className="status-dot" />
          Online
        </div>

      </header>

      <div className="messages-container">

        {messages.length === 0 ? (

          <EmptyState onSuggestion={sendUserMessage} />

        ) : (

          <div className="messages-list">

            {messages.map((message) => (
              <Message
                message={message}
                key={message.id}
              />
            ))}

            {loading && <TypingIndicator />}

            <div ref={bottomRef} />

          </div>

        )}

      </div>

      <MessageInput
        onSend={sendUserMessage}
        loading={loading}
      />

    </main>
  );
}