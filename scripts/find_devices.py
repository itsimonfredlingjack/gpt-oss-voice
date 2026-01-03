from __future__ import annotations

import sys

import pychromecast


def main() -> int:
    chromecasts, browser = pychromecast.get_chromecasts()
    try:
        if not chromecasts:
            print("No Chromecast devices found.")
            return 1

        devices = []
        for cast in chromecasts:
            info = getattr(cast, "cast_info", None)
            if info is None:
                continue
            devices.append(
                {
                    "name": info.friendly_name or "(unknown)",
                    "host": info.host,
                    "port": info.port,
                    "uuid": str(info.uuid),
                    "model": info.model_name or "",
                }
            )

        devices.sort(key=lambda d: (d["name"].lower(), d["host"]))

        print("Discovered Chromecast devices (friendly-names):\n")
        for d in devices:
            print(f"- {d['name']}  ({d['host']}:{d['port']})  {d['model']}  uuid={d['uuid']}")

        print("\nUse these exact names in env vars:")
        print("  CAST_DISPLAY_NAME=<name>")
        print("  CAST_SPEAKER_NAME=<name>")

        return 0
    finally:
        try:
            browser.stop_discovery()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())


