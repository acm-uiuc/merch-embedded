import traceback
from flask import Flask, request
import json
import signal
import sys
import configparser

import requests
from vend import Merch
from urllib.parse import urljoin

config = configparser.ConfigParser()
config.read("config.ini")
token = config.get("DEFAULT", "TOKEN", fallback=None)
coinmarketcap_key = config.get("DEFAULT", "COINMARKETCAP_KEY", fallback=None)
dev_mode = config.get("DEFAULT", "DEV_MODE", fallback="no")

app = Flask(__name__)


@app.route("/api", methods=["GET"])
def api():
    return "MERCH API RUNNING"


@app.route("/api/vend", methods=["POST"])
def vend():
    try:
        merch = Merch()
        if "item" not in request.args:
            return (
                json.dumps({"error": 'missing query parameter "item"'}),
                400,
                {"ContentType": "application/json"},
            )
        item = request.args["item"]
        listings = requests.get(urljoin(config.get("CORE_API_URL"), "/items")).json()[
            "items"
        ]
        our_listing = None
        for listing in listings:
            if listing["id"] == item:
                our_listing = listing
        if not our_listing:
            return (
                json.dumps({"error": "Item ID was not found."}),
                400,
                {"ContentType": "application/json"},
            )
        for slot in item["slots"]:
            # try to vend all slots we could have the item in.
            if merch.vend(slot[0], int(slot[1])):
                return (
                    json.dumps({"success": True}),
                    200,
                    {"ContentType": "application/json"},
                )
    except Exception:
        print(f"Failed to vend: {traceback.format_exc()}")
        return (
            json.dumps({"error": "failed to vend"}),
            500,
            {"ContentType": "application/json"},
        )


def signal_handler(signal, frame):
    # merch.cleanup()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    app.run(debug=True, host="0.0.0.0")
