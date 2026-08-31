Add these entries to `tsup.config.ts`:

```ts
"observability/index": "src/observability/index.ts",
"observability/node": "src/observability/node.ts",
"observability/bullmq": "src/observability/bullmq.ts",
"observability/genai": "src/observability/genai.ts",
```

Add matching package exports for `./observability`, `./observability/node`, `./observability/bullmq`, and `./observability/genai`.
