# Basic Chat Layout (React + TypeScript)

This project contains a minimal, responsive chat layout built with Vite + React + TypeScript. It's intentionally API‑agnostic so you can integrate a backend (WebSocket, REST, Socket.IO) later.

## Quick start

1. Install dependencies:

```bash
npm install
```

2. Run development server:

```bash
npm run dev
```

3. Open http://localhost:3000

## Files of interest

- `src/components/ChatLayout.tsx` — high-level layout
- `src/components/MessageList.tsx` — renders messages
- `src/components/MessageInput.tsx` — input + send handling
- `src/App.tsx` — example wiring (local state)

## Integrating an API later

- Provide an `onSend` that posts the message to your API and updates the local state when the server confirms:

```ts
// Example: App passes this to ChatLayout
const handleSend = async (text: string) => {
  const payload = await fetch("/api/messages", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
  const saved = await payload.json();
  setMessages((s) => [...s, saved]);
};
```

## Notes

- No persistence or auth included — kept minimal to make backend integration straightforward.
- Styling is plain CSS for easy customization.

If you'd like, I can now add localStorage persistence, or scaffold a basic Socket.IO server for real-time messaging — tell me which you prefer.
