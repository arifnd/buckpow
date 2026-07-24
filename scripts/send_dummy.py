import argparse
import json
import random
import time
import urllib.error
import urllib.request

FW_VERSION = "1.0.0"


def send_reading(url, device_id, energy, api_key=None):
    bus_v = round(random.uniform(4.8, 5.2), 3)
    shunt_v = round(random.uniform(75, 85), 1)
    current_ma = round(random.uniform(400, 600), 1)
    power_mw = round(bus_v * current_ma, 1)
    energy += (power_mw / 1000.0) * (1 / 3600)

    payload = json.dumps({
        "device_id": device_id,
        "firmware_version": FW_VERSION,
        "bus_voltage": bus_v,
        "shunt_voltage": shunt_v,
        "current": current_ma,
        "power": power_mw,
    }).encode()

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        resp = urllib.request.urlopen(req)
        print(f"{resp.status} {resp.read().decode()}")
    except urllib.error.HTTPError as e:
        print(f"Error: {e.code} {e.read().decode()}")
    return energy


def main():
    parser = argparse.ArgumentParser(description="Send dummy power readings to BuckPow v0.1 API")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between readings (default: 1.0)")
    parser.add_argument("--url", default="http://localhost:8000/api/v1/measurements", help="API endpoint URL")
    parser.add_argument("--device", default="esp32-dummy", help="Device ID (default: esp32-dummy)")
    parser.add_argument("--api-key", help="API key for device authentication (Bearer token)")
    parser.add_argument("--firmware", default="1.0.0", help="Firmware version to report (default: 1.0.0)")
    args = parser.parse_args()
    global FW_VERSION
    FW_VERSION = args.firmware

    if args.api_key:
        print(f"Sending dummy readings every {args.interval}s to {args.url} [device={args.device}, api_key=***]")
    else:
        print(f"Sending dummy readings every {args.interval}s to {args.url} [device={args.device}]")
    print("Press Ctrl+C to stop.\n")

    energy = 0.0
    try:
        while True:
            energy = send_reading(args.url, args.device, energy, api_key=args.api_key)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
