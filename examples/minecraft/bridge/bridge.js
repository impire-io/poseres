// pra-mc/1 mineflayer bridge (feature 027) — the live side of the contract in
// specs/027-minecraft-body/contracts/minecraft-adapter.md. One bot, one TCP
// client at a time, newline-delimited JSON. Command failures (an undigable
// block, nothing to place) are world facts, not protocol errors: the action
// no-ops and the brain reads the consequences in its observations.
//
// Env: MC_HOST (127.0.0.1), MC_PORT (25565), BOT_NAME (pra), BRIDGE_PORT (25580)

"use strict";

const net = require("net");
const readline = require("readline");
const mineflayer = require("mineflayer");
const { Vec3 } = require("vec3");

const VERSION = "pra-mc/1";
const CHANNELS = { pose: 5, vitals: 2, env: 4, blocks: 3, inventory: 5, hand: 4, grid: 5 };

// feature 031: the held class and the 2x2 staging grid — body furniture
// (contract-declared): virtual staging over the REAL inventory, real craft
// at take_result, the world always the authority on counts.
const HOLD_CYCLE = [null, "blocks", "logs", "planks", "sticks"];
let held = null;
let grid = []; // <=4 class names, column-first; first two are column-adjacent

const MC_HOST = process.env.MC_HOST || "127.0.0.1";
const MC_PORT = parseInt(process.env.MC_PORT || "25565", 10);
const BOT_NAME = process.env.BOT_NAME || "pra";
const BRIDGE_PORT = parseInt(process.env.BRIDGE_PORT || "25580", 10);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const clip = (v) => Math.max(-1, Math.min(1, v));

const bot = mineflayer.createBot({ host: MC_HOST, port: MC_PORT, username: BOT_NAME });

bot.on("kicked", (reason) => console.error("kicked:", reason));
bot.on("error", (err) => console.error("bot error:", err.message));
bot.on("end", () => {
  console.error("bot disconnected from the server — restart the stack (README)");
  process.exit(1);
});
// a weeks-long bridge logs unforeseen failures instead of dying of them;
// per-request errors still reach the client as ok:false responses.
process.on("unhandledRejection", (err) => console.error("unhandled:", err && err.message));

let spawnAnchor = null;
let tick = 0;
let busy = false;

bot.once("spawn", () => {
  spawnAnchor = bot.entity.position.clone();
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
  socket.on("close", () => {
    busy = false;
    clearControls();
    console.log("client disconnected");
  });
}

function safeWrite(socket, message) {
  // the client may have vanished mid-request (a killed brain): a write to a
  // dead socket must never take the bridge down with it.
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
    // every world action is bounded by the tick's own timescale: a dig that
    // needs longer than the budget is abandoned mid-swing (stopDigging), a
    // hung placeBlock is dropped — world facts, never protocol stalls.
    const budget = Math.max(1000, 4 * tickMs);
    for (const command of message.commands || []) await applyCommand(command, budget);
    await sleep(tickMs);
    clearControls();
    tick += 1;
    return [{ ok: true, tick, channels: sampleChannels() }, false];
  }
  if (op === "state") return [{ ok: true, world: { live: true, tick } }, false];
  if (op === "load_state") {
    // a live world restores nothing but the tick counter — Doc 06 §5b class 4,
    // stated: the brain resumes exactly, the world resumes wherever it is.
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
  // never let a world action outlive its budget; late failures are swallowed
  // (the observations carry the verdict), late successes simply land.
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
  if (names.length === 0) return; // idle
  if (names.length > 1) throw new Error(`command carries ${names.length} keys, expected one`);
  const name = names[0];
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
    const block = bot.blockAt(aheadColumn());
    if (block && block.diggable && bot.canDigBlock(block)) {
      await bounded(bot.dig(block), budget, () => {
        try {
          bot.stopDigging();
        } catch (err) {
          /* already stopped */
        }
      });
    }
  } else if (name === "place_ahead") {
    // feature 031: held-based — selection is the brain's; blocks and planks
    // are the placeable classes
    const target = aheadColumn();
    const below = bot.blockAt(target.offset(0, -1, 0));
    if (below && (held === "blocks" || held === "planks")) {
      const equipped = await equipHeld(budget);
      if (equipped) await bounded(bot.placeBlock(below, new Vec3(0, 1, 0)), budget);
    }
  } else if (name === "hold_next") {
    held = HOLD_CYCLE[(HOLD_CYCLE.indexOf(held) + 1) % HOLD_CYCLE.length];
  } else if (name === "grid_put") {
    if (held && grid.length < 4 && rawCount(held) - stagedCount(held) > 0) {
      grid.push(held);
    }
  } else if (name === "grid_take") {
    grid = [];
  } else if (name === "take_result") {
    const offer = gridOffer();
    if (offer === "planks") {
      const log = bot.inventory.items().find((i) => isLogItem(i.name));
      if (log) {
        const before = rawCount("planks");
        await craftByName(log.name.replace("_log", "_planks"), budget);
        if (rawCount("planks") > before) grid = []; // the world confirms
      }
    } else if (offer === "sticks") {
      const before = rawCount("sticks");
      await craftByName("stick", budget);
      if (rawCount("sticks") > before) grid = [];
    }
    resyncGrid();
  } else {
    throw new Error(`unknown command '${name}'`);
  }
}

