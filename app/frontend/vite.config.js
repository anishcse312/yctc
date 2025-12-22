import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  base: "/",
  build: {
    outDir: path.resolve(__dirname, "../public/vite"),
    emptyOutDir: true,
  },
  server: {
    proxy: {
      "^/(api|admin-login|admin-register|forgot|otp|set-new-password|logout|search|update-profile|update-profile-picture)":
        "http://localhost:5000",
    },
  },
});
