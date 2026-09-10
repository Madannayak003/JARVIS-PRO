"use client";

import "../app/ai-chat.css";

import {
  FormEvent,
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
                <button
                  type="button"
                  key={chat.id}
                  className={
                    "ai-chat-history-item " +
                    (currentSession?.id === chat.id
                      ? "active"
                      : "")
                  }
                  onClick={() =>
                    void loadChat(chat.id)
                  }
                >
                  <span className="ai-chat-history-icon">
                    ▸
                  </span>

                  <span className="ai-chat-history-text">
                    {chat.title || "New Chat"}
                  </span>
                </button>
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
                      {item.content}
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
              onChange={(event) =>
                setMessage(event.target.value)
              }
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
