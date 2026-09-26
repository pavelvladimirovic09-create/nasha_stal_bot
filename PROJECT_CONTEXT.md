# PROJECT: Telegram-bot NASHA STAL

## BASIC INFO

- Server: 167.71.129.198 (DigitalOcean, Ubuntu 24.04)
- Project dir: /root/nasha_stal_bot
- venv: /root/nasha_stal_bot/venv
- Python: 3.12.3
- Channel ID: -1004320078173
- Bot: @nasha_stal_bot

## MANAGEMENT

    systemctl status nasha_stal       # status
    systemctl restart nasha_stal      # restart
    journalctl -u nasha_stal -f       # systemd logs
    tail -f logs/bot_$(date +%Y%m%d).log   # bot logs

## SCHEDULE (Kyiv time)

- News post: every 10 min, 7:00-22:00
- Morning digest: 8:00
- Weekly digest: Sunday 20:00
- Monthly digest: 1st day, 20:00
- Cache cleanup (35 days): 07:00
- Backup: 23:00

## STRUCTURE

- main.py - entry point
- bot/ - dispatcher, post formatter
- core/ - RSS, news processing (OpenAI), priorities
- morning/ - morning digest (weather, currency, fuel, day info)
- post_modules/ - weekly_digest, monthly_digest, rubric, humanize
- scheduler/ - job_scheduler, clean_cache
- config/ - settings (from .env)
- logs/ - daily logs (logrotate)
- templates/ - post images

## RUNTIME DATA (not in git)

- posted_links.json - dict {link: timestamp}, 35 days
- weekly_news.json - news archive, 35 days (weekly: 7d, monthly: 30d)

## .env KEYS

- TELEGRAM_BOT_TOKEN
- OPENAI_API_KEY
- CHANNEL_ID
- POST_INTERVAL_MINUTES
- MAX_POSTS_PER_DAY

## BACKUP

- /root/backups/nasha_stal_YYYYMMDD_HHMM.tar.gz (7 last)
- Script: /root/backups/backup.sh
- Cron: daily 20:00 UTC (23:00 Kyiv)

## IMPORTANT NOTES

- TZ: ZoneInfo(Europe/Kyiv) in code. System is UTC.
- RSS limit: limit_per_source=5 -> ~95 news per cycle.
- feedparser needs feedparser-sgmllib - do NOT remove!
- clear_weekly_news() in weekly_digest.py - do NOT call.

## HISTORY

- 2026-09-26: TZ fix, RSS limit 5, dict cache, clean_cache 35d, real monthly, backups
- 2026-09-25: systemd instead of screen, feedparser-sgmllib fix, crash-loop closed
