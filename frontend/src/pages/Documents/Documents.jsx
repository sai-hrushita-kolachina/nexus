import "./Documents.css";

import {
  FileText,
  Plus,
  RefreshCw,
  Search,
  Trash2,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import Sidebar from "../../components/Sidebar/Sidebar";
import DocumentCard from "../../components/DocumentCard/DocumentCard";
import UploadModal from "../../components/UploadModal/UploadModal";

import {
  deleteDocument,
  getDocuments,
} from "../../services/api";

export default function Documents() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [search, setSearch] = useState("");

  async function loadDocuments() {
    try {
      setLoading(true);

      const data = await getDocuments();

      setDocuments(data.documents || data || []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleDelete(filename) {
    const confirmed = window.confirm(
      `Delete "${filename}" from the knowledge base?`
    );

    if (!confirmed) {
      return;
    }

    try {
      await deleteDocument(filename);
      await loadDocuments();
    } catch (error) {
      console.error(error);
      alert("Unable to delete the document.");
    }
  }

  const filteredDocuments = documents.filter((document) =>
    (document.filename || document.name || "")
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div className="app-shell">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed((value) => !value)}
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />

      <main className="dashboard-main">
        <header className="page-header">
          <div>
            <h1>Documents</h1>

            <p>
              Manage the knowledge available to Company AI.
            </p>
          </div>

          <button
            className="primary-button"
            onClick={() => setUploadOpen(true)}
          >
            <Plus size={17} />
            Add document
          </button>
        </header>

        <section className="stats-row">
          <div className="stat-card">
            <div className="stat-icon">
              <FileText size={19} />
            </div>

            <div>
              <span>Documents</span>
              <strong>{documents.length}</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <RefreshCw size={19} />
            </div>

            <div>
              <span>Knowledge status</span>
              <strong className="success-text">Active</strong>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">
              <Search size={19} />
            </div>

            <div>
              <span>Retrieval</span>
              <strong>Hybrid</strong>
            </div>
          </div>
        </section>

        <section className="content-card">
          <div className="content-card-header">
            <div>
              <h2>Knowledge base</h2>

              <p>
                Uploaded documents are automatically chunked, embedded and
                indexed.
              </p>
            </div>

            <div className="search-box">
              <Search size={16} />

              <input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Filter documents..."
              />
            </div>
          </div>

          <div className="documents-list">
            {loading ? (
              <div className="page-loading">
                <span className="spinner" />
                Loading documents...
              </div>
            ) : filteredDocuments.length === 0 ? (
              <div className="documents-empty">
                <FileText size={34} />

                <h3>No documents found</h3>

                <p>
                  Upload company documentation to build your knowledge base.
                </p>

                <button
                  className="primary-button"
                  onClick={() => setUploadOpen(true)}
                >
                  <Plus size={17} />
                  Upload first document
                </button>
              </div>
            ) : (
              filteredDocuments.map((document, index) => (
                <DocumentCard
                  key={document.id || document.filename || index}
                  document={document}
                  onDelete={handleDelete}
                />
              ))
            )}
          </div>
        </section>
      </main>

      <UploadModal
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onUploaded={loadDocuments}
      />
    </div>
  );
}