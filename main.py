import requests
import time
import subprocess
import select
import re
import argparse


def send_discord_message(webhook_url: str, message: str) -> None:
    """
    HTTP Post string to discord webhook URL
    :param webhookurl: URL to discord webhook
    :param message: Message contents
    :raises: raises exception when HTTP status code is not ok (e.g, 4xx or 5xx)
    """
    r = requests.post(webhook_url, data={
        "content": message
    })
    r.raise_for_status()


def filter_log_message(illegal_keywords: list[str], message: str) -> str:
    """
    Santize the log message before it can be sent to discord
    :param illegal_keywords: List of static string keywords (i.e. without regex) that will get masked
    :param message: Message contents to get filtered
    :returns: resulting message after filtration
    """
    message = re.sub("#(?:[0-9a-fA-F]{3}){1,2}", "", message)
    for hidden_static_str in illegal_keywords:
        masked_str = "#" * len(hidden_static_str)
        message = re.sub(hidden_static_str, masked_str, message)
    return message


def start(log_path: str, webhook_url: str, illegal_keywords: list[str]) -> None:
    """
    Start watching log file and post updates to webhook url
    """
    f = subprocess.Popen(['tail', '-0f', log_path],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)

    print(f"====Started MTALogBot====\
        \nLog filepath: {log_path}\
        \nWebhook URL: {webhook_url}\
        \nKeywords given: {len(illegal_keywords)}\
        \n=========================")

    while True:
        if p.poll(1):
            try:
                log_message = filter_log_message(
                    illegal_keywords, f.stdout.readline().decode("utf-8"))
                send_discord_message(webhook_url, log_message)
            except Exception as e:
                print(e)
            finally:
                # clean up here
                pass

        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Share MTA:SA server logs to discord via webhook')
    parser.add_argument('logpath', help='Path to MTA:SA server.log')
    parser.add_argument('webhook', help='A valid discord webhook url')
    parser.add_argument('keywords', nargs='*',
                        help='A list of keywords to mask')
    args = parser.parse_args()
    start(args.logpath, args.webhook, args.keywords)
