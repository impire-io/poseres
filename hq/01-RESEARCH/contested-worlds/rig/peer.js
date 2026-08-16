// The scripted peer "rook" (contested-worlds rung 1) — a second BODY,
// not a brain, in one of two fixed, non-adaptive configurations:
//
//   PEER_MODE=forager (default) — the commensal control measured
//   2026-08-16: cycle the three melon patches, dig the nearest melon,
//   walk over drops near itself.
//
//   PEER_MODE=hostile (Amendment 1) — deliberate contention: shadow
//   the subject, take drops NEAR THE SUBJECT, dig the melon nearest
//   the subject. Same escape ladder, same logging.
//
// It issues no admin command and reads nothing of the subject's
// internals (the shadow reads the subject's world-visible avatar
// position — a world fact any body can see); it perturbs the shared
// world only through real acts, and every act is one JSONL line so
// the perturbation stream is on the record. No pathfinder exists in
// the rig's node_modules, so navigation is straight-line walking with
// a fixed escape ladder (stuck -> jump; still stuck -> veer 60
// degrees alternating; objective timeout -> abandon + blacklist).
"use strict";

const path = require("path");
const NM = path.join(__dirname, "..", "..", "..", "..", "examples", "minecraft", "bridge", "node_modules");
const mineflayer = require(path.join(NM, "mineflayer"));
const { Vec3 } = require(path.join(NM, "vec3"));

const MC_PORT = parseInt(process.env.MC_PORT || "25603", 10);
const NAME = process.env.PEER_NAME || "rook";
const MODE = process.env.PEER_MODE || "forager";
const SUBJECT = process.env.SUBJECT_NAME || "pra";
const PATCHES = [
  [5, 5],
  [28, 0],
  [0, 28],
];
const TICK_MS = 250;
const DROP_TIMEOUT_MS = 6000;
const TRAVEL_TIMEOUT_MS = 20000;
const MELON_TIMEOUT_MS = 15000;
const BLACKLIST_MS = 30000;

function log(ev, extra) {
  console.log(JSON.stringify({ t: Date.now(), ev, ...(extra || {}) }));
}

const bot = mineflayer.createBot({ host: "127.0.0.1", port: MC_PORT, username: NAME });

let patchIdx = 0;
let busy = false;
let lastPos = null;
let stuckTicks = 0;
let stuckJumps = 0;
let veerUntil = 0;
let veerSign = 1;
let objective = null; // {kind, key, since}
const blacklist = new Map(); // key -> until (ms)

function dist2d(a, b) {
  const dx = a.x - b.x;
  const dz = a.z - b.z;
  return Math.sqrt(dx * dx + dz * dz);
}

function blacklisted(key) {
  const until = blacklist.get(key);
  if (until === undefined) return false;
  if (Date.now() > until) {
    blacklist.delete(key);
    return false;
  }
  return true;
}

function setObjective(kind, key) {
  if (!objective || objective.kind !== kind || objective.key !== key) {
    objective = { kind, key, since: Date.now() };
    stuckJumps = 0;
  }
}

function abandon(reason) {
  if (objective && (objective.kind === "drop" || objective.kind === "melon"))
    blacklist.set(objective.key, Date.now() + BLACKLIST_MS);
  log("abandon", { objective, reason });
  objective = null;
  stuckJumps = 0;
  veerUntil = 0;
}

function patchCenter() {
  const [x, z] = PATCHES[patchIdx];
  return new Vec3(x + 0.5, -60, z + 0.5);
}

function subjectPos() {
  const p = bot.players[SUBJECT];
  return p && p.entity ? p.entity.position : null;
}

function rotatedAim(target) {
  const pos = bot.entity.position;
  const dx = target.x - pos.x;
  const dz = target.z - pos.z;
  const a = (veerSign * 60 * Math.PI) / 180;
  return new Vec3(
    pos.x + dx * Math.cos(a) - dz * Math.sin(a),
    target.y,
    pos.z + dx * Math.sin(a) + dz * Math.cos(a)
  );
}

async function walkToward(target) {
  const aim = Date.now() < veerUntil ? rotatedAim(target) : target;
  busy = true;
  try {
    await bot.lookAt(new Vec3(aim.x, bot.entity.position.y + 1.6, aim.z), true);
  } finally {
    busy = false;
  }
  bot.setControlState("forward", true);
}

function stuckWatch() {
  const pos = bot.entity.position;
  if (lastPos && dist2d(pos, lastPos) < 0.03 && bot.getControlState("forward")) {
    stuckTicks += 1;
  } else {
    stuckTicks = 0;
  }
  lastPos = pos.clone();
  if (stuckTicks >= 6) {
    stuckTicks = 0;
    stuckJumps += 1;
    if (stuckJumps >= 6) {
      abandon("stuck");
      if (MODE === "forager") {
        patchIdx = (patchIdx + 1) % PATCHES.length;
        log("patch-skip", { next: patchIdx });
      }
      return;
    }
    if (stuckJumps >= 2) {
      veerSign = -veerSign;
      veerUntil = Date.now() + 1200;
      log("veer", { sign: veerSign, pos });
    }
    bot.setControlState("jump", true);
    setTimeout(() => bot.setControlState("jump", false), 300);
    log("stuck-jump", { pos, jumps: stuckJumps });
  }
}

