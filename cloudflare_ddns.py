import json
import requests
import os
import sys
import time

CONFIG_FILE = "config.json"
IP_CHECK_URL = "https://api.ipify.org"
LIST_RECORDS_URL = "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={record_name}"
UPDATE_RECORD_URL = "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
REQUEST_TIMEOUT = 5  # seconds
LOG_FILE = "ddns.log"


def log(message):
    """Append timestamped message to log file."""
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} {message}\n")


def load_config():
    """Load configuration from config.json."""
    if not os.path.exists(CONFIG_FILE):
        log("Missing config.json")
        sys.exit(1)
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_current_ip():
    """Get the current public IP address."""
    try:
        response = requests.get(IP_CHECK_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as error:
        log(f"Error fetching public IP: {error}")
        return None


def get_record_id(config):
    """Retrieve the DNS record ID for the given record name."""
    url = LIST_RECORDS_URL.format(
        zone_id=config["zone_id"],
        record_name=config["record_name"]
    )
    headers = {
        "Authorization": f"Bearer {config['api_token']}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        records = response.json().get("result", [])
        if not records:
            log("DNS record not found")
            return None
        return records[0]["id"]
    except requests.RequestException as error:
        log(f"Error fetching record ID: {error}")
        return None


def update_dns_record(config, record_id, current_ip):
    """Update the DNS A record with the new IP."""
    url = UPDATE_RECORD_URL.format(
        zone_id=config["zone_id"],
        record_id=record_id
    )
    headers = {
        "Authorization": f"Bearer {config['api_token']}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": config["record_name"],
        "content": current_ip,
        "ttl": 120,
        "proxied": False
    }

    try:
        response = requests.put(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        log(f"Successfully updated DNS to {current_ip}")
    except requests.RequestException as error:
        log(f"Failed to update DNS: {error}")


def main():
    """Main script entrypoint."""
    config = load_config()
    current_ip = get_current_ip()
    if not current_ip:
        return

    record_id = get_record_id(config)
    if not record_id:
        return

    update_dns_record(config, record_id, current_ip)


if __name__ == "__main__":
    main()
