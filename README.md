# cloudflare-ddns-updater
script to automatically update your ip on cloudflare

1. `git clone https://github.com/kohbgk/cloudflare-ddns-updater.git && cd cloudflare-ddns-updater`
2. `pip install -r requirements.txt`
3. Update `config.json` with your Cloudflare API token, zone ID, and record name
4. `python cloudflare_ddns.py`

- Set `"proxied": false` in the script if you're using WireGuard.
- Use Task Scheduler or cron to run it automatically.
