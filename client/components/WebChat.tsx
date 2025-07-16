"use client";
import React, { useState, useRef, useEffect } from "react";
import { Send, Search, Globe, MessageCircle } from "lucide-react";
import ReactMarkdown from "react-markdown";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

const TimelineStep = ({ icon, label, content, time, isLast }) => {
    // helper to turn plain‐text lines into linkified React nodes
    const linkify = (text) => {
        if (typeof text !== "string") return text;

        // split on URLs
        const parts = text.split(/(https?:\/\/[^\s]+)/g);
        return parts.map((part, i) =>
            /^https?:\/\//.test(part) ? (
                <a
                    key={i}
                    href={part}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline text-blue-300 hover:text-blue-400"
                >
                    {part}
                </a>
            ) : (
                <span key={i}>{part}</span>
            )
        );
    };

    return (
        <div className="flex items-start gap-3 mb-4">
            <div className="flex flex-col items-center z-10">
                <div className="rounded-full bg-black text-white p-2 border border-gray-700 shadow">
                    {icon}
                </div>
                {!isLast && <div className="w-px flex-1 bg-gray-700 mt-1" />}
            </div>
            <div className="ml-1">
                <div className="text-sm text-gray-300 font-semibold">{label}</div>
                <div className="text-sm text-gray-100">
                    {Array.isArray(content)
                        ? content.map((line, i) => <div key={i}>{linkify(line)}</div>)
                        : linkify(content)}
                </div>
                {time && <div className="text-xs text-gray-500 mt-1">{time}</div>}
            </div>
        </div>
    );
};


