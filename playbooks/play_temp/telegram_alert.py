import os
import json
import urllib.request
from ansible.plugins.callback import CallbackBase

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'telegram_alert'

    def __init__(self):
        super(CallbackModule, self).__init__()
        # Fetch Bot Token and Chat ID from environment variables for security
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    def _send_telegram(self, text):
        if not self.bot_token or not self.chat_id:
            self._display.warning("Telegram Callback: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = json.dumps({
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }).encode('utf-8')

        req = urllib.request.Request(
            url, 
            data=payload, 
            headers={'Content-Type': 'application/json'}
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                pass
        except Exception as e:
            self._display.warning(f"Telegram Callback: Failed to send alert - {str(e)}")

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Fires automatically when a task fails."""
        if ignore_errors:
            return

        host = result._host.get_name()
        task_name = result._task.get_name()
        
        # Extract meaningful error message
        error_msg = result._result.get('msg', '')
        if not error_msg:
            error_msg = result._result.get('stderr', 'No detailed stdout/stderr provided')

        alert_payload = (
            f"🚨 *Ansible Task Failure*\n\n"
            f"*Device:* `{host}`\n"
            f"*Task:* {task_name}\n"
            f"*Details:* `{error_msg}`"
        )

        self._send_telegram(alert_payload)

    def v2_runner_on_unreachable(self, result):
        """Fires when SSH/Netmiko connection fails completely."""
        host = result._host.get_name()
        error_msg = result._result.get('msg', 'Host unreachable')

        alert_payload = (
            f"⚠️ *Ansible Host Unreachable*\n\n"
            f"*Device:* `{host}`\n"
            f"*Details:* `{error_msg}`"
        )

        self._send_telegram(alert_payload)