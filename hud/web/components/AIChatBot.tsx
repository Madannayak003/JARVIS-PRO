"use client";

import "../app/ai-chat.css";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

import {
  KeyboardEvent,
  useEffect,
  useRef,
  useState,
} from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
};

type ChatSession = {
  id: string;
  title: string;
  created_at?: string;
  updated_at?: string;
  provider?: string;
  model?: string;
  messages?: ChatMessage[];
};

const DASHBOARD_URL =
  process.env.NEXT_PUBLIC_JARVIS_DASHBOARD_URL ||
  (typeof window !== "undefined"
    ? `http://${window.location.hostname}:8765`
    : "http://127.0.0.1:8765");

console.log("[AI CHAT] DASHBOARD_URL:", DASHBOARD_URL);

const DEFAULT_MODEL = "gemini-3.6-flash";

const CHAT_MODELS = [
  {
    id: "gemini-3.8-flash",
    name: "Gemini 3.8 Flash",
    description: "Best overall",
  },
  {
    id: "gemini-3.7-flash",
    name: "Gemini 3.7 Flash",
    description: "Coding & agents",
  },
  {
    id: "gemini-3.6-flash",
    name: "Gemini 3.6 Flash",
    description: "Balanced",
  },
  {
    id: "gemini-3.5-flash",
    name: "Gemini 3.5 Flash",
    description: "General purpose",
  },
  {
    id: "gemini-3.5-flash-lite",
    name: "Gemini 3.5 Flash-Lite",
    description: "Fast & lightweight",
  },
  {
    id: "gemini-3.1-flash-lite",
    name: "Gemini 3.1 Flash-Lite",
    description: "Low latency",
  },
] as const;;