const WebSearchApp = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef(null);
    const [threadId, setThreadId] = useState<number>(() => Date.now()); // initial value

    // auto‐scroll
    useEffect(() => {
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        setThreadId(Date.now());
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = { type: "user", content: input.trim(), timestamp: new Date(), events: [] };
        const aiPlaceholder = { type: "assistant", content: "", tokens: [], timestamp: new Date(), events: [] };

        setMessages((m) => [...m, userMessage, aiPlaceholder]);
        setInput("");
        setIsLoading(true);
        setIsTyping(true);

        try {
            const res = await fetch(`${API_BASE}/research/stream?user_input=${encodeURIComponent(input)}&thread_id=${threadId}`);
            const reader = res.body.getReader();
            const dec = new TextDecoder();
            let buf = "";

            let done = false;
            while (!done) {
                const { value, done: streamDone } = await reader.read();
                if (streamDone) break;
                buf += dec.decode(value, { stream: true });

                let idx;
                while ((idx = buf.indexOf("\n\n")) !== -1) {
                    const raw = buf.slice(0, idx).trim();
                    buf = buf.slice(idx + 2);

                    let evType = null, dataObj = null;
                    raw.split("\n").forEach((line) => {
                        if (line.startsWith("event: ")) evType = line.slice(7);
                        if (line.startsWith("data: ")) {
                            try { dataObj = JSON.parse(line.slice(6)); }
                            catch {}
                        }
                    });
                    if (!evType || !dataObj) continue;
                    console.log({ raw, evType, dataObj });

                    if (evType === "token") {
                        setMessages((m) => {
                            const copy = [...m];
                            let i = copy.length - 1;
                            while (i >= 0 && copy[i].type !== "assistant") i--;
                            if (i < 0) return m;
                            copy[i].tokens = copy[i].tokens || [];
                            if (!copy[i].tokens.length || copy[i].tokens.at(-1) !== dataObj.content) {
                                copy[i].tokens.push(dataObj.content);
                            }
                            copy[i].content = copy[i].tokens.join("");
                            return copy;
                        });
                    } else if (evType === "search" || evType === "urls") {
                        setMessages((m) => {
                            const copy = [...m];
                            let i = copy.length - 1;
                            while (i >= 0 && copy[i].type !== "assistant") i--;
                            if (i < 0) return m;
                            const evs = copy[i].events;
                            const last = evs.at(-1);
                            if (!last || last.type !== evType || last.content !== dataObj.content) {
                                evs.push({
                                    type: evType,
                                    content: dataObj.content,
                                    time: new Date().toLocaleTimeString(),
                                });
                            }
                            return copy;
                        });
                    } else if (evType === "done") {
                        done = true;
                        setIsTyping(false);
                    } else if (evType === "error") {
                        setMessages((m) => [
                            ...m,
                            { type: "error", content: dataObj.error, timestamp: new Date(), events: [] },
                        ]);
                        done = true;
                        setIsTyping(false);
                    }
                }
            }
        } catch {
            setMessages((m) => [
                ...m,
                { type: "error", content: "Connection error. Please try again.", timestamp: new Date(), events: [] },
            ]);
            setIsTyping(false);
        } finally {
            setIsLoading(false);
        }
    };



    return (
        <div className="relative h-screen bg-black text-gray-100 font-mono">
            <Link href={"/"}>
            <header className="h-12 flex items-center px-4 border-b border-gray-800 bg-black z-10">
                <h1
                    className="text-xl font-semibold"
                >Local Mind</h1>
            </header>
            </Link>

            {/* scrollable messages */}
            <div
                ref={scrollRef}
                className="absolute inset-x-0 top-12 bottom-24 overflow-y-auto px-4 pt-6 sm:max-w-2xl mx-auto"
                style={{ scrollbarWidth: "none" }}
            >
                {/* hide webkit scrollbar */}
                <style jsx>{`
          div::-webkit-scrollbar {
            display: none;
          }
        `}</style>

                {messages.length === 0 ? (
                    <div className="text-center text-gray-600 mt-16">
                        <MessageCircle className="mx-auto mb-2" size={32} />
                        Ask me anything…
                    </div>
                ) : (
                    messages.map((m, i) => {
                        if (m.type === "user") {
                            return (
                                <h1 key={i} className="text-3xl font-semibold mb-6">
                                    {m.content}
                                </h1>
                            );
                        }
                        if (m.type === "assistant") {
                            return (
                                <div key={i} className="mb-8">
                                    {m.events.length > 0 && (
                                        <div className="mb-4 border-l-4 border-cyan-500 pl-4">
                                            {m.events.map((ev, j) => (
                                                <TimelineStep
                                                    key={j}
                                                    icon={ev.type === "search" ? <Search size={16}/> : <Globe size={16}/>}
                                                    label={ev.type === "search" ? "Web Search" : "Web Result"}
                                                    content={ev.content}
                                                    time={ev.time}
                                                    isLast={j === m.events.length - 1}
                                                />
                                            ))}
                                        </div>
                                    )}

                                    <div className="space-y-4 text-lg leading-relaxed">
                                        <div className="prose prose-invert">
                                            <ReactMarkdown>
                                                {m.content}
                                            </ReactMarkdown>
                                        </div>
                                        {isTyping && i === messages.length - 1 && (
                                            <span className="inline-block w-2 h-5 bg-gray-400 animate-pulse"/>
                                        )}
                                    </div>

                                    <div className="flex justify-between items-center text-sm text-gray-500 mt-4">
                                        <button
                                            onClick={() => navigator.clipboard.writeText(m.content)}
                                            className="hover:underline"
                                        >
                                            Copy
                                        </button>
                                    </div>
                                </div>
                            );
                        }
                        return null;
                    })
                )}
            </div>

            {/* fixed, levitating input */}
            <footer className="fixed inset-x-0 bottom-4 px-4 flex justify-center pointer-events-none z-20 h-12">
                <form
                    onSubmit={handleSubmit}
                    className="pointer-events-auto flex items-center w-full max-w-xl bg-[#111111] border border-[#2e2e2e] rounded-full px-5 py-2 shadow-[0_0_10px_rgba(0,0,0,0.4)]"
                >
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a follow-up…"
                        disabled={isLoading}
                        className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none text-sm"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="text-blue-400 hover:text-blue-500 disabled:opacity-30"
                    >
                        {isLoading ? "…" : <Send size={16} />}
                    </button>
                </form>
            </footer>
        </div>
    );
};

export default WebSearchApp;
