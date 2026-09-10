"use client";

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
          data?.message ||
          "AI response failed.";

        if (
          response.status === 429 ||
          String(errorText).includes("RESOURCE_EXHAUSTED")
        ) {
          setQuotaError(
            `The ${session!.model || selectedModel} model has reached its current Gemini quota. Please choose another model above and try again.`
          );

          throw new Error(
            "Model quota reached. Choose another model."
          );
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

      <style jsx>{`
        .ai-chat-window {
          position: fixed;
          inset: 18px;
          z-index: 500;
          display: flex;
          overflow: hidden;
          background: #02080d;
          border: 1px solid rgba(0, 190, 255, 0.42);
          box-shadow:
            0 0 35px rgba(0, 160, 255, 0.13),
            inset 0 0 35px rgba(0, 100, 150, 0.04);
          color: #d8f7ff;
          font-family:
            "Courier New",
            Consolas,
            monospace;
        }

        .ai-chat-sidebar {
          width: 285px;
          min-width: 285px;
          display: flex;
          flex-direction: column;
          background: #020b11;
          border-right: 1px solid rgba(0, 190, 255, 0.3);
        }

        .ai-chat-brand {
          padding: 24px 20px 18px;
          border-bottom: 1px solid
            rgba(0, 190, 255, 0.22);
        }

        .ai-chat-brand-title {
          color: #f3b51b;
          font-size: 22px;
          font-weight: 700;
          letter-spacing: 4px;
          text-transform: uppercase;
        }

        .ai-chat-robot {
          margin-right: 10px;
        }

        .ai-chat-brand-subtitle {
          margin-top: 7px;
          color: rgba(243, 181, 27, 0.55);
          font-size: 9px;
          letter-spacing: 2px;
        }

        .ai-chat-new-button {
          margin: 18px;
          padding: 13px 15px;
          border: 1px solid rgba(0, 200, 255, 0.45);
          background: rgba(0, 150, 200, 0.09);
          color: #f3b51b;
          font: inherit;
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 1px;
          cursor: pointer;
          text-align: left;
        }

        .ai-chat-new-button:hover {
          background: rgba(0, 200, 255, 0.12);
          border-color: #00c8ff;
        }

        .ai-chat-sidebar-section {
          flex: 1;
          min-height: 0;
          padding: 8px 12px;
          overflow: hidden;
        }

        .ai-chat-section-title {
          padding: 12px 8px;
          color: #00c8ff;
          font-size: 10px;
          letter-spacing: 2px;
          border-bottom: 1px solid
            rgba(0, 190, 255, 0.15);
        }

        .ai-chat-history {
          height: calc(100% - 45px);
          overflow-y: auto;
          padding-top: 6px;
        }

        .ai-chat-history-item {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 9px;
          padding: 11px 8px;
          margin-bottom: 2px;
          border: 1px solid transparent;
          background: transparent;
          color: #8fb4c0;
          font: inherit;
          font-size: 11px;
          text-align: left;
          cursor: pointer;
        }

        .ai-chat-history-item:hover,
        .ai-chat-history-item.active {
          color: #f3b51b;
          border-color: rgba(0, 190, 255, 0.28);
          background: rgba(0, 190, 255, 0.06);
        }

        .ai-chat-history-icon {
          color: #00c8ff;
        }

        .ai-chat-history-text {
          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;
        }

        .ai-chat-empty {
          padding: 18px 8px;
          color: rgba(150, 190, 200, 0.45);
          font-size: 10px;
        }

        .ai-chat-sidebar-footer {
          padding: 14px 18px;
          border-top: 1px solid
            rgba(0, 190, 255, 0.18);
          font-size: 10px;
        }

        .ai-chat-independent {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #8fb4c0;
        }

        .ai-chat-status-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #00e676;
          box-shadow: 0 0 8px #00e676;
        }

        .ai-chat-model-small {
          margin-top: 7px;
          color: rgba(150, 190, 200, 0.45);
        }

        .ai-chat-main {
          flex: 1;
          min-width: 0;
          display: flex;
          flex-direction: column;
        }

        .ai-chat-header {
          min-height: 72px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 24px;
          border-bottom: 1px solid
            rgba(0, 190, 255, 0.24);
          background: rgba(0, 20, 30, 0.7);
        }

        .ai-chat-header-title {
          color: #f3b51b;
          font-size: 18px;
          font-weight: 700;
          letter-spacing: 2px;
          text-transform: uppercase;
        }

        .ai-chat-header-subtitle {
          margin-top: 5px;
          color: rgba(130, 190, 205, 0.5);
          font-size: 9px;
          letter-spacing: 2px;
        }

        .ai-chat-header-controls {
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .ai-chat-model {
          padding: 8px 12px;
          border: 1px solid
            rgba(0, 190, 255, 0.28);
          color: #8edfff;
          font-size: 10px;
        }

        .ai-chat-model span {
          color: #f3b51b;
          margin-right: 6px;
        }

        .ai-chat-ready {
          display: flex;
          align-items: center;
          gap: 7px;
          color: #00e676;
          font-size: 10px;
          letter-spacing: 1px;
        }

        .ai-chat-ready span {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #00e676;
          box-shadow: 0 0 8px #00e676;
        }

        .ai-chat-close {
          width: 34px;
          height: 34px;
          border: 1px solid rgba(0, 190, 255, 0.35);
          background: transparent;
          color: #f3b51b;
          font: inherit;
          font-size: 20px;
          cursor: pointer;
        }

        .ai-chat-close:hover {
          background: rgba(255, 80, 80, 0.12);
          border-color: #ff6868;
          color: #ff6868;
        }

        .ai-chat-messages {
          flex: 1;
          min-height: 0;
          overflow-y: auto;
          padding: 28px 36px;
          background:
            radial-gradient(
              circle at 50% 40%,
              rgba(0, 150, 200, 0.055),
              transparent 42%
            ),
            #02080d;
        }

        .ai-chat-welcome {
          min-height: 100%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          text-align: center;
        }

        .ai-chat-welcome-icon {
          width: 68px;
          height: 68px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 20px;
          border: 1px solid #00c8ff;
          color: #00c8ff;
          font-size: 28px;
          box-shadow: 0 0 24px rgba(0, 200, 255, 0.15);
        }

        .ai-chat-welcome-title {
          color: #f3b51b;
          font-size: 25px;
          font-weight: 700;
          letter-spacing: 2px;
        }

        .ai-chat-welcome-text {
          margin-top: 10px;
          color: #a5c4cc;
          font-size: 13px;
        }

        .ai-chat-welcome-note {
          margin-top: 7px;
          color: rgba(140, 190, 205, 0.42);
          font-size: 9px;
          letter-spacing: 1px;
        }

        .ai-chat-examples {
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          gap: 8px;
          margin-top: 28px;
        }

        .ai-chat-examples button {
          padding: 10px 14px;
          border: 1px solid
            rgba(0, 190, 255, 0.3);
          background: rgba(0, 150, 200, 0.055);
          color: #8edfff;
          font: inherit;
          font-size: 10px;
          cursor: pointer;
        }

        .ai-chat-examples button:hover {
          border-color: #00c8ff;
          color: #f3b51b;
        }

        .ai-chat-message-list {
          max-width: 1050px;
          margin: 0 auto;
        }

        .ai-chat-message-row {
          margin-bottom: 24px;
        }

        .ai-chat-message-label {
          margin-bottom: 6px;
          color: #00c8ff;
          font-size: 9px;
          letter-spacing: 2px;
        }

        .ai-chat-message-row.user {
          padding-left: 12%;
        }

        .ai-chat-message-row.user
          .ai-chat-message-label {
          color: #f3b51b;
          text-align: right;
        }

        .ai-chat-message-bubble {
          padding: 15px 17px;
          border: 1px solid
            rgba(0, 190, 255, 0.2);
          background: rgba(0, 30, 42, 0.55);
          color: #cce9ef;
          font-size: 12px;
          line-height: 1.7;
          white-space: pre-wrap;
          word-break: break-word;
        }

        .ai-chat-message-row.user
          .ai-chat-message-bubble {
          border-color: rgba(243, 181, 27, 0.24);
          background: rgba(55, 38, 5, 0.25);
          color: #f1d58a;
        }

        .ai-chat-thinking {
          display: flex;
          gap: 5px;
          width: fit-content;
        }

        .ai-chat-thinking span {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: #00c8ff;
          animation: aiChatPulse 1s infinite;
        }

        .ai-chat-thinking span:nth-child(2) {
          animation-delay: 0.15s;
        }

        .ai-chat-thinking span:nth-child(3) {
          animation-delay: 0.3s;
        }

        @keyframes aiChatPulse {
          0%,
          100% {
            opacity: 0.25;
          }

          50% {
            opacity: 1;
          }
        }

        .ai-chat-composer {
          padding: 14px 22px 11px;
          border-top: 1px solid
            rgba(0, 190, 255, 0.25);
          background: rgba(0, 15, 23, 0.9);
        }

        .ai-chat-input-shell {
          display: flex;
          align-items: center;
          gap: 7px;
          padding: 7px 9px;
          border: 1px solid
            rgba(0, 190, 255, 0.35);
          background: #020a10;
        }

        .ai-chat-input-tool {
          width: 34px;
          height: 34px;
          flex-shrink: 0;
          border: 1px solid
            rgba(0, 190, 255, 0.2);
          background: transparent;
          color: #7ea8b4;
          cursor: pointer;
        }

        .ai-chat-input-tool:hover {
          color: #f3b51b;
          border-color: #00c8ff;
        }

        .ai-chat-input-shell textarea {
          flex: 1;
          min-width: 0;
          min-height: 34px;
          max-height: 130px;
          resize: none;
          padding: 8px 5px;
          border: none;
          outline: none;
          background: transparent;
          color: #dff8ff;
          font: inherit;
          font-size: 12px;
        }

        .ai-chat-input-shell textarea::placeholder {
          color: rgba(130, 180, 195, 0.4);
        }

        .ai-chat-send {
          width: 42px;
          height: 38px;
          flex-shrink: 0;
          border: 1px solid #00c8ff;
          background: rgba(0, 190, 255, 0.12);
          color: #f3b51b;
          font-size: 17px;
          cursor: pointer;
        }

        .ai-chat-send:hover:not(:disabled) {
          background: rgba(0, 190, 255, 0.24);
          box-shadow: 0 0 15px
            rgba(0, 190, 255, 0.18);
        }

        .ai-chat-send:disabled {
          opacity: 0.3;
          cursor: default;
        }

        .ai-chat-composer-note {
          padding-top: 7px;
          color: rgba(120, 175, 190, 0.35);
          font-size: 8px;
          text-align: center;
          letter-spacing: 1px;
        }

        @media (max-width: 800px) {
          .ai-chat-window {
            inset: 0;
          }

          .ai-chat-sidebar {
            width: 220px;
            min-width: 220px;
          }

          .ai-chat-messages {
            padding: 20px;
          }

          .ai-chat-message-row.user {
            padding-left: 5%;
          }

          .ai-chat-header-controls {
            gap: 7px;
          }

          .ai-chat-model {
            display: none;
          }
        }
      `}</style>
    </section>
  );
}
