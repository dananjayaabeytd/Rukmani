"use client";

/**
 * The visitor's chat list (newest first), with rename and delete.
 * Rename and delete update the list straight away, then sync with the server.
 */

import { useCallback, useEffect, useState } from "react";
import { deleteChat, listChats, renameChat } from "@/lib/api";
import type { ChatSummary } from "@/lib/types";

export function useChats() {
  const [chats, setChats] = useState<ChatSummary[]>([]);

  const refresh = useCallback(async () => {
    try {
      setChats(await listChats());
    } catch {
      // Keep showing the last list; the next refresh will try again.
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- initial load from the server
    void refresh();
  }, [refresh]);

  const rename = useCallback(
    async (id: string, title: string) => {
      setChats((all) => all.map((c) => (c.id === id ? { ...c, title } : c)));
      await renameChat(id, title).catch(refresh); // on failure, show the real list again
    },
    [refresh],
  );

  const remove = useCallback(
    async (id: string) => {
      setChats((all) => all.filter((c) => c.id !== id));
      await deleteChat(id).catch(refresh);
    },
    [refresh],
  );

  return { chats, refresh, rename, remove };
}
