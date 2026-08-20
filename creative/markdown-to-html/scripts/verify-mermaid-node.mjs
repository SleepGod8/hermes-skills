#!/usr/bin/env node
// 无头验证 HTML 内所有 Mermaid 块语法（jsdom 模拟浏览器环境）
// 用法: node verify-mermaid-node.mjs <html路径>
// 前置: npm install mermaid@11 jsdom --no-audit --no-fund --loglevel=error
// 注意: 只用 mermaid.parse() 验证语法 — jsdom 不实现 SVG getBBox，render() 必然失败，勿用
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { JSDOM } = require("jsdom");
const fs = require("fs");

const htmlPath = process.argv[2];
if (!htmlPath) {
  console.error("用法: node verify-mermaid-node.mjs <html路径>");
  process.exit(2);
}

const dom = new JSDOM("<!DOCTYPE html><html><body></body></html>", {
  pretendToBeVisual: true,
  url: "file:///" + htmlPath.replace(/\\/g, "/"),
});
global.window = dom.window;
global.document = dom.window.document;
// Node 22 里 global.navigator 等是只读 getter，需 defineProperty 兜底
for (const k of ["navigator", "HTMLElement", "SVGElement", "Node", "Element", "DOMParser", "XMLSerializer", "getComputedStyle", "MutationObserver", "CustomEvent", "Event", "CSSStyleSheet"]) {
  if (dom.window[k] !== undefined) {
    try { global[k] = dom.window[k]; } catch (e) {
      Object.defineProperty(global, k, { value: dom.window[k], writable: true, configurable: true });
    }
  }
}

(async () => {
  const html = fs.readFileSync(htmlPath, "utf-8");
  const blocks = [...html.matchAll(/<pre class="mermaid"[^>]*>([\s\S]*?)<\/pre>/g)];
  if (!blocks.length) {
    console.log("FAIL: 未找到 <pre class=\"mermaid\"> 块");
    process.exit(1);
  }
  const { default: mermaid } = await import("mermaid");
  await mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "dark" });
  let ok = true;
  for (let i = 0; i < blocks.length; i++) {
    // HTML 转义还原（生成 HTML 时用了 html.escape）
    const code = blocks[i][1]
      .replace(/&lt;/g, "<").replace(/&gt;/g, ">")
      .replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'");
    try {
      await mermaid.parse(code);
      console.log(`PASS: mermaid 块 #${i + 1} 语法验证通过 (${code.split("\n").length} 行)`);
    } catch (e) {
      ok = false;
      console.log(`FAIL: mermaid 块 #${i + 1}:\n${String(e).slice(0, 500)}`);
    }
  }
  process.exit(ok ? 0 : 1);
})();
