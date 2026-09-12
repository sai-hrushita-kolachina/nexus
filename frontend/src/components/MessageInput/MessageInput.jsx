import {
  ArrowUp,
  Paperclip,
} from "lucide-react";

import {
  useRef,
  useState,
} from "react";

import "./MessageInput.css";


export default function MessageInput({ onSend, loading }) {

  const [value, setValue] = useState("");

  const textareaRef = useRef(null);

  function resizeTextarea() {

    const textarea = textareaRef.current;

    if (!textarea) return;

    textarea.style.height = "auto";

    const lineHeight = 21;
    const maxHeight = lineHeight * 5;

    const newHeight = Math.min(
      textarea.scrollHeight,
      maxHeight
    );

    textarea.style.height = `${newHeight}px`;

    if (textarea.scrollHeight > maxHeight) {
      textarea.style.overflowY = "auto";
    } else {
      textarea.style.overflowY = "hidden";
    }
  }

  function handleChange(event) {

    setValue(event.target.value);

    requestAnimationFrame(() => {
      resizeTextarea();
    });
  }

  function resetTextarea() {

    const textarea = textareaRef.current;

    if (!textarea) return;

    textarea.style.height = "21px";
    textarea.style.overflowY = "hidden";
  }

  function submit() {

    if (!value.trim() || loading) {
      return;
    }

    onSend(value);

    setValue("");

    requestAnimationFrame(() => {
      resetTextarea();
    });
  }

  function handleKeyDown(event) {

    if (event.key === "Enter" && !event.shiftKey) {

      event.preventDefault();

      submit();
    }
  }

  return (
    <div className="input-area">

      <div className="input-shell">

        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Ask Nexus anything..."
          rows={1}
          disabled={loading}
        />

        <div className="input-bottom">

          <button
            className="input-tool"
            title="Attachments"
            disabled
          >
            <Paperclip size={17} />
          </button>

          <button
            className="send-button"
            onClick={submit}
            disabled={!value.trim() || loading}
          >
            <ArrowUp size={18} />
          </button>

        </div>

      </div>

      <div className="input-disclaimer">
        Nexus can make mistakes. Check
        important info.
      </div>

    </div>
  );
}