/**
 * Keeps the current conversation in the browser, so a page refresh shows
 * the same chat. The backend has the real conversation (by thread id);
 * this is only what the screen shows.
 *
 * Browser storage can be unavailable (private mode, blocked cookies), so
 * every access is wrapped: if it fails, the chat simply starts fresh.
 */

import type { ChatMessage } from "./types";

const CHAT_KEY = "rukmani:chat";

interface SavedChat {
  threadId: string;
  messages: ChatMessage[];
}

export function loadChat(): SavedChat | null {
  try {
    const raw = localStorage.getItem(CHAT_KEY);
    return raw ? (JSON.parse(raw) as SavedChat) : null;
  } catch {
    return null;
  }
}

export function saveChat(chat: SavedChat): void {
  try {
    localStorage.setItem(CHAT_KEY, JSON.stringify(chat));
  } catch {
    // Storage full or blocked — not worth interrupting the customer for.
  }
}

export function clearChat(): void {
  try {
    localStorage.removeItem(CHAT_KEY);
  } catch {
    // Same as above.
  }
}
