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

Checks: `npm run lint` · `npx tsc --noEmit` · `npm run build`

## How the code is organised

| Path | Job |
|---|---|
| `app/` | Page, root layout (fonts, metadata) and `globals.css` (Kapruka colour tokens). |
| `lib/types.ts` | Types shared with the backend. Keep in sync with the backend's `models.py` and `events.py`. |
| `lib/api.ts` | `streamChat` (`POST /api/chat`, parses the Server-Sent Events reply) and `confirmCheckout` (`POST /api/checkout`). |
| `hooks/useChat.ts` | Conversation state: applies each stream event to Rukmani's reply. |
| `components/chat/` | Screen layout: header with cart, welcome screen, messages, status pill, message box, cart drawer. `ChatActions.tsx` shares actions like "send" with the cards. |
| `components/cards/` | What tools produced: product carousel, product details, delivery check, cart, checkout summary (with gift card preview) and the pay-link card. |

Cart changes from the UI ("Add to cart", remove in the drawer) are sent to Rukmani as messages, so she always knows the cart. Only the **Confirm** button on the checkout summary places an order.

## Brand colours

Taken from kapruka.com's stylesheet and logo, defined once in `app/globals.css` and used as Tailwind classes (`bg-brand`, `text-sun`, ...):

| Token | Colour | Used for |
|---|---|---|
| `brand` | `#402970` | Buttons, prices, customer messages |
| `brand-logo` | `#442a73` | Header (matches the logo's background) |
| `sun` | `#f8da08` | The logo's yellow "smile": send button, avatar ring, sale badge |
| `brand-tint` / `brand-mist` | `#f9f7ff` / `#edf0f8` | Page and card backgrounds |
| `ink` / `ink-soft` | `#111111` / `#3a3b3c` | Text |

Fonts: Roboto (Kapruka's font) with Noto Sans Sinhala for Sinhala script.
