// pra-mc/1 mineflayer bridge (features 027/030/031/033) — the live side of
// the contract in specs/027-minecraft-body/contracts/minecraft-adapter.md.
// One bot, one TCP client at a time, newline-delimited JSON. Command
// failures are world facts, not protocol errors.
//
// Feature 033 (the property body): no material classifiers anywhere — the
// channels carry properties (the game's own facts: placeability, counts)
// and appearance signatures (sha256 of the item name); digging is a held
// intention with sensed progress (start/continue on dig_ahead, released by
// any other command, 10 s no-progress safety cap); every tick also carries
// a ground-truth `view` (real item names) for the human-facing world view —
// the brain never senses it.
//
// Env: MC_HOST (127.0.0.1), MC_PORT (25565), BOT_NAME (pra), BRIDGE_PORT (25580)

"use strict";

const crypto = require("crypto");
const net = require("net");
const readline = require("readline");
const mineflayer = require("mineflayer");
const { Vec3 } = require("vec3");

const VERSION = "pra-mc/1";
const CHANNELS = { pose: 5, vitals: 2, env: 4, blocks: 3, mining: 1, pocket: 4, hand: 6, grid: 7 };
const DIG_SAFETY_MS = 10000; // the owner's cap: a dig making no progress is released

const MC_HOST = process.env.MC_HOST || "127.0.0.1";
const MC_PORT = parseInt(process.env.MC_PORT || "25565", 10);
const BOT_NAME = process.env.BOT_NAME || "pra";
const BRIDGE_PORT = parseInt(process.env.BRIDGE_PORT || "25580", 10);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const clip = (v) => Math.max(-1, Math.min(1, v));

// ---- the body's material state (names, never classes) -----------------------
let held = null; // the held kind: an item NAME (hold_next cycles pocket kinds)
let grid = []; // <=4 staged item names, column-first (virtual staging, real flows)
let digTarget = null; // Vec3 of the block being broken (the held intention)
let digStart = 0; // wall-clock ms when the intention began
let digTotalMs = 1; // the game's own break time for the target
let mcData = null; // loaded at spawn for placeability + recipes

function itemSignature(name) {
  // the contract's appearance signature: sha256 bytes 0..2 -> [-1, 1];
  // identical in the fake bridge by construction
  const d = crypto.createHash("sha256").update(name, "utf8").digest();
  return [d[0] / 127.5 - 1, d[1] / 127.5 - 1, d[2] / 127.5 - 1];
}

const isPlaceable = (name) => !!(mcData && mcData.blocksByName[name]);

function pocketItems() {
  // name -> raw count from the REAL inventory (the world is the authority)
  const counts = new Map();
  for (const item of bot.inventory.items()) {
    counts.set(item.name, (counts.get(item.name) || 0) + item.count);
  }
  return counts;
}

const stagedCount = (name) => grid.filter((n) => n === name).length;
const availableCount = (name) => Math.max(0, (pocketItems().get(name) || 0) - stagedCount(name));

function kinds() {
  return [...pocketItems().keys()].sort();
}

function resyncGrid() {
  // reservations the real inventory can no longer cover are dropped
  for (const name of new Set(grid)) {
    while (stagedCount(name) > (pocketItems().get(name) || 0)) {
      grid.splice(grid.lastIndexOf(name), 1);
    }
  }
}

function gridOffer() {
  // the world's pocket-craft rules, vanilla-exact matching (contract):
  // one log alone -> its species' planks x4; two same planks -> sticks x4
  if (grid.length === 1 && grid[0].endsWith("_log")) {
    return { name: grid[0].replace("_log", "_planks"), count: 4 };
  }
  if (grid.length === 2 && grid[0] === grid[1] && grid[0].endsWith("_planks")) {
    return { name: "stick", count: 4 };
  }
  return null;
}

function stopDig() {
  if (digTarget !== null) {
    try {
      bot.stopDigging();
    } catch (err) {
      /* already stopped */
    }
    digTarget = null;
  }
}

// ---- bot lifecycle -----------------------------------------------------------
const bot = mineflayer.createBot({ host: MC_HOST, port: MC_PORT, username: BOT_NAME });

bot.on("kicked", (reason) => console.error("kicked:", reason));
bot.on("error", (err) => console.error("bot error:", err.message));
bot.on("end", () => {
  console.error("bot disconnected from the server — restart the stack (README)");
  process.exit(1);
});
process.on("unhandledRejection", (err) => console.error("unhandled:", err && err.message));

let spawnAnchor = null;
let tick = 0;
let busy = false;

bot.once("spawn", () => {
  spawnAnchor = bot.entity.position.clone();
  mcData = require("minecraft-data")(bot.version);
  const server = net.createServer(handleClient);
  server.listen(BRIDGE_PORT, "127.0.0.1", () =>
    console.log(`pra-mc/1 bridge: bot '${BOT_NAME}' spawned, listening on 127.0.0.1:${BRIDGE_PORT}`)
  );
});

