import "./EmptyState.css";

import {
  ArrowRight,
  Building2,
  FileSearch,
  Sparkles,
} from "lucide-react";


export default function EmptyState({ onSuggestion }) {

  const suggestions = [
    {
      icon: Building2,
      title: "Company policies",
      text: "What is the annual leave policy?",
    },
    {
      icon: FileSearch,
      title: "Find information",
      text: "What does our WFH policy say?",
    },
    {
      icon: Sparkles,
      title: "Ask anything",
      text: "Explain RAG in simple terms.",
    },
  ];

  return (
    <div className="empty-state">

      <div className="empty-logo">
        <Sparkles size={28} />
      </div>

      <h1>
        Hi, I am Nexus. How can I help you today?
      </h1>

      <p>
        Ask about company policies,
        internal documents, or anything
        else you need help with.
      </p>

      <div className="suggestion-grid">

        {suggestions.map(({ icon: Icon, title, text }) => (
          <button
            className="suggestion-card"
            key={title}
            onClick={() => onSuggestion(text)}
          >

            <div className="suggestion-icon">
              <Icon size={18} />
            </div>

            <div>
              <strong>{title}</strong>
              <span>{text}</span>
            </div>

            <ArrowRight size={16} />

          </button>
        ))}

      </div>

    </div>
  );
}