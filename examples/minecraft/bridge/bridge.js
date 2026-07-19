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
const CHANNELS = { pose: 5, vitals: 2, env: 4, blocks: 3 };

const MC_HOST = process.env.MC_HOST || "127.0.0.1";
const MC_PORT = parseInt(process.env.MC_PORT || "25565", 10);
const BOT_NAME = process.env.BOT_NAME || "pra";
const BRIDGE_PORT = parseInt(process.env.BRIDGE_PORT || "25580", 10);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const clip = (v) => Math.max(-1, Math.min(1, v));

const bot = mineflayer.createBot({ host: MC_HOST, port: MC_PORT, username: BOT_NAME });

bot.on("kicked", (reason) => console.error("kicked:", reason));
bot.on("error", (err) => console.error("bot error:", err.message));

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
  if (busy) {
    socket.write(JSON.stringify({ ok: false, error: "bridge serves one client at a time" }) + "\n");
    socket.end();
    return;
  }
  busy = true;
  console.log("client connected");
  const lines = readline.createInterface({ input: socket });
  let queue = Promise.resolve();
  lines.on("line", (line) => {
    queue = queue.then(async () => {
      let response;
      let goodbye = false;
      try {
        const message = JSON.parse(line);
        [response, goodbye] = await handle(message);
      } catch (err) {
        response = { ok: false, error: String(err.message || err) };
      }
      socket.write(JSON.stringify(response) + "\n");
      if (goodbye) socket.end();
    });
  });
  socket.on("close", () => {
    busy = false;
    clearControls();
    console.log("client disconnected");
  });
  socket.on("error", () => {});
}

async function handle(message) {
  const op = message.op;
  if (op === "hello") {
    if (message.version !== VERSION)
      return [{ ok: false, error: `protocol version mismatch: bridge speaks ${VERSION}` }, false];
    return [{ ok: true, version: VERSION, channels: CHANNELS, spawn: true }, false];
  }
  if (op === "tick") {
    for (const command of message.commands || []) await applyCommand(command);
    await sleep(Math.max(1, message.tick_ms | 0));
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

async function applyCommand(command) {
  const names = Object.keys(command);
  if (names.length === 0) return; // idle
  if (names.length > 1) throw new Error(`command carries ${names.length} keys, expected one`);
  const name = names[0];
  if (name === "forward" || name === "back") {
    bot.setControlState(name, true);
  } else if (name === "turn_left") {
    await bot.look(bot.entity.yaw + Math.PI / 4, 0, true);
  } else if (name === "turn_right") {
    await bot.look(bot.entity.yaw - Math.PI / 4, 0, true);
  } else if (name === "jump_forward") {
    bot.setControlState("forward", true);
    bot.setControlState("jump", true);
  } else if (name === "dig_ahead") {
    const block = bot.blockAt(aheadColumn());
    if (block && block.diggable && bot.canDigBlock(block)) {
      try {
        await bot.dig(block);
      } catch (err) {
        /* the world said no — the observations carry the verdict */
      }
    }
  } else if (name === "place_ahead") {
    const target = aheadColumn();
    const below = bot.blockAt(target.offset(0, -1, 0));
    const held = bot.heldItem || (await equipAnyBlock());
    if (below && held) {
      try {
        await bot.placeBlock(below, new Vec3(0, 1, 0));
      } catch (err) {
        /* nothing placeable / no reach — a world fact */
      }
    }
  } else {
    throw new Error(`unknown command '${name}'`);
  }
}

async function equipAnyBlock() {
  const item = bot.inventory.items().find((i) => i.name.includes("dirt") || i.name.includes("stone"));
  if (!item) return null;
  try {
    await bot.equip(item, "hand");
    return item;
  } catch (err) {
    return null;
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
  };
}
