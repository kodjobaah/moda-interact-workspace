import { defineConfig } from "tsup";

export default defineConfig({
  entry: {
    index: "src/index.ts",
    "shopify/index": "src/shopify/index.ts",
    "shopify/node": "src/shopify/node.ts",
    "logging/index": "src/logging/index.ts",
    "logging/node": "src/logging/node.ts",
  },
  format: ["esm"],
  dts: true,
  clean: true,
  sourcemap: true,
});