export default function AIChatBot({
  open,
  onClose,
}: {
  open: boolean;
  onClose?: () => void;
}) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] =
    useState<ChatSession | null>(null);

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);

  const [selectedModel, setSelectedModel] =
    useState(DEFAULT_MODEL);

  const [modelUpdating, setModelUpdating] =
    useState(false);

  const [quotaError, setQuotaError] =
    useState<string | null>(null);

  const [openMenuId, setOpenMenuId] =
    useState<string | null>(null);

  const [renameChatId, setRenameChatId] =
    useState<string | null>(null);

  const [renameTitle, setRenameTitle] =
    useState("");

  const [deleteChatId, setDeleteChatId] =
    useState<string | null>(null);

  const [chatActionLoading, setChatActionLoading] =
    useState(false);

  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const messagesRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  /* =========================================================
     LOAD CHAT HISTORY
     ========================================================= */

  const loadChats = async () => {
    try {
      setLoadingHistory(true);

      const response = await fetch(
        `${DASHBOARD_URL}/api/ai-chat/chats`,
        {
          cache: "no-store",
        }
      );

      const data = await response.json();

      if (data?.success) {
        const chats = data.chats || [];
        setSessions(chats);

        if (chats.length > 0 && !currentSession) {
          await loadChat(chats[0].id);
        }
      }
    } catch (error) {
      console.error("[AI CHAT] Failed to load chats:", error);
    } finally {
      setLoadingHistory(false);
    }
  };

  /* =========================================================
     LOAD SINGLE CHAT
     ========================================================= */

  const loadChat = async (sessionId: string) => {
    try {
      const response = await fetch(
        `${DASHBOARD_URL}/api/ai-chat/${sessionId}`,
        {
          cache: "no-store",
        }
      );

      const data = await response.json();

      if (data?.success && data.chat) {
        setCurrentSession(data.chat);
      }
    } catch (error) {
      console.error("[AI CHAT] Failed to load chat:", error);
    }
  };

  /* =========================================================
     INITIAL LOAD
     ========================================================= */

  useEffect(() => {
    void loadChats();
  }, []);

  /* =========================================================
     AUTO SCROLL
     ========================================================= */

  useEffect(() => {
    const container = messagesRef.current;

    if (!container) {
      return;
    }

    container.scrollTop = container.scrollHeight;
  }, [currentSession?.messages, loading]);

  /* =========================================================
     NEW CHAT
     ========================================================= */

  const createNewChat = async () => {
    try {
      const response = await fetch(
        `${DASHBOARD_URL}/api/ai-chat/new`,
        {
          method: "POST",
          cache: "no-store",
        }
      );

      const data = await response.json();

      if (!data?.success || !data.chat) {
        throw new Error(
          data?.error || "Unable to create new chat."
        );
      }

      setCurrentSession(data.chat);

      setSessions((previous) => [
        data.chat,
        ...previous.filter(
          (chat) => chat.id !== data.chat.id
        ),
      ]);

      setMessage("");

      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    } catch (error) {
      console.error("[AI CHAT] New chat failed:", error);
    }
  };

  /* =========================================================
     SEND MESSAGE
     ========================================================= */

  const sendMessage = async () => {
    const text = message.trim();

    if (!text || loading) {
      return;
    }

    let session = currentSession;

    if (!session) {
      try {
        const response = await fetch(
          `${DASHBOARD_URL}/api/ai-chat/new`,
          {
            method: "POST",
            cache: "no-store",
          }
        );

        const data = await response.json();

        if (!data?.success || !data.chat) {
          throw new Error(
            data?.error || "Unable to create chat."
          );
        }

        session = data.chat;

        setCurrentSession(session);

        setSessions((previous) => [
          session!,
          ...previous,
        ]);
      } catch (error) {
        console.error(
          "[AI CHAT] Automatic chat creation failed:",
          error
        );
        return;
      }
    }

    setMessage("");
    setLoading(true);

    const optimisticUserMessage: ChatMessage = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    setCurrentSession((previous) =>
      previous
        ? {
            ...previous,
            messages: [
              ...(previous.messages || []),
              optimisticUserMessage,
            ],
          }
        : previous
    );

    try {
      const response = await fetch(
        `${DASHBOARD_URL}/api/ai-chat/message`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          cache: "no-store",
          body: JSON.stringify({
            session_id: session!.id,
            message: text,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data?.success) {
        const errorText =
          data?.error ||
          data?.raw_error ||
          `Request failed with status ${response.status}.`;

        const rawError = String(
          data?.raw_error || data?.error || errorText
        );

        if (
          response.status === 503 ||
          rawError.includes("503") ||
          rawError.includes("UNAVAILABLE") ||
          rawError.toLowerCase().includes("high demand")
        ) {
          setQuotaError(
            `The selected model "${selectedModel}" is temporarily unavailable because it is experiencing high demand. Please try again later or select another model.`
          );

          return;
        }

        if (
          response.status === 429 ||
          data?.error_code === "MODEL_QUOTA_EXCEEDED" ||
          rawError.includes("429") ||
          rawError.includes("RESOURCE_EXHAUSTED") ||
          rawError.toLowerCase().includes("quota")
        ) {
          setQuotaError(
            `The selected model "${selectedModel}" has reached its current Gemini quota or rate limit. Please select another model or try again later.`
          );

          return;
        }

        throw new Error(errorText);
      }

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: data.response || "",
        timestamp: new Date().toISOString(),
      };

      setCurrentSession((previous) =>
        previous
          ? {
              ...previous,
              messages: [
                ...(previous.messages || []),
                assistantMessage,
              ],
              title:
                previous.title === "New Chat"
                  ? text.slice(0, 60)
                  : previous.title,
              updated_at:
                new Date().toISOString(),
            }
          : previous
      );

      await loadChats();
    } catch (error) {
      console.error("[AI CHAT] Send failed:", error);

      const errorMessage: ChatMessage = {
        role: "assistant",
        content:
          error instanceof Error
            ? `Unable to respond: ${error.message}`
            : "Unable to respond.",
        timestamp: new Date().toISOString(),
      };

      setCurrentSession((previous) =>
        previous
          ? {
              ...previous,
              messages: [
                ...(previous.messages || []),
                errorMessage,
              ],
            }
          : previous
      );
    } finally {
      setLoading(false);

      requestAnimationFrame(() => {
        inputRef.current?.focus();
      });
    }
  };

  /* =========================================================
    MODEL SELECTION
    ========================================================= */

  const changeModel = async (model: string) => {
    if (!currentSession || modelUpdating) {
      return;
    }

    try {
      setModelUpdating(true);
      setQuotaError(null);

      const response = await fetch(
        `${DASHBOARD_URL}/api/ai-chat/${currentSession.id}/model`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          cache: "no-store",
          body: JSON.stringify({
            model,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data?.success) {
        throw new Error(
          data?.error ||
            "Unable to change AI model."
        );
      }

      setSelectedModel(model);

      setCurrentSession((previous) =>
        previous
          ? {
              ...previous,
              model,
            }
          : previous
      );

      setSessions((previous) =>
        previous.map((chat) =>
          chat.id === currentSession.id
            ? {
                ...chat,
                model,
              }
            : chat
        )
      );
    } catch (error) {
      console.error(
        "[AI CHAT] Model change failed:",
        error
      );
    } finally {
      setModelUpdating(false);
    }
  };


  /* =========================================================
     CODE COPY
     ========================================================= */

  const copyCode = async (code: string) => {
    if (!code) {
      return;
    }

    try {
      /*
       * First use the JARVIS backend.
       *
       * This works in the native JARVIS window because Python
       * writes directly to the Windows system clipboard.
       */
      try {
        const response = await fetch(
          `${DASHBOARD_URL}/api/ai-chat/clipboard`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            cache: "no-store",
            body: JSON.stringify({
              text: code,
            }),
          }
        );

        const data = await response.json();

        if (response.ok && data?.success) {
          setCopiedCode(code);

          window.setTimeout(() => {
            setCopiedCode((current) =>
              current === code ? null : current
            );
          }, 1500);

          return;
        }
      } catch (error) {
        console.warn(
          "[AI CHAT] Native clipboard unavailable. Using browser clipboard.",
          error
        );
      }

      /*
       * Browser fallback.
       */
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(code);

        setCopiedCode(code);

        window.setTimeout(() => {
          setCopiedCode((current) =>
            current === code ? null : current
          );
        }, 1500);

        return;
      }

      throw new Error(
        "Clipboard is not available."
      );
    } catch (error) {
      console.error(
        "[AI CHAT] Code copy failed:",
        error
      );
    }
  };

  /* =========================================================
    CHAT HISTORY ACTIONS
    ========================================================= */

  const startRenameChat = (chat: ChatSession) => {
    setOpenMenuId(null);
    setRenameChatId(chat.id);
    setRenameTitle(chat.title || "New Chat");
  };

  const cancelRenameChat = () => {
    if (chatActionLoading) {
      return;
    }

    setRenameChatId(null);
    setRenameTitle("");
  };

  const saveRenameChat = async () => {
    const chatId = renameChatId;
    const title = renameTitle.trim();

    if (!chatId || !title || chatActionLoading) {
      return;
    }

    try {
      setChatActionLoading(true);

      const response = await fetch(
        `${DASHBOARD_URL}/api/ai-chat/${chatId}/rename`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          cache: "no-store",
          body: JSON.stringify({
            title,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || !data?.success) {
        throw new Error(
          data?.error ||
            "Unable to rename chat."
        );
      }

      setSessions((previous) =>
        previous.map((chat) =>
          chat.id === chatId
            ? {
                ...chat,
                title: data.title || title,
              }
            : chat
        )
      );

      setCurrentSession((previous) =>
        previous?.id === chatId
          ? {
              ...previous,
              title: data.title || title,
            }
          : previous
      );

      setRenameChatId(null);
      setRenameTitle("");
    } catch (error) {
      console.error(
        "[AI CHAT] Rename failed:",
        error
      );
    } finally {
      setChatActionLoading(false);
    }
  };

  const confirmDeleteChat = (chatId: string) => {
    setOpenMenuId(null);
    setDeleteChatId(chatId);
  };

  const cancelDeleteChat = () => {
    if (chatActionLoading) {
      return;
    }

    setDeleteChatId(null);
  };

  const deleteChat = async () => {
    const chatId = deleteChatId;

    if (!chatId || chatActionLoading) {
      return;
    }

    try {
      setChatActionLoading(true);

      const response = await fetch(
        `${DASHBOARD_URL}/api/ai-chat/${chatId}`,
        {
          method: "DELETE",
          cache: "no-store",
        }
      );

      const data = await response.json();

      if (!response.ok || !data?.success) {
        throw new Error(
          data?.error ||
            "Unable to delete chat."
        );
      }

      const remainingChats =
        sessions.filter(
          (chat) => chat.id !== chatId
        );

      setSessions(remainingChats);
      setDeleteChatId(null);

      /*
      * If the deleted chat was the currently
      * open conversation, move somewhere safe.
      */
      if (currentSession?.id === chatId) {
        if (remainingChats.length > 0) {
          await loadChat(
            remainingChats[0].id
          );
        } else {
          await createNewChat();
        }
      }
    } catch (error) {
      console.error(
        "[AI CHAT] Delete failed:",
        error
      );
    } finally {
      setChatActionLoading(false);
    }
  };

  /* =========================================================
     KEYBOARD
     ========================================================= */

  const handleKeyDown = (
    event: KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendMessage();
    }
  };

  /* =========================================================
     EXAMPLE PROMPTS
     ========================================================= */

  const useExample = (text: string) => {
    setMessage(text);

    requestAnimationFrame(() => {
      inputRef.current?.focus();
    });
  };

  /* =========================================================
     RENDER
     ========================================================= */

    if (!open) {
      return null;
    }

  return (
    <section className="ai-chat-window">
      {/* =====================================================
          SIDEBAR
          ===================================================== */}

      <aside className="ai-chat-sidebar">
        <div className="ai-chat-brand">
          <div className="ai-chat-brand-title">
            <span className="ai-chat-robot">▣</span>
            AI Chat
          </div>

          <div className="ai-chat-brand-subtitle">
            INDEPENDENT GEMINI CHAT
          </div>
        </div>

        <button
          type="button"
          className="ai-chat-new-button"
          onClick={() => void createNewChat()}
        >
          <span>＋</span>
          New Chat
        </button>

        <div className="ai-chat-sidebar-section">
          <div className="ai-chat-section-title">
            CHAT HISTORY
          </div>

          <div className="ai-chat-history">
            {loadingHistory ? (
              <div className="ai-chat-empty">
                Loading history...
              </div>
            ) : sessions.length === 0 ? (
              <div className="ai-chat-empty">
                No conversations yet.
              </div>
            ) : (
              sessions.map((chat) => (
                <div
                  key={chat.id}
                  className={
                    "ai-chat-history-row " +
                    (currentSession?.id === chat.id
                      ? "active"
                      : "")
                  }
                >
                  <button
                    type="button"
                    className="ai-chat-history-item"
                    onClick={() => {
                      setOpenMenuId(null);
                      void loadChat(chat.id);
                    }}
                  >
                    <span className="ai-chat-history-icon">
                      ▸
                    </span>

                    <span className="ai-chat-history-text">
                      {chat.title || "New Chat"}
                    </span>
                  </button>

                  <button
                    type="button"
                    className="ai-chat-history-menu-button"
                    aria-label={`Options for ${
                      chat.title || "New Chat"
                    }`}
                    title="Chat options"
                    onClick={(event) => {
                      event.stopPropagation();

                      setOpenMenuId(
                        openMenuId === chat.id
                          ? null
                          : chat.id
                      );
                    }}
                  >
                    ⋯
                  </button>

                  {openMenuId === chat.id && (
                    <div className="ai-chat-history-menu">
                      <button
                        type="button"
                        onClick={() =>
                          startRenameChat(chat)
                        }
                      >
                        <span>✎</span>
                        Rename
                      </button>

                      <button
                        type="button"
                        className="danger"
                        onClick={() =>
                          confirmDeleteChat(chat.id)
                        }
                      >
                        <span>⌫</span>
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="ai-chat-sidebar-footer">
          <div className="ai-chat-independent">
            <span className="ai-chat-status-dot" />
            Independent AI
          </div>

          <div className="ai-chat-model-small">
            Gemini
          </div>
        </div>
      </aside>

      {/* =====================================================
          RENAME CHAT DIALOG
          ===================================================== */}

      {renameChatId && (
        <div
          className="ai-chat-dialog-backdrop"
          onMouseDown={(event) => {
            if (
              event.target === event.currentTarget
            ) {
              cancelRenameChat();
            }
          }}
        >
          <div
            className="ai-chat-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="rename-chat-title"
          >
            <div className="ai-chat-dialog-title">
              Rename chat
            </div>

            <div className="ai-chat-dialog-text">
              Choose a name for this conversation.
            </div>

            <input
              className="ai-chat-dialog-input"
              value={renameTitle}
              maxLength={60}
              autoFocus
              disabled={chatActionLoading}
              onChange={(event) =>
                setRenameTitle(
                  event.target.value
                )
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  void saveRenameChat();
                }

                if (event.key === "Escape") {
                  cancelRenameChat();
                }
              }}
            />

            <div className="ai-chat-dialog-actions">
              <button
                type="button"
                className="ai-chat-dialog-cancel"
                onClick={cancelRenameChat}
                disabled={chatActionLoading}
              >
                Cancel
              </button>

              <button
                type="button"
                className="ai-chat-dialog-primary"
                onClick={() =>
                  void saveRenameChat()
                }
                disabled={
                  chatActionLoading ||
                  !renameTitle.trim()
                }
              >
                {chatActionLoading
                  ? "Saving..."
                  : "Save"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================
          DELETE CHAT CONFIRMATION
          ===================================================== */}

      {deleteChatId && (
        <div
          className="ai-chat-dialog-backdrop"
          onMouseDown={(event) => {
            if (
              event.target === event.currentTarget
            ) {
              cancelDeleteChat();
            }
          }}
        >
          <div
            className="ai-chat-dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-chat-title"
          >
            <div
              id="delete-chat-title"
              className="ai-chat-dialog-title"
            >
              Delete chat?
            </div>

            <div className="ai-chat-dialog-text">
              This conversation will be permanently
              deleted from your AI chat history.
            </div>

            <div className="ai-chat-dialog-actions">
              <button
                type="button"
                className="ai-chat-dialog-cancel"
                onClick={cancelDeleteChat}
                disabled={chatActionLoading}
              >
                Cancel
              </button>

              <button
                type="button"
                className="ai-chat-dialog-danger"
                onClick={() =>
                  void deleteChat()
                }
                disabled={chatActionLoading}
              >
                {chatActionLoading
                  ? "Deleting..."
                  : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================
          MAIN
          ===================================================== */}

      <main className="ai-chat-main">
        {/* HEADER */}

        <header className="ai-chat-header">
          <div>
            <div className="ai-chat-header-title">
              AI Assistant
            </div>

            <div className="ai-chat-header-subtitle">
              Independent Gemini Chat
            </div>
          </div>

          <div className="ai-chat-header-controls">
            <select
              className="ai-chat-model-select"
              value={
                currentSession?.model ||
                selectedModel
              }
              disabled={modelUpdating}
              onChange={(event) =>
                void changeModel(event.target.value)
              }
            >
              {CHAT_MODELS.map((model) => (
                <option
                  key={model.id}
                  value={model.id}
                >
                  {model.name}
                </option>
              ))}
            </select>

            <div className="ai-chat-ready">
              <span />
              Ready
            </div>

            {onClose && (
              <button
                type="button"
                className="ai-chat-close"
                onClick={onClose}
                aria-label="Close AI Chat"
              >
                ×
              </button>
            )}
          </div>
        </header>

        {quotaError && (
          <div className="ai-chat-quota-warning">
            <div>
              <strong>MODEL QUOTA REACHED</strong>
              <span>{quotaError}</span>
            </div>

            <button
              type="button"
              onClick={() => setQuotaError(null)}
            >
              ×
            </button>
          </div>
        )}

        {/* CHAT */}

        <div
          ref={messagesRef}
          className="ai-chat-messages"
        >
          {!currentSession ||
          !currentSession.messages ||
          currentSession.messages.length === 0 ? (
            <div className="ai-chat-welcome">
              <div className="ai-chat-welcome-icon">
                ◉
              </div>

              <div className="ai-chat-welcome-title">
                Welcome to AI Assistant
              </div>

              <div className="ai-chat-welcome-text">
                Ask me anything.
              </div>

              <div className="ai-chat-welcome-note">
                This chatbot is independent from JARVIS.
              </div>

              <div className="ai-chat-examples">
                <button
                  type="button"
                  onClick={() =>
                    useExample(
                      "Explain quantum computing"
                    )
                  }
                >
                  Explain quantum computing
                </button>

                <button
                  type="button"
                  onClick={() =>
                    useExample(
                      "Write a Python function"
                    )
                  }
                >
                  Write a Python function
                </button>

                <button
                  type="button"
                  onClick={() =>
                    useExample(
                      "Explain this concept simply"
                    )
                  }
                >
                  Explain this concept simply
                </button>
              </div>
            </div>
          ) : (
            <div className="ai-chat-message-list">
              {currentSession.messages.map(
                (item, index) => (
                  <div
                    key={`${index}-${item.timestamp || ""}`}
                    className={
                      "ai-chat-message-row " +
                      item.role
                    }
                  >
                    <div className="ai-chat-message-label">
                      {item.role === "user"
                        ? "YOU"
                        : "AI"}
                    </div>

                    <div className="ai-chat-message-bubble">
                      {item.role === "assistant" ? (
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code({ className, children, ...props }) {
                              const match = /language-(\w+)/.exec(
                                className || ""
                              );

                              const code = String(children).replace(
                                /\n$/,
                                ""
                              );

                              /*
                              * Inline code:
                              *
                              * `example`
                              */
                              if (!match) {
                                return (
                                  <code
                                    className={className}
                                    {...props}
                                  >
                                    {children}
                                  </code>
                                );
                              }

                              /*
                              * Fenced code block:
                              *
                              * ```python
                              * print("Hello")
                              * ```
                              */
                              return (
                                <div className="ai-chat-code-block">
                                  <div className="ai-chat-code-header">
                                    <span className="ai-chat-code-language">
                                      {match[1]}
                                    </span>

                                    <button
                                      type="button"
                                      className="ai-chat-code-copy-button"
                                      onPointerDown={(event) => {
                                        event.preventDefault();
                                        event.stopPropagation();

                                        void copyCode(code);
                                      }}
                                    >
                                      {copiedCode === code
                                        ? "Copied ✓"
                                        : "Copy"}
                                    </button>
                                  </div>

                                  <div className="ai-chat-code-scroll">
                                    <SyntaxHighlighter
                                      language={match[1]}
                                      style={oneDark}
                                      PreTag="div"
                                      customStyle={{
                                        margin: 0,
                                        padding: "16px",
                                        background: "transparent",
                                        fontSize: "13px",
                                        lineHeight: "1.65",
                                        overflow: "visible",
                                      }}
                                      codeTagProps={{
                                        style: {
                                          fontFamily:
                                            "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                                        },
                                      }}
                                    >
                                      {code}
                                    </SyntaxHighlighter>
                                  </div>
                                </div>
                              );
                            },
                          }}
                        >
                          {item.content}
                        </ReactMarkdown>
                      ) : (
                        item.content
                      )}
                    </div>
                  </div>
                )
              )}

              {loading && (
                <div className="ai-chat-message-row assistant">
                  <div className="ai-chat-message-label">
                    AI
                  </div>

                  <div className="ai-chat-message-bubble ai-chat-thinking">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* COMPOSER */}

        <div className="ai-chat-composer">
          <div className="ai-chat-input-shell">
            <button
              type="button"
              className="ai-chat-input-tool"
              title="Settings"
              aria-label="Settings"
            >
              ⚙
            </button>

            <button
              type="button"
              className="ai-chat-input-tool"
              title="Attach file"
              aria-label="Attach file"
            >
              ⌕
            </button>

            <textarea
              ref={inputRef}
              value={message}
              onChange={(event) => {
                setMessage(event.target.value);

                const textarea = event.target;

                textarea.style.height = "auto";
                textarea.style.height = `${Math.min(
                  textarea.scrollHeight,
                  180
                )}px`;
              }}
              onKeyDown={handleKeyDown}
              placeholder="Message independent AI..."
              rows={1}
              disabled={loading}
            />

            <button
              type="button"
              className="ai-chat-send"
              onClick={() => void sendMessage()}
              disabled={!message.trim() || loading}
              aria-label="Send message"
            >
              ➤
            </button>
          </div>

          <div className="ai-chat-composer-note">
            Independent Gemini conversation ·
            No JARVIS context
          </div>
        </div>
      </main>
    </section>
  );
}
