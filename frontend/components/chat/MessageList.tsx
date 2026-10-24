"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/lib/types";
import { AssistantMessage } from "./AssistantMessage";
import { UserMessage } from "./UserMessage";

interface MessageListProps {
  messages: ChatMessage[];
}

/** The conversation. Keeps the newest message in view as replies stream in. */
export function MessageList({ messages }: MessageListProps) {
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 px-4 py-6">
      {messages.map((message) =>
        message.role === "user" ? (
          <UserMessage key={message.id} text={message.text} />
        ) : (
          <AssistantMessage key={message.id} message={message} />
        ),
      )}
      <div ref={bottom} />
    </div>
  );
}
