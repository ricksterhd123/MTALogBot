import platform
import requests
import subprocess
import re
import argparse


def get_tail_cmd(system, log_path):
    tail_cmd = {
        'Windows': f"powershell.exe \"Get-Content '{log_path}' -Tail 0 -Wait\"",
        'Linux': ['tail', '-0f', log_path]
    }
    return tail_cmd[system]


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
    # Remove hex colour tags e.g. #FF0000
    message = re.sub("#(?:[0-9a-fA-F]{3}){1,2}", "", message)
    # Mask illegal keywords
    for hidden_static_str in illegal_keywords:
        masked_str = "#" * len(hidden_static_str)
        message = re.sub(hidden_static_str, masked_str, message)
    return message


def start(log_path: str, webhook_url: str, illegal_keywords: list[str]) -> None:
    """
    Start watching log file and post updates to webhook url
    """
    cmd = get_tail_cmd(platform.system(), log_path)
    print(cmd)
    f = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f"====Started MTALogBot====\
        \nLog filepath: {log_path}\
        \nWebhook URL: {webhook_url}\
        \nKeywords given: {len(illegal_keywords)}\
        \n=========================")

    while True:
        try:
            message = f.stdout.readline().decode("utf-8")
            if message:
                log_message = filter_log_message(
                    illegal_keywords, message)
                send_discord_message(webhook_url, log_message)
        except Exception as e:
            print(e)
        finally:
            # clean up here
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Share MTA:SA server logs to discord via webhook')
    parser.add_argument('logpath', help='Path to MTA:SA server.log')
    parser.add_argument('webhook', help='A valid discord webhook url')
    parser.add_argument('keywords', nargs='*',
                        help='A list of keywords to mask')
    args = parser.parse_args()
    start(args.logpath, args.webhook, args.keywords)
