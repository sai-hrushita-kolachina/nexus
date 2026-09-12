import "./AdminDashboard.css";

import {
  ArrowRight,
  Database,
  FileText,
  MessageSquare,
  Plus,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

import {
  useEffect,
  useState,
} from "react";

import { useNavigate } from "react-router-dom";

import Sidebar from "../../components/Sidebar/Sidebar";
import UploadModal from "../../components/UploadModal/UploadModal";

import { getDocuments } from "../../services/api";

import { useChat } from "../../context/ChatContext";

export default function AdminDashboard() {
  const navigate = useNavigate();

  const { conversations } = useChat();

  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [documents, setDocuments] = useState([]);

  async function loadDocuments() {
    try {
      const data = await getDocuments();

      setDocuments(data.documents || data || []);
    } catch (error) {
      console.error(error);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

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
            <div className="eyebrow">
              <ShieldCheck size={18} />
              ADMIN
            </div>

            <h1>Nexus workspace</h1>

            <p>
              Manage the information your organization's AI assistant knows.
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

        <section className="hero-admin-card">
          <div className="hero-admin-content">
            <div className="hero-admin-icon">
              <Sparkles size={22} />
            </div>

            <div>
              <span className="hero-label">Nexus</span>

              <h2>Your knowledge base is powering the assistant.</h2>

              <p>
                Documents uploaded here are transformed into searchable
                knowledge using semantic embeddings, keyword retrieval and
                reranking.
              </p>
            </div>
          </div>

          <button
            className="hero-action"
            onClick={() => navigate("/documents")}
          >
            Manage knowledge
            <ArrowRight size={17} />
          </button>
        </section>

        <section className="stats-row dashboard-stats">
          <div className="stat-card large-stat">
            <div className="stat-icon">
              <FileText size={20} />
            </div>

            <div>
              <span>Knowledge documents</span>

              <strong>{documents.length}</strong>

              <small>Indexed and searchable</small>
            </div>
          </div>

          <div className="stat-card large-stat">
            <div className="stat-icon">
              <MessageSquare size={20} />
            </div>

            <div>
              <span>Conversations</span>

              <strong>{conversations.length}</strong>

              <small>AI conversations</small>
            </div>
          </div>

          <div className="stat-card large-stat">
            <div className="stat-icon">
              <Database size={20} />
            </div>

            <div>
              <span>Retrieval engine</span>

              <strong>Hybrid RAG</strong>

              <small>Semantic + keyword + rerank</small>
            </div>
          </div>
        </section>

        <section className="admin-grid">
          <div className="content-card">
            <div className="content-card-header">
              <div>
                <h2>Quick actions</h2>

                <p>Common knowledge management tasks.</p>
              </div>
            </div>

            <div className="quick-actions">
              <button
                className="quick-action"
                onClick={() => setUploadOpen(true)}
              >
                <div className="quick-action-icon">
                  <Plus size={19} />
                </div>

                <div>
                  <strong>Upload document</strong>

                  <span>Add new company knowledge</span>
                </div>

                <ArrowRight size={16} />
              </button>

              <button
                className="quick-action"
                onClick={() => navigate("/documents")}
              >
                <div className="quick-action-icon">
                  <FileText size={19} />
                </div>

                <div>
                  <strong>Manage documents</strong>

                  <span>View and remove indexed files</span>
                </div>

                <ArrowRight size={16} />
              </button>
            </div>
          </div>

          <div className="content-card">
            <div className="content-card-header">
              <div>
                <h2>Architecture</h2>

                <p>Current AI pipeline.</p>
              </div>
            </div>

            <div className="architecture-list">
              <ArchitectureItem
                number="01"
                title="Query Router"
                text="Company / General / Mixed"
              />

              <ArchitectureItem
                number="02"
                title="Hybrid Retrieval"
                text="Vector + BM25 search"
              />

              <ArchitectureItem
                number="03"
                title="LLM Orchestration"
                text="Gemini + Groq fallback"
              />
            </div>
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

function ArchitectureItem({ number, title, text }) {
  return (
    <div className="architecture-item">
      <span className="architecture-number">{number}</span>

      <div>
        <strong>{title}</strong>

        <span>{text}</span>
      </div>
    </div>
  );
}