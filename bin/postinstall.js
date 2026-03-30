#!/usr/bin/env node
// Runs after `npm install`. Saves partner ID to config.json if provided via:
//   PARTNER_ID=xxx npm install          (recommended)
//   npm install --partner_id=xxx        (also supported)
//
// Always prints partner attribution status so users know the current state.

import { existsSync, readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_PATH = resolve(__dirname, "..", "config.json");

const partnerId = process.env.PARTNER_ID || process.env.npm_config_partner_id;

let config = {};
if (existsSync(CONFIG_PATH)) {
  try {
    config = JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));
  } catch {}
}

if (partnerId) {
  config.PARTNER_ID = partnerId;
  writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2) + "\n");
  console.log(`[ACP] Partner ID saved: ${partnerId}`);
} else if (config.PARTNER_ID) {
  console.log(`[ACP] Partner ID (from config): ${config.PARTNER_ID}`);
} else {
  console.log("[ACP] Partner ID: not set (optional)");
}
