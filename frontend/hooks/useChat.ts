"use client";

/**
 * The open conversation with Rukmani.
 *
 * `send()` adds the customer's message plus an empty reply from Rukmani,
 * then fills that reply in as stream events arrive: text tokens, tool
 * status (which tool is running), and artifacts (product cards, delivery).
 *
 * The server keeps every conversation. `open()` loads one back (e.g. from
 * the chat list, or after a page refresh); `newChat()` starts a fresh one.
 *
 * `confirmCheckout()` places the order for this chat's pending checkout.
 * It is only called from the Confirm button on the summary card.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, confirmCheckout as postCheckout, getChat, streamChat } from "@/lib/api";
import { loadCurrentChatId, saveCurrentChatId } from "@/lib/storage";
import type { ChatMessage, Order, StreamEvent } from "@/lib/types";

function newMessage(role: ChatMessage["role"], text = ""): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role,
    text,
    artifacts: [],
    status: role === "assistant" ? "thinking" : null,
    failed: false,
  };
}

/** Apply one stream event to Rukmani's reply. Returns a new message object. */
function applyEvent(reply: ChatMessage, event: StreamEvent): ChatMessage {
  switch (event.type) {
    case "token":
      return { ...reply, text: reply.text + event.text, status: null };
    case "tool":
      // The status is the tool name; StatusPill shows it in the chosen language.
      return { ...reply, status: event.tool };
    case "artifact":
      return { ...reply, artifacts: [...reply.artifacts, event.artifact] };
    case "error":
      return { ...reply, text: event.message, status: null, failed: true };
    case "done":
      return { ...reply, status: null };
  }
}

interface UseChatOptions {
  /** Called after each reply, so the chat list can refresh (titles, order). */
  onTurnFinished?: () => void;
}

export function useChat({ onTurnFinished }: UseChatOptions = {}) {
  const [chatId, setChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [summary, setSummary] = useState<string | null>(null);
  const [isReplying, setIsReplying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const abort = useRef<AbortController | null>(null);

  const updateMessage = useCallback((id: string, update: (m: ChatMessage) => ChatMessage) => {
    setMessages((all) => all.map((m) => (m.id === id ? update(m) : m)));
  }, []);

  /** Start a fresh conversation. */
  const newChat = useCallback(() => {
    abort.current?.abort();
    setChatId(null);
    setMessages([]);
    setSummary(null);
    setIsReplying(false);
    saveCurrentChatId(null);
  }, []);

  /** Reopen a saved conversation from the server. */
  const open = useCallback(
    async (id: string) => {
      abort.current?.abort();
      setIsReplying(false);
      setIsLoading(true);
      try {
        const history = await getChat(id);
        setChatId(id);
        setMessages(history.messages);
        setSummary(history.summary);
        saveCurrentChatId(id);
      } catch {
        newChat(); // deleted, or not this visitor's — start fresh instead
      } finally {
        setIsLoading(false);
      }
    },
    [newChat],
  );

  // After a refresh, reopen the chat the customer was in (browser-only, so
  // it runs after the first render to match the pre-built page).
  useEffect(() => {
    const saved = loadCurrentChatId();
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time restore after load
    if (saved) void open(saved);
  }, [open]);

  const send = useCallback(
    async (text: string) => {
      const message = text.trim();
      if (!message || isReplying) return;

      // A new chat gets its id on the first message; the server lists it then.
      const id = chatId ?? crypto.randomUUID();
      if (!chatId) {
        setChatId(id);
        saveCurrentChatId(id);
      }

      const reply = newMessage("assistant");
      setMessages((all) => [...all, newMessage("user", message), reply]);
      setIsReplying(true);

      abort.current = new AbortController();
      try {
        await streamChat(
          id,
          message,
          (event) => updateMessage(reply.id, (m) => applyEvent(m, event)),
          abort.current.signal,
        );
      } catch (error) {
        if ((error as Error).name !== "AbortError") {
          // Messages from our server (e.g. "please wait a few minutes") are
          // written for customers. For anything else (a connection problem) the
          // text stays empty and the UI shows its own message in the chosen language.
          const text = error instanceof ApiError ? error.message : "";
          updateMessage(reply.id, (m) => ({ ...m, text, status: null, failed: true }));
        }
      } finally {
        // If the stream ended without a "done" event, stop showing the status.
        updateMessage(reply.id, (m) => ({ ...m, status: null }));
        setIsReplying(false);
        onTurnFinished?.();
      }
    },
    [chatId, isReplying, updateMessage, onTurnFinished],
  );

  const confirmCheckout = useCallback(async (): Promise<Order> => {
    if (!chatId) throw new Error("Start a conversation first.");
    return postCheckout(chatId);
  }, [chatId]);

  return { chatId, messages, summary, isReplying, isLoading, send, confirmCheckout, open, newChat };
}
