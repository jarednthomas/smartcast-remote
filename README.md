# SmartCast Remote

A self-hosted web remote for Vizio SmartCast TVs. Runs a small Python server that proxies key presses and app launches to your TV's local SmartCast API, with a mobile-friendly on-screen remote.

## Requirements

- Python 3.10+
- A Vizio SmartCast TV on the same network
- Your TV's auth token (see [Getting your auth token](#getting-your-auth-token))

```bash
pip install -r requirements.txt
```

## Configuration

The app reads its settings from environment variables:

| Variable      | Required | Default | Description                        |
|---------------|----------|---------|-------------------------------------|
| `TV_IP`       | Yes      | —       | Your TV's local IP address          |
| `VIZIO_AUTH`  | Yes      | —       | Auth token from pairing with the TV |
| `PORT`        | No       | `8100`  | Port the web server listens on      |

### Option A: export variables

```bash
export TV_IP=192.168.0.x
export VIZIO_AUTH=your-auth-token
```

### Option B: `.env` file

Create a `.env` file in the project root (this is gitignored, never commit it):

```
TV_IP=192.168.0.x
VIZIO_AUTH=your-auth-token
PORT=8100
```


## Run

```bash
python remote.py
```

Then open `http://localhost:8100` in a browser. To use it from your phone, find your computer's LAN IP (e.g. `192.168.0.x`) and open `http://<that-ip>:8100` on your phone, same wifi network required.

## Docker

### Build and run

```bash
docker build -t smartcast-remote .
docker run -d --name smartcast-remote \
  -p 8100:8100 \
  --env-file .env \
  --restart unless-stopped \
  smartcast-remote
```

### Or with Docker Compose

```bash
docker compose up -d --build
```

Compose reads `.env` automatically from the project root.

View logs:

```bash
docker logs -f smartcast-remote
```

## Getting your auth token

1. Put the TV in pairing mode via its SmartCast settings, or use a pairing script against `https://<TV_IP>:7345/pairing/start`.
2. Follow the standard Vizio SmartCast pairing flow to retrieve your `AUTH` token.
3. Set it as `VIZIO_AUTH` above.

## Notes

- All TV communication uses HTTPS with a self-signed cert, so requests disable certificate verification. This is expected for local SmartCast devices.
- Tested on Vizio SmartCast TVs over the local port `7345`. Key and app codes may vary slightly by firmware.