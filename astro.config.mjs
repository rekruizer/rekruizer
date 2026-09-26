import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://denisyuce.com",
  output: "static",
  trailingSlash: "always",
  build: {
    format: "directory",
  },
});
