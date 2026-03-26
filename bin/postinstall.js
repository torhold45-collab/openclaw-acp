#!/usr/bin/env node
// Runs after `npm install`. If --partner_id was passed (e.g. npm install --partner_id xxx),
// npm exposes it as npm_config_partner_id — we save it to config.json.

import { existsSync, readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_PATH = resolve(__dirname, "..", "config.json");

const partnerId = process.env.npm_config_partner_id;
if (!partnerId) process.exit(0);

let config = {};
if (existsSync(CONFIG_PATH)) {
  try {
    config = JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));
  } catch {}
}

config.PARTNER_ID = partnerId;
writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2) + "\n");
console.log(`[ACP] Partner ID saved: ${partnerId}`);
