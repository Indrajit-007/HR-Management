"use client";

import { FormEvent, useMemo, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

type Role = "user" | "assistant";
type Message = { role: Role; content: string; tools?: string[]; timestamp: string };
type Tab = "chat" | "system" | "analytics";

const samples = [
  "What holidays are coming up?",
  "Who works in Engineering?",
  "What's the sick leave policy?",
  "Search for John",
  "What team events are planned?",
];

const serverCards = [
  {
    icon: "▤",
    title: "Database Server",
    purpose: "Employee records and leave balances",
    storage: "SQLite",
    tools: ["get_employee_info", "get_leave_balance", "get_department_summary", "search_employees"],
  },
  {
    icon: "▧",
    title: "Filesystem Server",
    purpose: "Company announcements and updates",
    storage: "Text files",
    tools: ["list_announcements", "read_announcement", "get_recent_announcements", "search_announcements"],
  },
  {
    icon: "✧",
    title: "RAG Server",
    purpose: "Semantic search over policy documents",
    storage: "ChromaDB",
    tools: ["query_documents", "query_policies", "query_announcements", "get_policy_summary", "list_policies"],
  },
];

export default function Home() {
  const [tab, setTab] = useState<Tab>("chat");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const usedTools = useMemo(
    () => messages.flatMap((message) => message.tools ?? []),
    [messages],
  );
  const totalTools = serverCards.reduce((total, server) => total + server.tools.length, 0);

  async function sendMessage(text: string) {
    const question = text.trim();
    if (!question || busy) return;

    const userMessage: Message = {
      role: "user",
      content: question,
      timestamp: new Date().toISOString(),
    };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setError("");
    setBusy(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: nextMessages.map(({ role, content }) => ({ role, content })),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "The assistant could not answer.");

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.answer,
          tools: data.toolsUsed ?? [],
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Something went wrong.");
    } finally {
      setBusy(false);
      requestAnimationFrame(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }));
    }
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void sendMessage(input);
  }

  function clearChat() {
    setMessages([]);
    setError("");
    setInput("");
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">✧</div>
          <div>
            <div className="brand-name">RAG-MCP ASSISTANT</div>
            <div className="brand-sub">Your HR knowledge companion</div>
          </div>
        </div>

        <div className="side-label">Session stats</div>
        <div className="stats-row">
          <div className="stat-card"><div className="stat-label">Queries</div><div className="stat-value">{messages.filter((m) => m.role === "user").length}</div></div>
          <div className="stat-card"><div className="stat-label">Tools used</div><div className="stat-value">{new Set(usedTools).size}</div></div>
        </div>

        <div className="side-label">System info</div>
        <div className="side-card">
          <div className="system-line"><span>Assistant</span><span className="status-dot">Ready</span></div>
          <div className="system-line"><span>Provider</span><span>Groq</span></div>
          <div className="system-line"><span>MCP servers</span><span>03</span></div>
          <div className="system-line"><span>Available tools</span><span>{totalTools}</span></div>
        </div>

        <div className="side-label">Quick actions</div>
        <div className="quick-list">
          {samples.map((sample) => (
            <button className="quick-button" key={sample} onClick={() => void sendMessage(sample)} disabled={busy}>
              <span aria-hidden="true">↗</span>&nbsp; {sample}
            </button>
          ))}
        </div>
        <div className="side-spacer" />
        <button className="clear-button" onClick={clearChat}>↻ &nbsp; Clear chat</button>
        <div className="sidebar-footer">RAG + MCP · Powered by Groq</div>
      </aside>

      <main className="main">
        <header className="topline">
          <div>
            <div className="eyebrow">People · Policies · Announcements</div>
            <h1>RAG-MCP Intelligent Assistant</h1>
            <div className="subtitle">Ask me anything about employees, policies, or announcements.</div>
          </div>
          <div className="top-pill">Assistant online</div>
        </header>

        <nav className="tabs" aria-label="Application sections">
          <button className={`tab ${tab === "chat" ? "active" : ""}`} onClick={() => setTab("chat")}>◉ &nbsp; Chat</button>
          <button className={`tab ${tab === "system" ? "active" : ""}`} onClick={() => setTab("system")}>⌘ &nbsp; System details</button>
          <button className={`tab ${tab === "analytics" ? "active" : ""}`} onClick={() => setTab("analytics")}>▥ &nbsp; Analytics</button>
        </nav>

        <section className="content">
          {tab === "chat" && (
            <div className="glass-card chat-card">
              <div className="chat-heading">
                <div><h2>Assistant chat</h2><p>Answers grounded in your connected company data</p></div>
                <span className="status-dot">Live</span>
              </div>
              <div className="chat-body">
                {messages.length === 0 && (
                  <div className="welcome">
                    <div className="welcome-icon">✧</div>
                    <h3>Welcome! How can I help?</h3>
                    <p>Your assistant can look across employee records, company announcements, and HR policy documents.</p>
                    <div className="welcome-grid">
                      <div className="welcome-item"><span>⌕</span><div><b>Employee information</b>Search by name, department, or ID</div></div>
                      <div className="welcome-item"><span>▧</span><div><b>Announcements</b>Holidays, events, and updates</div></div>
                      <div className="welcome-item"><span>▤</span><div><b>Policy questions</b>Leave, salary, and HR policies</div></div>
                      <div className="welcome-item"><span>⤢</span><div><b>Connected answers</b>Combine information across sources</div></div>
                    </div>
                  </div>
                )}
                {messages.map((message, index) => (
                  <div key={`${message.timestamp}-${index}`}>
                    <div className={`message ${message.role}`}>
                      <div className="avatar">{message.role === "user" ? "Y" : "✧"}</div>
                      <div className="bubble">
                        {message.role === "assistant" ? (
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content}
                          </ReactMarkdown>
                        ) : message.content}
                      </div>
                    </div>
                    {message.role === "assistant" && message.tools && message.tools.length > 0 && (
                      <div className="tool-tags">{message.tools.map((tool, i) => <span className="tool-tag" key={`${tool}-${i}`}>↗ {tool}</span>)}</div>
                    )}
                  </div>
                ))}
                {busy && <div className="typing">Thinking · checking connected sources…</div>}
                <div ref={bottomRef} />
              </div>
              {error && <div className="error-box">{error}</div>}
              <form className="composer" onSubmit={submit}>
                <input value={input} onChange={(event) => setInput(event.target.value)} placeholder="Ask about employees, policies, or announcements…" aria-label="Your question" disabled={busy} />
                <button className="send-button" type="submit" disabled={busy || !input.trim()}>{busy ? "Working…" : <>Send&nbsp; ↗</>}</button>
              </form>
            </div>
          )}

          {tab === "system" && (
            <>
              <div className="details-grid">
                {serverCards.map((server) => (
                  <article className="glass-card detail-card" key={server.title}>
                    <div className="detail-icon">{server.icon}</div>
                    <h3>{server.title}</h3>
                    <p>{server.purpose}<br />Storage: {server.storage}</p>
                    <div className="tool-list">{server.tools.map((tool) => <span key={tool}>{tool}</span>)}</div>
                  </article>
                ))}
              </div>
              <div className="glass-card flow-card">
                <h2>Orchestration flow</h2>
                <div className="flow">
                  <span className="flow-node">Your question</span><span className="flow-arrow">→</span>
                  <span className="flow-node emphasis">Groq assistant</span><span className="flow-arrow">→</span>
                  <span className="flow-node">Tool selection</span><span className="flow-arrow">→</span>
                  <span className="flow-node emphasis">3 MCP servers</span><span className="flow-arrow">→</span>
                  <span className="flow-node">Grounded answer</span>
                </div>
              </div>
            </>
          )}

          {tab === "analytics" && (
            <>
              <h2 className="analytics-head">Usage analytics</h2>
              <div className="analytics-grid">
                <div className="glass-card analytics-card"><div className="stat-label">Total queries</div><div className="stat-value">{messages.filter((m) => m.role === "user").length}</div></div>
                <div className="glass-card analytics-card"><div className="stat-label">Unique tools</div><div className="stat-value">{new Set(usedTools).size}</div></div>
                <div className="glass-card analytics-card"><div className="stat-label">Messages</div><div className="stat-value">{messages.length}</div></div>
                <div className="glass-card analytics-card"><div className="stat-label">MCP servers</div><div className="stat-value">03</div></div>
              </div>
              <div className="glass-card history-card">
                <h3>Recent conversation</h3>
                {messages.length === 0 ? <div className="empty-state">Your conversation history will appear here.</div> : [...messages].reverse().map((message, index) => (
                  <div className="history-row" key={`${message.timestamp}-history-${index}`}>
                    <span>{message.role === "user" ? "You" : "Assistant"}: {message.content}</span>
                    <small>{new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</small>
                  </div>
                ))}
              </div>
            </>
          )}
        </section>
        <footer className="footer">Made for people teams · Powered by RAG, MCP, and Groq</footer>
      </main>
    </div>
  );
}
