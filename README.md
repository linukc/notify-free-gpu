Get notifications via Telegram when your nvidia GPU is available again. It is a modified version of https://github.com/cyd3r/notify-free-gpu.

## How it works

+ If memory usage of the GPU drops below utilization_threshold MB, you will get a message "The GPU is available"
+ If memory usage of the GPU goes above utilization_threshold MB, you will get a message "The GPU is in use"

If you want to know the current memory usage of the GPU, send `/gpu` to the bot and it will respond you with a message like "Z MB is in use"
If you see divergence with nvidia-smi, set variable in config (in MB)

## Setup

Create venv and install requirements. Tested with py3.8 and py3.10.

Next, you have to create a `config.json` file in this directory containing the bot token and a list of user ids that the bot should send messages to:

```json
{
    "whitelist": [
        123456789,
        987654321
    ],
    "utilization_threshold": 1000,
    "divergence_with_nvidia_smi": 0
}
```

If you don't know how to set up a bot or get the bot token, take a look at https://core.telegram.org/bots

If you start a chat with the bot and your user id is not listed in the whitelist, the bot will tell you:

> You are not yet on the whitelist. Add 987654321 to your config to receive notifications from me

## Run

```python
API_TOKEN=... python3 notify.py
```