async function chaseDrop(drop) {
  setObjective("drop", String(drop.id));
  if (Date.now() - objective.since > DROP_TIMEOUT_MS) {
    abandon("drop-timeout");
    return;
  }
  await walkToward(drop.position);
}

async function digMelon(melon) {
  busy = true;
  try {
    log("dig", { at: melon.position });
    await bot.lookAt(melon.position.offset(0.5, 0.5, 0.5), true);
    await bot.dig(bot.blockAt(melon.position));
    log("dug", { at: melon.position });
  } catch (e) {
    blacklist.set(`m${melon.position}`, Date.now() + BLACKLIST_MS);
    log("dig-fail", { e: String(e) });
  } finally {
    busy = false;
  }
}

async function foragerStep(pos) {
  // priority 1: a ground item within 8 of SELF — walk over it
  const drop = bot.nearestEntity(
    (e) => e.name === "item" && dist2d(e.position, pos) < 8 && !blacklisted(String(e.id))
  );
  if (drop) {
    await chaseDrop(drop);
    return;
  }
  if (objective && objective.kind === "drop") objective = null;

  // priority 2: travel to the current patch
  const center = patchCenter();
  if (dist2d(pos, center) > 2.5) {
    setObjective("travel", String(patchIdx));
    if (Date.now() - objective.since > TRAVEL_TIMEOUT_MS) {
      abandon("travel-timeout");
      patchIdx = (patchIdx + 1) % PATCHES.length;
      log("patch-skip", { next: patchIdx });
      return;
    }
    await walkToward(center);
    return;
  }
  bot.setControlState("forward", false);
  objective = null;

  // priority 3: dig the patch's nearest melon; empty -> next patch
  const melon = bot.findBlock({
    point: center,
    maxDistance: 5,
    matching: (b) => b && b.name === "melon" && !blacklisted(`m${b.position ?? ""}`),
  });
  if (!melon) {
    patchIdx = (patchIdx + 1) % PATCHES.length;
    log("patch-empty", { next: patchIdx });
    return;
  }
  await digMelon(melon);
}

async function hostileStep(pos) {
  const s = subjectPos();
  if (!s) {
    // subject not in view yet: hold at the spawn patch
    if (objective === null || objective.kind !== "no-subject") {
      setObjective("no-subject", "");
      log("no-subject", {});
    }
    if (dist2d(pos, patchCenter()) > 2.5) await walkToward(patchCenter());
    else bot.setControlState("forward", false);
    return;
  }

  // priority 1: a drop near the SUBJECT — take it before they do
  const drop = bot.nearestEntity(
    (e) => e.name === "item" && dist2d(e.position, s) < 10 && !blacklisted(String(e.id))
  );
  if (drop) {
    await chaseDrop(drop);
    return;
  }
  if (objective && objective.kind === "drop") objective = null;

  // priority 2: the melon nearest the subject — contend for it
  const melon = bot.findBlock({
    point: s,
    maxDistance: 24,
    matching: (b) => b && b.name === "melon" && !blacklisted(`m${b.position ?? ""}`),
  });
  if (melon) {
    setObjective("melon", `m${melon.position}`);
    if (Date.now() - objective.since > MELON_TIMEOUT_MS) {
      abandon("melon-timeout");
      return;
    }
    if (dist2d(pos, melon.position) > 2.8) {
      await walkToward(new Vec3(melon.position.x + 0.5, -60, melon.position.z + 0.5));
      return;
    }
    bot.setControlState("forward", false);
    await digMelon(melon);
    objective = null;
    return;
  }
  if (objective && objective.kind === "melon") objective = null;

  // priority 3: shadow the subject at close range
  if (dist2d(pos, s) > 4) {
    setObjective("shadow", "");
    if (Date.now() - objective.since > TRAVEL_TIMEOUT_MS) abandon("shadow-timeout");
    await walkToward(s);
    return;
  }
  bot.setControlState("forward", false);
  objective = null;
}

async function step() {
  if (busy || !bot.entity) return;
  stuckWatch();
  const pos = bot.entity.position;
  if (MODE === "hostile") await hostileStep(pos);
  else await foragerStep(pos);
}

bot.once("spawn", () => {
  log("spawn", { pos: bot.entity.position, name: NAME, mode: MODE });
  setInterval(() => {
    step().catch((e) => log("step-error", { e: String(e) }));
  }, TICK_MS);
});
bot.on("kicked", (r) => {
  log("kicked", { r: String(r) });
  process.exit(1);
});
bot.on("error", (e) => log("error", { e: String(e) }));
bot.on("death", () => log("death", { pos: bot.entity && bot.entity.position }));
