# Quickstart: The Builder's Body (feature 030)

## The gate (no broker, no Minecraft)

```bash
./.venv/bin/ruff format --check . && ./.venv/bin/ruff check . && ./.venv/bin/pytest -q
```

The FakeBridge carries everything: the amended contract semantics, the
full material chain, byte-identity + exact resume with inventory in the
state seam, and the 19/10 anatomy metadata.

## The pilot (pre-registered, spec FR-008)

Run by the implementer once, in the session scratchpad; numbers land in
the journey episode. 8 paired seeds, engine over FakeBridge,
`crafting=True` vs `crafting=False`, short budget.

## See it live

```bash
cd examples/minecraft && ./up.sh      # the brain now boots the 19/10 body
```

The Brain tab shows the `inventory` group and the craft actions
automatically (feature 029's metadata path — zero dashboard changes).
To watch the material loop by hand: spectate, and give the bot wood
(`docker compose exec minecraft rcon-cli "give pra oak_log 8"`) — the
inventory channels move within a tick, and a `craft_planks` choice
becomes visible in the anatomy view's action highlight.

Note: any pre-030 `c1-snapshots/` will refuse to resume into the 19-dim
config (loud config check). Start the long run fresh — or run the
legacy body with the anatomy flag if reverting (spec, Assumptions).
