import { rmSync } from "node:fs";
import resolve from "@rollup/plugin-node-resolve";
import terser from "@rollup/plugin-terser";
import typescript from "@rollup/plugin-typescript";

// The integration serves this folder as /maico_kwl/frontend. The loader keeps
// its name (it is what the integration registers); the card chunk is named by
// its content, so browsers never run a stale copy.
const OUT_DIR = "../custom_components/maico_kwl/frontend";

const clean = () => ({
  name: "clean",
  buildStart() {
    rmSync(OUT_DIR, { recursive: true, force: true });
  },
});

export default {
  input: { "maico-kwl-card": "src/loader.ts" },
  output: {
    dir: OUT_DIR,
    format: "es",
    entryFileNames: "[name].js",
    chunkFileNames: "[name]-[hash].js",
  },
  plugins: [clean(), resolve(), typescript(), terser({ keep_classnames: true, format: { comments: false } })],
};
