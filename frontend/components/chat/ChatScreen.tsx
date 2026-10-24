"use client";

/**
 * The full-screen chat: header on top, conversation in the middle,
 * message box at the bottom. Before the first message, a welcome screen
 * with suggestions takes the conversation's place.
 */

import { useChat } from "@/hooks/useChat";
import { Composer } from "./Composer";
import { Header } from "./Header";
import { MessageList } from "./MessageList";
import { Welcome } from "./Welcome";

export function ChatScreen() {
  const { messages, isReplying, send, reset } = useChat();
  const hasStarted = messages.length > 0;

  return (
    <div className="flex h-dvh flex-col">
      <Header onNewChat={reset} canReset={hasStarted} />

      <main className="flex-1 overflow-y-auto">
        {hasStarted ? <MessageList messages={messages} /> : <Welcome onPick={send} />}
      </main>

      <Composer onSend={send} disabled={isReplying} />
    </div>
  );
}