const CLASS_TESTS = {
  blocks: isBlockItem,
  logs: isLogItem,
  planks: isPlankItem,
  sticks: (n) => n === "stick",
};

function rawCount(cls) {
  let n = 0;
  for (const item of bot.inventory.items()) if (CLASS_TESTS[cls](item.name)) n += item.count;
  return n;
}

function stagedCount(cls) {
  return grid.filter((c) => c === cls).length;
}

function resyncGrid() {
  // the world is the authority: reservations the real inventory can no
  // longer cover are dropped (newest first)
  for (const cls of Object.keys(CLASS_TESTS)) {
    while (stagedCount(cls) > rawCount(cls)) {
      grid.splice(grid.lastIndexOf(cls), 1);
    }
  }
}

function gridOffer() {
  // vanilla-exact: contents must match the recipe exactly
  if (grid.length === 1 && grid[0] === "logs") return "planks";
  if (grid.length === 2 && grid[0] === "planks" && grid[1] === "planks") return "sticks";
  return null;
}

async function equipHeld(budget) {
  const item = bot.inventory.items().find((i) => CLASS_TESTS[held](i.name));
  if (!item) return null;
  await bounded(bot.equip(item, "hand"), budget);
  return bot.heldItem;
}

async function craftByName(itemName, budget) {
  // pocket (2x2) recipes only — no crafting table; an unmet or timed-out
  // craft is a world fact, exactly like an undigable block.
  const mcData = require("minecraft-data")(bot.version);
  const item = mcData.itemsByName[itemName];
  if (!item) return;
  const recipe = bot.recipesFor(item.id, null, 1, null)[0];
  if (!recipe) return;
  await bounded(bot.craft(recipe, 1, null), budget);
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
    inventory: sampleInventory(),
    hand: [
      held === "blocks" ? 1 : 0,
      held === "logs" ? 1 : 0,
      held === "planks" ? 1 : 0,
      held === "sticks" ? 1 : 0,
    ],
    grid: [
      grid.length / 4,
      stagedCount("logs") / 4,
      stagedCount("planks") / 4,
      gridOffer() === "planks" ? 1 : 0,
      gridOffer() === "sticks" ? 1 : 0,
    ],
  };
}

// features 030/031: the pocket, read fresh every tick — the contract's four
// material classes (items outside them are not counted); staged reservations
// are subtracted so pocket + grid always sum to the real inventory.
const isBlockItem = (n) => n.includes("dirt") || n.includes("stone");
const isLogItem = (n) => n.endsWith("_log");
const isPlankItem = (n) => n.endsWith("_planks");

function sampleInventory() {
  const pocket = (cls) => Math.max(0, rawCount(cls) - stagedCount(cls));
  const norm = (n) => Math.min(n, 64) / 64;
  return [
    norm(pocket("blocks")),
    norm(pocket("logs")),
    norm(pocket("planks")),
    norm(pocket("sticks")),
    held === "blocks" || held === "planks" ? 1 : 0,
  ];
}
