Reference production start:

```json
"start": "node --import ./observability.mjs ./node_modules/@react-router/serve/bin.js ./build/server/index.js"
```

Do not initialize the heavy Node OTel SDK from `app/entry.server.jsx`.
