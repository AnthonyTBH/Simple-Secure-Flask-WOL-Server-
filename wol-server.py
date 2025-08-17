from flask import Flask, request, jsonify
import logging
import socket
import struct
import os

app = Flask(__name__)

# ✅ Configuration
SECRET_PASSWORD = os.environ.get("WOL_PASSWORD", "changeme")  # use env var or default
BIND_HOST = "0.0.0.0"   # listen on all interfaces
BIND_PORT = 5000        # change if needed

# ✅ Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def send_wol(mac_address: str) -> None:
    """
    Send a Wake-on-LAN magic packet to the given MAC address.
    """
    # Clean MAC string (AA:BB:CC:DD:EE:FF → aabbccddeeff)
    mac_address = mac_address.replace(":", "").replace("-", "").lower()

    if len(mac_address) != 12:
        raise ValueError("Invalid MAC address format")

    # Magic packet = 6x FF + 16 repetitions of MAC
    data = b"\xff" * 6 + bytes.fromhex(mac_address) * 16

    # Send as broadcast UDP packet
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data, ("<broadcast>", 9))  # port 9 is standard WOL
    logging.info(f"Magic packet sent to {mac_address}")


@app.route("/wake", methods=["POST"])
def wake_device():
    """
    API endpoint to trigger WOL.
    Requires JSON body: { "password": "...", "mac": "AA:BB:CC:DD:EE:FF" }
    """
    try:
        data = request.get_json(force=True)
        password = data.get("password")
        mac = data.get("mac")

        if not password or not mac:
            return jsonify({"error": "Missing fields (password, mac required)"}), 400

        if password != SECRET_PASSWORD:
            return jsonify({"error": "Unauthorized"}), 401

        send_wol(mac)
        return jsonify({"status": "success", "message": f"WOL sent to {mac}"}), 200

    except ValueError as ve:
        logging.error(f"Value error: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logging.exception("Unexpected error")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    logging.info(f"Starting WOL server on {BIND_HOST}:{BIND_PORT}")
    app.run(host=BIND_HOST, port=BIND_PORT)
