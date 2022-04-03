# MTA log bot
Relay MTA:SA server logs into discord via webhooks

## Features
- [x] Simple CLI interface
- [x] Mask static keywords such as serials, secrets etc

## Setup
### Clone repository
`git clone https://github.com/ricksterhd123/MTALogBot.git`

### Change directory
`cd MTALogBot`

### Setup venv
`python3 -m venv ./venv`

### Activate venv
#### Linux
`source ./venv/bin/activate`
#### Windows
`.\venv\Scripts\activate`

### Install required dependencies
`pip install -r requirements.txt`

## Usage
`python main.py [log_path] [webhook_url] [...illegal_keywords]`

### Example
`python main.py ../logs/server.log https://discord.com/api/webhooks/{{id}}/{{token}}`

### Help
`python main.py -h`
