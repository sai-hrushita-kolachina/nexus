import "./SourcePanel.css";

import {
  BookOpen,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

import { useState } from "react";
import SourceCard from "../SourceCard/SourceCard";

export default function SourcePanel({
  sources = [],
}) {
  const [open, setOpen] =
    useState(false);

  if (!sources.length) {
    return null;
  }

  return (
    <div className="source-panel">
      <button
        className="source-panel-header"
        onClick={() =>
          setOpen((value) => !value)
        }
      >
        <div className="source-panel-title">
          <BookOpen size={16} />

          <span>
            {sources.length} company source
            {sources.length !== 1
              ? "s"
              : ""}
          </span>
        </div>

        {open ? (
          <ChevronUp size={16} />
        ) : (
          <ChevronDown size={16} />
        )}
      </button>

      {open && (
        <div className="source-panel-content">
          {sources.map(
            (source, index) => (
              <SourceCard
                source={source}
                key={`${source.filename}-${source.page}-${index}`}
              />
            )
          )}
        </div>
      )}
    </div>
  );
}