import logging

logger = logging.getLogger(__name__)

def send_email(to: str, subject: str, body: str):
    logger.info(f"STUB: Email to {to} - {subject}: {body}")
    return True

def send_slack(channel: str, message: str):
    logger.info(f"STUB: Slack to {channel}: {message}")
    return True
