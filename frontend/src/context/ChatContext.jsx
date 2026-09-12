import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  getConversation,
  getConversations,
  deleteConversation,
  sendMessage,
} from "../services/api";

const ChatContext = createContext(null);

export function ChatProvider({ children }) {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [error, setError] = useState(null);

  async function loadConversations() {
    try {
      const data = await getConversations();
      setConversations(data.conversations || []);
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadConversations();
  }, []);

  // Start a new conversation.

  function newConversation() {
    setConversationId(null);
    setMessages([]);
    setError(null);
  }

  // Open an existing conversation.

  async function openConversation(id) {
    try {
      setLoadingHistory(true);
      setError(null);

      const data = await getConversation(id);

      setConversationId(id);

      setMessages(
        (data.messages || []).map((message) => ({
          id: `${message.id}-${message.role}`,
          role: message.role,
          content: message.content,
          queryType: message.query_type,
          provider: message.provider,
        }))
      );
    } catch (err) {
      console.error(err);
      setError("Unable to load this conversation.");
    } finally {
      setLoadingHistory(false);
    }
  }

  // Delete an existing conversation.

  async function removeConversation(id) {
    try {
      await deleteConversation(id);

      if (id === conversationId) {
        newConversation();
      }

      await loadConversations();
    } catch (err) {
      console.error(err);
      setError("Unable to delete this conversation.");
    }
  }

  // Send a user message and receive the assistant response.

  async function sendUserMessage(text) {
    if (!text.trim() || loading) {
      return;
    }

    setError(null);

    const userMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text.trim(),
    };

    setMessages((previous) => [...previous, userMessage]);

    setLoading(true);

    try {
      const data = await sendMessage(text.trim(), conversationId);

      setConversationId(data.conversation_id);

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.answer,
        queryType: data.query_type,
        provider: data.provider,
        sources: data.sources || [],
        retrievalRelevance: data.retrieval_relevance,
      };

      setMessages((previous) => [...previous, assistantMessage]);

      await loadConversations();

      return data;
    } catch (err) {
      console.error(err);

      const message = err?.response?.data?.detail || "Something went wrong while contacting Nexus.";

      setError(message);

      setMessages((previous) => [
        ...previous,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: "I couldn't process that request right now. Please check that the backend is running and try again.",
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <ChatContext.Provider
      value={{
        conversationId,
        messages,
        conversations,
        loading,
        loadingHistory,
        error,
        newConversation,
        openConversation,
        removeConversation,
        sendUserMessage,
        loadConversations,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  return useContext(ChatContext);
}