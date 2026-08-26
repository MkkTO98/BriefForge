#!/usr/bin/env python3
"""Telegram notifier stub.

This is intentionally inactive by default. To activate later:
1. Create a Telegram bot with BotFather.
2. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in a local, untracked `.env` or service environment.
3. Extend this script to POST pending questions to Telegram's sendMessage endpoint.

Do not commit secrets.
"""
from pathlib import Path
import json


def list_pending(project='.'):
    p=Path(project)/'question_queue'/'pending'
    for f in sorted(p.glob('*.json')):
        print(json.dumps(json.loads(f.read_text()), indent=2))

if __name__ == '__main__':
    list_pending()
