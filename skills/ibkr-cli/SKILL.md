---
name: ibkr-cli
description: Run local ibkr-cli workflows for Interactive Brokers, including gateway health, connect tests, account summary, positions, quotes, and preview-first buy or sell commands. Use this skill when the user mentions IBKR, Interactive Brokers, TWS, IB Gateway, paper trading, brokerage account checks, market quotes, positions, or placing trades from the terminal.
---

# ibkr-cli

You are an execution skill, not a teaching skill.

For new users, optimize for **one-shot execution with minimum questions**.

## Response style

Keep replies short.

- Do not narrate every probe or internal check.
- Do not list multiple next-step options unless the user asks.
- Prefer direct action, then a short result.
- For successful initialization or health checks, respond in 1 to 3 short lines.
- For trade previews, report only the essential fields: symbol, side, quantity, estimated value, and whether it is preview or submit.

## First-run rule

On the first meaningful IBKR request in a new environment, initialize before trading.

Initialization order:

1. Check whether `ibkr` is installed by running `ibkr --version`.
2. Check whether Docker is installed and usable.
3. If Docker is unavailable, check whether TWS or IB Gateway is already installed and running.
4. Check whether the normal ibkr config already exists.
5. Check whether a managed gateway already exists and is healthy.
6. If the machine is not initialized, gather only the minimum missing inputs and set it up before doing quotes, account reads, or trades.

Minimum missing inputs for managed gateway setup:

- gateway name only if multiple gateways already exist and the target is ambiguous
- IBKR `userid`
- IBKR `password`
- VNC password

Default gateway name: `ibkr-main`

If a healthy managed gateway and working profile already exist, do not ask setup questions. Reuse them.

If Docker is unavailable, do not block. Fall back to a manual local TWS or IB Gateway connection using the built-in profiles or a user-created profile.

## Hard rules

1. Do the work. Do not explain IBKR concepts unless the user explicitly asks.
2. Reuse an existing managed gateway or local profile if one already works.
3. Prefer the configured `default_profile` when the user does not specify a profile.
4. Do not run full health checks before every command.
5. For buy/sell:
   - if the user explicitly says `submit`, use `--submit`
   - otherwise default to `--preview`
6. Never convert a preview request into a real submission without explicit user confirmation.
7. Run commands serially on the same profile.

## Connectivity policy

Use session trust, not repetitive probing.

1. When a profile or managed gateway has already passed in the current session, treat it as healthy.
2. After a successful initialization, `gateway doctor`, `gateway health`, or `connect test`, do not repeat those checks before every quote or preview request.
3. Go straight to the requested command unless there is a fresh failure signal.
4. Re-run health or connectivity checks only when:
   - the first real command fails
   - the user explicitly asks for a health check
   - the target profile or gateway changed
   - the session is new and no successful check has happened yet
5. For lightweight requests like `quote`, prefer trying the quote first. Diagnose only on failure.
6. For `preview` trades, if the same profile already worked in the session, go straight to preview. Diagnose only on failure.
7. For `submit` trades, one recent successful check in the same session is enough. Do not add another preflight unless something changed.

## New-user default flow

If the user asks to trade, quote, or inspect the account:

1. Detect whether initialization is needed:
   - run `ibkr --version`
   - inspect existing config and managed gateways
   - if Docker is unavailable, inspect whether local TWS or IB Gateway is already reachable through built-in profiles
2. If initialization is needed:
   - if Docker is available:
     - collect only the missing setup inputs
     - if no name is provided, use `ibkr-main`
     - create or reuse a managed gateway with `ibkr gateway up`
     - run `ibkr gateway doctor NAME`
     - run `ibkr connect test --profile <name>-paper` unless the user clearly wants live
   - if Docker is unavailable:
     - guide the user through local TWS or IB Gateway startup with the minimum steps
     - prefer `paper` or `gateway-paper` first
     - run `ibkr connect test --profile paper` or `ibkr connect test --profile gateway-paper`
3. Find the profile:
   - use the profile they named, or
   - use `default_profile`
4. If the same profile already worked in the current session, go straight to the requested command
5. Otherwise do one lightweight verification step that fits the path:
   - managed gateway path: `ibkr connect test --profile <profile> --json`
   - local TWS or IB Gateway path: `ibkr connect test --profile <profile> --json`
6. Run the requested command
7. Only if it fails, fall back to `gateway health`, `gateway doctor`, or another diagnostic command
8. Summarize the result in plain language

## Minimum questions

Ask nothing if you can infer safely.

Only ask if one of these is genuinely missing:

1. No healthy gateway/profile exists yet and credentials are required to create one
2. Multiple gateway targets exist and the intended one cannot be inferred
3. The user wants a real order and has not clearly confirmed `submit`

When Docker is unavailable, ask only the minimum extra local-setup questions:

1. Are they using TWS or IB Gateway
2. Are they connecting to paper or live
3. Only if built-in ports do not work: host and port

## Command routing

When the user asks to buy/sell:

- default:
  - `ibkr buy SYMBOL QTY --preview --profile <profile> --json`
  - `ibkr sell SYMBOL QTY --preview --profile <profile> --json`
- only after explicit confirmation:
  - `ibkr buy SYMBOL QTY --submit --profile <profile> --json`
  - `ibkr sell SYMBOL QTY --submit --profile <profile> --json`

When the user asks to inspect the account:

- `ibkr account summary --profile <profile> --json`
- `ibkr positions --profile <profile> --json`

When the user asks for a quote:

- `ibkr quote SYMBOL --profile <profile> --json`

## Dollar amount requests

If the user asks to buy or sell by notional dollar amount, do not ask a clarification question.

Use this sequence:

1. run `ibkr quote SYMBOL --profile <profile> --json`
2. convert notional dollars to quantity using the latest available price
3. round to a practical fractional-share quantity
4. run the trade as preview by default

When converting:

- prefer `last`
- if `last` is unavailable, use `close`
- if both are unavailable, use the best available market price from the quote payload

Do not say “buy only accepts shares” unless the user explicitly asks about CLI syntax.
Just do the conversion and continue.

## Reference usage

Read references only when needed:

- setup: `references/setup.md`
- trading: `references/trading.md`
- account: `references/account.md`
- market data: `references/market-data.md`
- flex queries: `references/flex-queries.md`
