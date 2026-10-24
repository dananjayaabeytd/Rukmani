# Rukmani frontend

Next.js full-screen chat for Rukmani. It streams replies from the backend and shows Kapruka products, product details and delivery checks as cards, styled with Kapruka's own colours.

## Run it

Start the backend first (see [`../backend/README.md`](../backend/README.md)), then:

```bash
cd frontend
cp .env.example .env.local    # NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev                   # http://localhost:3000
```

Checks: `npm run lint` · `npm run typecheck` · `npm run build`

## How the code is organised

| Path | Job |
|---|---|
| `app/` | Page, root layout (fonts, metadata) and `globals.css` (Kapruka colour tokens). |
| `lib/types.ts` | Types shared with the backend. Keep in sync with the backend's `models.py` and `events.py`. |
| `lib/api.ts` | `streamChat` (`POST /api/chat`, parses the Server-Sent Events reply), `confirmCheckout`, the chat list (list, open, rename, delete) and memory (list, forget). Every call sends the visitor id. |
| `lib/i18n.ts` | Every interface string in English, Sinhala and Tamil. |
| `lib/occasions.ts` | Sri Lankan gifting occasions for the "coming up soon" banner. |
| `lib/storage.ts` | The browser's anonymous visitor id and the open chat's id. The chats themselves are kept by the server. |
| `hooks/useChat.ts` | The open conversation: applies each stream event to Rukmani's reply, opens saved chats, starts new ones. |
| `hooks/useChats.ts` | The chat list in the sidebar (rename, delete). |
| `components/LanguageProvider.tsx` | The chosen interface language (remembered in the browser). |
| `components/chat/` | Screen layout: sidebar with your chats (a slide-in panel on phones), header (language switch, cart), welcome screen with occasion banner, messages, status pill, message box, cart drawer, and the *What Rukmani remembers* panel. `ChatActions.tsx` shares actions like "send" with the cards. |
| `components/cards/` | What tools produced: product carousel, product details, delivery check with date picker, cart, checkout summary (with gift card preview), gift unboxing + pay-link card, and order tracking. |

Cart changes from the UI ("Add to cart", remove in the drawer, a date in the date picker) are sent to Rukmani as messages in the chosen language, so she always knows the cart and answers in that language. Only the **Confirm** button on the checkout summary places an order.

## Languages

Switch with **EN / සිං / தமிழ்** in the header. To add or change a string, edit `lib/i18n.ts`. The `Strings` type makes TypeScript point out any language that's missing it.

## Brand colours

Taken from kapruka.com's stylesheet and logo, defined once in `app/globals.css` and used as Tailwind classes (`bg-brand`, `text-sun`, ...):

| Token | Colour | Used for |
|---|---|---|
| `brand` | `#402970` | Buttons, prices, customer messages |
| `brand-logo` | `#442a73` | Header (matches the logo's background) |
| `sun` | `#f8da08` | The logo's yellow "smile": send button, avatar ring, sale badge |
| `brand-tint` / `brand-mist` | `#f9f7ff` / `#edf0f8` | Page and card backgrounds |
| `ink` / `ink-soft` | `#111111` / `#3a3b3c` | Text |

Fonts: Roboto (Kapruka's font) with Noto Sans Sinhala and Noto Sans Tamil for those scripts.