function handleClient(socket) {
  socket.on("error", () => {});
  if (busy) {
    safeWrite(socket, { ok: false, error: "bridge serves one client at a time" });
    socket.end();
    return;
  }
  busy = true;
  console.log("client connected");
  const lines = readline.createInterface({ input: socket });
  let queue = Promise.resolve();
  lines.on("line", (line) => {
    queue = queue
      .then(async () => {
        let response;
        let goodbye = false;
        try {
          const message = JSON.parse(line);
          [response, goodbye] = await handle(message);
        } catch (err) {
          response = { ok: false, error: String(err.message || err) };
        }
        safeWrite(socket, response);
        if (goodbye) socket.end();
      })
      .catch((err) => console.error("request handling error:", err.message || err));
  });
  // a vanished client must never take the bridge down (EPIPE reaches the
  // readline Interface as an 'error' event; unhandled it kills the process)
  socket.on("error", (err) => console.error("client socket error:", err.code || err.message));
  lines.on("error", (err) => console.error("client stream error:", err.code || err.message));
  socket.on("close", () => {
    busy = false;
    clearControls();
    stopDig();
    console.log("client disconnected");
  });
}

function safeWrite(socket, message) {
  if (socket.destroyed || socket.writableEnded) return;
  try {
    socket.write(JSON.stringify(message) + "\n");
  } catch (err) {
    /* the close handler frees the slot */
  }
}

async function handle(message) {
  const op = message.op;
  if (op === "hello") {
    if (message.version !== VERSION)
      return [{ ok: false, error: `protocol version mismatch: bridge speaks ${VERSION}` }, false];
    return [{ ok: true, version: VERSION, channels: CHANNELS, spawn: true }, false];
  }
  if (op === "tick") {
    const tickMs = Math.max(1, message.tick_ms | 0);
    const budget = Math.max(1000, 4 * tickMs); // bounds *quick* ops (look/place/craft)
    for (const command of message.commands || []) await applyCommand(command, budget);
    await sleep(tickMs);
    // control writes count as movement and abort a dig in progress — while
    // the intention is held there is nothing to clear (dig sets no controls)
    if (digTarget === null) clearControls();
    tick += 1;
    return [{ ok: true, tick, channels: sampleChannels(), view: sampleView() }, false];
  }
  if (op === "state") return [{ ok: true, world: { live: true, tick } }, false];
  if (op === "load_state") {
    // a live world restores nothing but the tick counter — Doc 06 §5b class 4
    tick = (message.world && message.world.tick) | 0;
    return [{ ok: true }, false];
  }
  if (op === "bye") return [{ ok: true }, true];
  return [{ ok: false, error: `unknown op ${JSON.stringify(op)}` }, false];
}

function aheadColumn() {
  const p = bot.entity.position;
  const yaw = bot.entity.yaw;
  return new Vec3(Math.round(p.x - Math.sin(yaw)), Math.floor(p.y), Math.round(p.z + Math.cos(yaw)));
}

function bounded(promise, ms, onTimeout) {
  const guarded = promise.catch(() => {});
  return Promise.race([
    guarded,
    sleep(ms).then(() => {
      if (onTimeout) onTimeout();
    }),
  ]);
}

async function applyCommand(command, budget) {
  const names = Object.keys(command);
  const name = names.length === 0 ? null : names[0];
  if (names.length > 1) throw new Error(`command carries ${names.length} keys, expected one`);
  if (name !== "dig_ahead") stopDig(); // releasing the intention (idle included)
  if (name === null) return; // idle
  if (name === "forward" || name === "back") {
    bot.setControlState(name, true);
  } else if (name === "turn_left") {
    await bounded(bot.look(bot.entity.yaw + Math.PI / 4, 0, true), 500);
  } else if (name === "turn_right") {
    await bounded(bot.look(bot.entity.yaw - Math.PI / 4, 0, true), 500);
  } else if (name === "jump_forward") {
    bot.setControlState("forward", true);
    bot.setControlState("jump", true);
  } else if (name === "dig_ahead") {
    const target = aheadColumn();
    const block = bot.blockAt(target);
    if (!block || !block.diggable || !bot.canDigBlock(block)) {
      stopDig();
      return;
    }
    if (digTarget !== null && digTarget.equals(target)) {
      // continuing the held intention; the safety cap is the only bound
      if (Date.now() - digStart > DIG_SAFETY_MS) stopDig();
      return;
    }
    stopDig();
    digTarget = target.clone();
    digStart = Date.now();
    digTotalMs = Math.max(1, bot.digTime(block));
    // NOT awaited: the dig runs across ticks while the brain keeps sensing;
    // forceLook 'ignore' — a mid-dig look counts as movement and aborts the
    // dig (measured live: forceLook=true self-aborted at one tick)
    bot
      .dig(block, "ignore")
      .then(() => {
        digTarget = null; // broken — the drop lands by the game's own physics
      })
      .catch((err) => {
        console.error("dig ended early:", err && err.message, "after", Date.now() - digStart, "ms");
        digTarget = null;
      });
  } else if (name === "place_ahead") {
    const target = aheadColumn();
    const below = bot.blockAt(target.offset(0, -1, 0));
    if (below && held !== null && isPlaceable(held) && availableCount(held) > 0) {
      const item = bot.inventory.items().find((i) => i.name === held);
      if (item) {
        await bounded(bot.equip(item, "hand"), budget);
        await bounded(bot.placeBlock(below, new Vec3(0, 1, 0)), budget);
      }
    }
  } else if (name === "hold_next") {
    const cycle = [null, ...kinds()];
    const index = cycle.findIndex((n) => n === held);
    held = cycle[((index < 0 ? 0 : index) + 1) % cycle.length];
  } else if (name === "grid_put") {
    if (held !== null && grid.length < 4 && availableCount(held) > 0) {
      grid.push(held);
    }
  } else if (name === "grid_take") {
    grid = [];
  } else if (name === "take_result") {
    const offer = gridOffer();
    if (offer !== null && mcData) {
      const target = mcData.itemsByName[offer.name];
      if (target) {
        const before = pocketItems().get(offer.name) || 0;
        const recipe = bot.recipesFor(target.id, null, 1, null)[0];
        if (recipe) await bounded(bot.craft(recipe, 1, null), budget);
        if ((pocketItems().get(offer.name) || 0) > before) grid = []; // world-confirmed
      }
    }
    resyncGrid();
  } else {
    throw new Error(`unknown command '${name}'`);
  }
}

