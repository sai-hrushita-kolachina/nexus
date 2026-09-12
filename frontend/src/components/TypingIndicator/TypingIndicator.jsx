import "./TypingIndicator.css";

export default function TypingIndicator() {
  return (
    <div className="typing-wrapper">
      <div className="message-avatar assistant-avatar">
        ✦
      </div>

      <div className="typing-bubble">
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}