import "./UploadModal.css";
import {
  FileUp,
  Upload,
  X,
} from "lucide-react";

import {
  useRef,
  useState,
} from "react";

import { uploadDocument } from "../../services/api";

export default function UploadModal({
  open,
  onClose,
  onUploaded,
}) {

  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [department, setDepartment] = useState("");
  const [docType, setDocType] = useState("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  if (!open) {
    return null;
  }

  function handleFileChange(event) {
    const selected = event.target.files?.[0];

    setFile(selected || null);
    setError("");
  }

  async function handleUpload() {
    if (!file) {
      setError("Please select a document.");
      return;
    }

    try {

      setUploading(true);
      setError("");

      await uploadDocument(
        file,
        department,
        docType
      );

      setFile(null);
      setDepartment("");
      setDocType("");

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

      onUploaded?.();

      onClose();

    } catch (err) {

      console.error(err);

      setError(
        err?.response?.data?.detail ||
          "Unable to upload document."
      );

    } finally {

      setUploading(false);
    }
  }

  return (
    <div className="modal-overlay">

      <div className="upload-modal">

        <div className="modal-header">

          <div>

            <div className="modal-icon">
              <FileUp size={20} />
            </div>

            <h2>
              Add company document
            </h2>

            <p>
              Upload a PDF, DOCX, TXT, or
              Markdown file to the knowledge
              base.
            </p>

          </div>

          <button
            className="icon-button"
            onClick={onClose}
          >
            <X size={19} />
          </button>

        </div>

        <div
          className={`drop-zone ${
            file ? "has-file" : ""
          }`}
          onClick={() =>
            fileInputRef.current?.click()
          }
        >

          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md"
            hidden
            onChange={handleFileChange}
          />

          <Upload size={27} />

          {file ? (
            <>
              <strong>
                {file.name}
              </strong>

              <span>
                Click to choose another file
              </span>
            </>
          ) : (
            <>
              <strong>
                Click to choose a file
              </strong>

              <span>
                PDF, DOCX, TXT or MD
              </span>
            </>
          )}

        </div>

        <div className="form-grid">

          <label>

            Department

            <input
              value={department}
              onChange={(event) =>
                setDepartment(event.target.value)
              }
              placeholder="e.g. HR, IT, Finance"
            />

          </label>

          <label>

            Document type

            <input
              value={docType}
              onChange={(event) =>
                setDocType(event.target.value)
              }
              placeholder="e.g. Policy, Handbook"
            />

          </label>

        </div>

        {error && (
          <div className="form-error">
            {error}
          </div>
        )}

        <div className="modal-actions">

          <button
            className="secondary-button"
            onClick={onClose}
            disabled={uploading}
          >
            Cancel
          </button>

          <button
            className="primary-button"
            onClick={handleUpload}
            disabled={uploading}
          >

            {uploading ? (
              <>
                <span className="spinner" />
                Indexing...
              </>
            ) : (
              <>
                <Upload size={16} />
                Upload & Index
              </>
            )}

          </button>

        </div>

      </div>

    </div>
  );
}