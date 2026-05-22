# Setup and Connectivity

## Preferred initialization flow

For a new machine, use this order and do not branch unless something fails:

1. Check `ibkr --version`
2. Check Docker availability
3. If Docker is unavailable, check whether TWS or IB Gateway is already installed and running
4. Check whether the ibkr config already exists
5. Check whether a managed gateway already exists
6. If not initialized and Docker is available, create one managed gateway
7. If not initialized and Docker is unavailable, use the local TWS or IB Gateway path
8. Run doctor or connect test on paper first

Ask only for the minimum missing setup values:

- gateway name
- IBKR userid
- IBKR password
- VNC password

If the user does not provide a gateway name, prefer a simple default like `main`.

If Docker is unavailable, ask only:

- TWS or IB Gateway
- paper or live
- host and port only if built-in defaults fail

## Step 1: Install ibkr-cli

The CLI requires Python 3.10+ and Docker.

Recommended installation via `pipx`:

```bash
pipx install ibkr-cli
```

Alternative via pip:

```bash
python -m pip install ibkr-cli
```

Verify it works:

```bash
ibkr --version
```

## Step 2A: Start a managed Gateway when Docker is available

This fork is **gateway-first**. The preferred path is not "install Gateway manually and edit profiles by hand". Instead, use:

```bash
ibkr gateway up ib-a --userid YOUR_IBKR_USER --password YOUR_IBKR_PASSWORD --vnc-password dev --default
```

What this does:

- Starts or creates an IB Gateway Docker container
- Forces Docker restart policy `always`
- Auto-generates two profiles:
  - `ib-a-live` -> `127.0.0.1:4001`
  - `ib-a-paper` -> `127.0.0.1:4002`
- Stores both gateway metadata and profiles in the normal ibkr config file

Inspect the managed Gateway:

```bash
ibkr gateway ps
ibkr gateway doctor ib-a
ibkr gateway logs ib-a --tail 100
```

If the user needs different ports or multiple accounts, give each Gateway a unique name and distinct ports:

```bash
ibkr gateway up ib-b --userid USER_B --password PASS_B --vnc-password dev --live-port 4011 --paper-port 4012 --vnc-port 5902
```

## Step 2B: Use local TWS or IB Gateway when Docker is unavailable

If Docker is not installed, do not block the user. Fall back to the local desktop app path:

1. Launch TWS or IB Gateway
2. Log in
3. Enable API socket access
4. Prefer paper first
5. Test the built-in profile before asking for custom ports

Built-in local profiles:

| Profile         | Port | Use case              |
|-----------------|------|-----------------------|
| `paper`         | 7497 | TWS paper trading     |
| `live`          | 7496 | TWS live trading      |
| `gateway-paper` | 4002 | IB Gateway paper      |
| `gateway-live`  | 4001 | IB Gateway live       |

Test the likely profile first:

```bash
ibkr connect test --profile paper
ibkr connect test --profile gateway-paper
```

Only if those fail should you ask for a custom host or port.

## Step 3: Verify connectivity

The CLI still supports the upstream profile system, but for this fork the preferred flow is:

1. `ibkr gateway up ...`
2. `ibkr gateway doctor NAME`
3. `ibkr connect test --profile <name>-paper` or `--profile <name>-live`

The built-in fallback profiles remain available:

| Profile         | Port | Use case              |
|-----------------|------|-----------------------|
| `paper`         | 7497 | TWS paper trading     |
| `live`          | 7496 | TWS live trading      |
| `gateway-paper` | 4002 | IB Gateway paper      |
| `gateway-live`  | 4001 | IB Gateway live       |

For managed Gateways, prefer `<name>-live` or `<name>-paper` instead of the built-in defaults.

### Run doctor

```bash
ibkr gateway doctor ib-a
ibkr connect test --profile ib-a-paper
```

This checks whether the managed container exists and is running, then validates API connectivity through the generated profile. If it fails, common causes are:

- Docker container failed to start
- Wrong credentials
- Port conflict
- Firewall blocking the port

Walk through these diagnostics one at a time rather than listing them all at once.

## Troubleshooting

When things go wrong, use `ibkr gateway doctor NAME` first, then `ibkr connect test --profile <generated-profile>`. Common issues and how to resolve them:

- **"Connection refused"**: The container is not running yet, the port is wrong, or Docker failed to bind the port
- **"No market data"**: The user's IBKR account lacks market data subscriptions for the requested instrument. The quote command will automatically try delayed data as fallback.
- **"Client ID conflict"**: Multiple CLI processes are connecting to the same Gateway/TWS simultaneously. Advise running commands one at a time against a given profile.
- **Order rejected**: Use `--preview` first to check margin and commission before submitting. The preview output often reveals why an order would fail.
