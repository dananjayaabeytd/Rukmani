/**
 * The small things this browser remembers:
 *
 *   visitor id   a private random id that owns this browser's chats and
 *                memories on the server (there's no sign-in)
 *   current chat which chat to reopen after a page refresh
 *   sidebar      whether the chat list is collapsed (desktop)
 *
 * Conversations themselves live on the server. Browser storage can be
 * blocked (private mode), so every access is wrapped: the visitor id then
 * lasts for this visit only.
 */

const VISITOR_KEY = "rukmani:visitor";
const CURRENT_CHAT_KEY = "rukmani:current-chat";
const SIDEBAR_KEY = "rukmani:sidebar-collapsed";

let visitorForThisVisit: string | null = null;

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string | null): void {
  try {
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch {
    // Storage blocked — fine, it just won't be remembered.
  }
}

/** This browser's private visitor id, created on first use. */
export function getVisitorId(): string {
  visitorForThisVisit ??= read(VISITOR_KEY) ?? `v-${crypto.randomUUID()}`;
  write(VISITOR_KEY, visitorForThisVisit);
  return visitorForThisVisit;
}

export function loadCurrentChatId(): string | null {
  return read(CURRENT_CHAT_KEY);
}

export function saveCurrentChatId(chatId: string | null): void {
  write(CURRENT_CHAT_KEY, chatId);
}

export function loadSidebarCollapsed(): boolean {
  return read(SIDEBAR_KEY) === "1";
}

export function saveSidebarCollapsed(collapsed: boolean): void {
  write(SIDEBAR_KEY, collapsed ? "1" : null);
}
