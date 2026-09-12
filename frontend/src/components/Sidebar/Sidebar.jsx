import "./Sidebar.css";

import {
  ChevronLeft,
  ChevronRight,
  FileText,
  LogOut,
  MessageSquare,
  Plus,
  Settings,
  Shield,
  Trash2,
  Sparkles,
} from "lucide-react";

import {
  useNavigate,
  useLocation,
} from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { useChat } from "../../context/ChatContext";

import { formatDate } from "../../utils/helpers";


export default function Sidebar({
  collapsed,
  onToggle,
  mobileOpen,
  onMobileClose,
}) {

  const navigate = useNavigate();
  const location = useLocation();

  const { user, logout } = useAuth();

  const {
    conversations,
    conversationId,
    newConversation,
    openConversation,
    removeConversation,
  } = useChat();

  const isAdmin = user?.role === "admin";

  function navigateTo(path) {

    navigate(path);

    if (onMobileClose) {
      onMobileClose();
    }
  }

  function handleNewChat() {

    newConversation();

    navigate("/chat");

    if (onMobileClose) {
      onMobileClose();
    }
  }

  function handleLogout() {

    logout();
    navigate("/login");
  }

  return (
    <>
      {mobileOpen && (
        <div
          className="mobile-overlay"
          onClick={onMobileClose}
        />
      )}

      <aside
        className={`sidebar ${
          collapsed ? "sidebar-collapsed" : ""
        } ${
          mobileOpen ? "sidebar-mobile-open" : ""
        }`}
      >

        {/* SIDEBAR HEADER */}

        <div className="sidebar-header">

          <div
            className="brand"
            onClick={() =>
              navigateTo(isAdmin ? "/admin" : "/chat")
            }
          >

            <div className="brand-icon">
              <Sparkles size={24} />
            </div>

            {!collapsed && (
              <div className="brand-text">
                <strong>Nexus</strong>
              </div>
            )}

          </div>

          <button
            className="icon-button sidebar-toggle"
            onClick={onToggle}
            title={
              collapsed
                ? "Expand sidebar"
                : "Collapse sidebar"
            }
          >
            {collapsed ? (
              <ChevronRight size={18} />
            ) : (
              <ChevronLeft size={18} />
            )}
          </button>

        </div>

        {/* SIDEBAR CONTENT */}

        <div className="sidebar-content">

          {/* EMPLOYEE CHAT SECTION */}

          {!isAdmin && (
            <>

              {/* New Conversation */}

              <button
                className="new-chat-button"
                onClick={handleNewChat}
              >
                <Plus size={18} />

                {!collapsed && (
                  <span>
                    New conversation
                  </span>
                )}
              </button>

              {/* Workspace */}

              <div className="sidebar-section">

                {!collapsed && (
                  <div className="sidebar-section-title">
                    Workspace
                  </div>
                )}

                <button
                  className={`sidebar-nav-item ${
                    location.pathname === "/chat"
                      ? "active"
                      : ""
                  }`}
                  onClick={() => navigateTo("/chat")}
                  title="AI Chat"
                >
                  <MessageSquare size={18} />

                  {!collapsed && (
                    <span>
                      AI Chat
                    </span>
                  )}
                </button>

              </div>

              {/* Recent Conversations */}

              {!collapsed && (
                <div className="conversation-section">

                  <div className="sidebar-section-title">
                    Recent conversations
                  </div>

                  <div className="conversation-list">

                    {conversations.length === 0 ? (

                      <div className="empty-conversations">

                        <MessageSquare size={18} />

                        <span>
                          No conversations yet
                        </span>

                      </div>

                    ) : (

                      conversations
                        .slice(0, 12)
                        .map((conversation) => (

                          <div
                            className={`conversation-item ${
                              conversation.id === conversationId
                                ? "active"
                                : ""
                            }`}
                            key={conversation.id}
                          >

                            <button
                              className="conversation-main"
                              onClick={() => {

                                openConversation(
                                  conversation.id
                                );

                                navigate("/chat");

                                if (onMobileClose) {
                                  onMobileClose();
                                }
                              }}
                            >

                              <MessageSquare size={15} />

                              <div>

                                <span>
                                  {conversation.title ||
                                    "New conversation"}
                                </span>

                                <small>
                                  {formatDate(
                                    conversation.updated_at
                                  )}
                                </small>

                              </div>

                            </button>

                            <button
                              className="conversation-delete"
                              onClick={() =>
                                removeConversation(
                                  conversation.id
                                )
                              }
                              title="Delete conversation"
                            >
                              <Trash2 size={14} />
                            </button>

                          </div>

                        ))
                    )}

                  </div>

                </div>
              )}

            </>
          )}

          {/* ADMIN SECTION */}

          {isAdmin && (
            <div className="sidebar-section">

              {!collapsed && (
                <div className="sidebar-section-title">
                  Administration
                </div>
              )}

              {/* Admin Dashboard */}

              <button
                className={`sidebar-nav-item ${
                  location.pathname === "/admin"
                    ? "active"
                    : ""
                }`}
                onClick={() => navigateTo("/admin")}
                title="Admin Dashboard"
              >
                <Shield size={18} />

                {!collapsed && (
                  <span>
                    Admin Dashboard
                  </span>
                )}
              </button>

              {/* Documents */}

              <button
                className={`sidebar-nav-item ${
                  location.pathname === "/documents"
                    ? "active"
                    : ""
                }`}
                onClick={() => navigateTo("/documents")}
                title="Documents"
              >
                <FileText size={18} />

                {!collapsed && (
                  <span>
                    Documents
                  </span>
                )}
              </button>

            </div>
          )}

        </div>

        {/* SIDEBAR FOOTER */}

        <div className="sidebar-footer">

          <div className="user-mini">

            <div className="avatar">
              {user?.name?.charAt(0)?.toUpperCase() || "U"}
            </div>

            {!collapsed && (
              <div className="user-mini-info">

                <strong>
                  {user?.name || "Employee"}
                </strong>

                <span>
                  {isAdmin ? "Admin" : "Employee"}
                </span>

              </div>
            )}

          </div>

          <div className="sidebar-footer-actions">

            <button
              className="icon-button"
              title="Settings"
            >
              <Settings size={17} />
            </button>

            <button
              className="icon-button"
              title="Logout"
              onClick={handleLogout}
            >
              <LogOut size={17} />
            </button>

          </div>

        </div>

      </aside>
    </>
  );
}