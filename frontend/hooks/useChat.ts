"use client";

/**
 * Chat state for one conversation with Rukmani.
 *
 * `send()` adds the customer's message plus an empty reply from Rukmani,
 * then fills that reply in as stream events arrive: text tokens, tool
 * status ("Searching Kapruka..."), and artifacts (product cards, delivery).
 */

import { useCallback, useRef, useState } from "react";
import { streamChat } from "@/lib/api";
import type { ChatMessage, StreamEvent } from "@/lib/types";

const CONNECTION_ERROR =
  "I can't reach the shop right now. Please check your connection and try again.";

function newMessage(role: ChatMessage["role"], text = ""): ChatMessage {
  return {
    id: crypto.randomUUID(),
    role,
    text,
    artifacts: [],
    status: role === "assistant" ? "Thinking" : null,
    failed: false,
  };
}

/** Apply one stream event to Rukmani's reply. Returns a new message object. */
function applyEvent(reply: ChatMessage, event: StreamEvent): ChatMessage {
  switch (event.type) {
    case "token":
      return { ...reply, text: reply.text + event.text, status: null };
    case "tool":
      return { ...reply, status: event.label };
    case "artifact":
      return { ...reply, artifacts: [...reply.artifacts, event.artifact] };
    case "error":
      return { ...reply, text: event.message, status: null, failed: true };
    case "done":
      return { ...reply, status: null };
  }
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isReplying, setIsReplying] = useState(false);

  // The backend remembers the conversation by this id. Created on the
  // first message, and replaced when the customer starts a new chat.
  const threadId = useRef<string | null>(null);
  const abort = useRef<AbortController | null>(null);

  const updateMessage = useCallback((id: string, update: (m: ChatMessage) => ChatMessage) => {
    setMessages((all) => all.map((m) => (m.id === id ? update(m) : m)));
  }, []);

  const send = useCallback(
    async (text: string) => {
      const message = text.trim();
      if (!message || isReplying) return;

      threadId.current ??= crypto.randomUUID();
      const reply = newMessage("assistant");
      setMessages((all) => [...all, newMessage("user", message), reply]);
      setIsReplying(true);

      abort.current = new AbortController();
      try {
        await streamChat(
          threadId.current,
          message,
          (event) => updateMessage(reply.id, (m) => applyEvent(m, event)),
          abort.current.signal,
        );
      } catch (error) {
        if ((error as Error).name !== "AbortError") {
          updateMessage(reply.id, (m) => ({ ...m, text: CONNECTION_ERROR, status: null, failed: true }));
        }
      } finally {
        // If the stream ended without a "done" event, stop showing the status.
        updateMessage(reply.id, (m) => ({ ...m, status: null }));
        setIsReplying(false);
      }
    },
    [isReplying, updateMessage],
  );

  /** Start a fresh conversation (new thread on the backend too). */
  const reset = useCallback(() => {
    abort.current?.abort();
    threadId.current = null;
    setMessages([]);
    setIsReplying(false);
  }, []);

  return { messages, isReplying, send, reset };
}
