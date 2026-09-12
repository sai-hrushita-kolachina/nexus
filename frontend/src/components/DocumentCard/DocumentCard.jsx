import "./DocumentCard.css";

import {
  FileText,
  Trash2,
} from "lucide-react";

import {
  getFileIcon,
  formatFileSize,
} from "../../utils/helpers";


export default function DocumentCard({
  document,
  onDelete,
}) {

  const filename = document.filename || document.name || "Document";

  return (
    <div className="document-card">

      <div className="document-file-icon">
        <FileText size={22} />
      </div>

      <div className="document-info">

        <strong>{filename}</strong>

        <div className="document-meta">

          <span>
            {getFileIcon(filename)}
          </span>

          {document.size && (
            <>
              <span>•</span>

              <span>
                {formatFileSize(document.size)}
              </span>
            </>
          )}

          {document.chunks !== undefined && (
            <>
              <span>•</span>

              <span>
                {document.chunks} chunks
              </span>
            </>
          )}

        </div>

      </div>

      <div className="document-status">
        <span className="status-dot" />
        Indexed
      </div>

      <button
        className="danger-icon-button"
        onClick={() => onDelete(filename)}
        title="Delete document"
      >
        <Trash2 size={17} />
      </button>

    </div>
  );
}