function clearControls() {
  for (const control of ["forward", "back", "jump"]) bot.setControlState(control, false);
}

function sampleChannels() {
  const p = bot.entity.position;
  const yaw = bot.entity.yaw;
  const theta = 2 * Math.PI * ((bot.time.timeOfDay % 24000) / 24000);
  const feet = new Vec3(Math.floor(p.x), Math.floor(p.y), Math.floor(p.z));
  const ahead = aheadColumn();
  const solid = (block) => (block && block.boundingBox === "block" ? 1 : 0);
  const feetBlock = bot.blockAt(feet);
  const light = feetBlock && feetBlock.light !== undefined ? feetBlock.light : 15;
  const norm = (n) => Math.min(n, 64) / 64;

  const counts = pocketItems();
  let total = 0;
  let placeableTotal = 0;
  for (const [name, count] of counts) {
    const available = Math.max(0, count - stagedCount(name));
    total += available;
    if (isPlaceable(name)) placeableTotal += available;
  }
  const kindList = kinds();

  const heldAvailable = held === null ? 0 : availableCount(held);
  const hand =
    held !== null && heldAvailable > 0
      ? [1, isPlaceable(held) ? 1 : 0, norm(heldAvailable), ...itemSignature(held)]
      : [0, 0, 0, 0, 0, 0];

  const offer = gridOffer();
  const gridChannel =
    offer !== null
      ? [grid.length / 4, 1, isPlaceable(offer.name) ? 1 : 0, norm(offer.count), ...itemSignature(offer.name)]
      : [grid.length / 4, 0, 0, 0, 0, 0, 0];

  const mining =
    digTarget !== null ? [Math.min((Date.now() - digStart) / digTotalMs, 1)] : [0];

  return {
    pose: [
      clip((p.x - spawnAnchor.x) / 64),
      clip((p.z - spawnAnchor.z) / 64),
      clip((p.y - 64) / 64),
      Math.sin(yaw),
      Math.cos(yaw),
    ],
    vitals: [bot.health / 20, bot.food / 20],
    env: [light / 15, Math.sin(theta), Math.cos(theta), bot.isRaining ? 1 : 0],
    blocks: [
      solid(bot.blockAt(ahead)),
      solid(bot.blockAt(ahead.offset(0, 1, 0))),
      bot.blockAt(ahead.offset(0, -1, 0)) && bot.blockAt(ahead.offset(0, -1, 0)).boundingBox === "empty" ? 1 : 0,
    ],
    mining,
    pocket: [norm(total), Math.min(kindList.length, 9) / 9, norm(placeableTotal), norm(total - placeableTotal)],
    hand,
    grid: gridChannel,
  };
}

function sampleView() {
  // ground truth for humans (feature 033): real names, never sensed
  const p = bot.entity.position;
  const inventory = [...pocketItems().entries()].sort().map(([n, c]) => [n, c]);
  return {
    pos: [Math.round(p.x * 10) / 10, Math.round(p.y * 10) / 10, Math.round(p.z * 10) / 10],
    held,
    inventory,
    digging: digTarget !== null ? Math.min((Date.now() - digStart) / digTotalMs, 1) : 0,
    // server game-tick clock (feature: fast-real-bridge calibration) —
    // lets the harness measure achieved TPS and game-ticks-per-brain-step
    age: bot.time.age,
  };
}
