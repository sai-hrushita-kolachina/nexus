import "./SourceCard.css";

import {
  ExternalLink,
  FileText,
} from "lucide-react";


export default function SourceCard({ source }) {

  const relevance = Number(source?.relevance || 0);

  return (
    <div className="source-card">

      <div className="source-icon">
        <FileText size={17} />
      </div>

      <div className="source-content">

        <strong>
          {source?.filename || "Company document"}
        </strong>

        <div className="source-meta">

          {source?.page ? (
            <span>
              Page {source.page}
            </span>
          ) : (
            <span>
              Document
            </span>
          )}

          <span className="source-dot">
            •
          </span>

          <span>
            {Math.round(relevance * 100)}% match
          </span>

        </div>

      </div>

      <ExternalLink size={15} />

    </div>
  );
}