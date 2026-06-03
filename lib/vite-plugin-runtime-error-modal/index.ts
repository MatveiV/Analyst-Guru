import type { Plugin } from "vite";

export default function runtimeErrorOverlay(): Plugin {
  return {
    name: "runtime-error-overlay",
    transformIndexHtml() {
      return [
        {
          tag: "script",
          attrs: { type: "module" },
          children: `
window.addEventListener("error", (e) => {
  const overlay = document.createElement("div");
  overlay.id = "__runtime_error_overlay";
  overlay.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.9);color:#fff;padding:40px;font-family:monospace;z-index:99999;overflow:auto";
  overlay.innerHTML = "<h2>Runtime Error</h2><pre style='white-space:pre-wrap;color:#ff6b6b'>" + e.message + "</pre><hr><pre style='white-space:pre-wrap'>" + (e.error?.stack || "") + "</pre><button onclick='this.parentElement.remove()' style='position:fixed;top:20px;right:20px;padding:8px 20px;cursor:pointer'>Close</button>";
  document.body.appendChild(overlay);
});
window.addEventListener("unhandledrejection", (e) => {
  const overlay = document.createElement("div");
  overlay.id = "__runtime_error_overlay";
  overlay.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.9);color:#fff;padding:40px;font-family:monospace;z-index:99999;overflow:auto";
  overlay.innerHTML = "<h2>Unhandled Promise Rejection</h2><pre style='white-space:pre-wrap;color:#ff6b6b'>" + (e.reason?.message || String(e.reason)) + "</pre><button onclick='this.parentElement.remove()' style='position:fixed;top:20px;right:20px;padding:8px 20px;cursor:pointer'>Close</button>";
  document.body.appendChild(overlay);
});`,
        },
      ];
    },
  };
}
