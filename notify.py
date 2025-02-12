#!/usr/bin/env python3

import os
import json
import telegram
from telegram.ext import Updater, CommandHandler
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
import pynvml
import time

def pbar(current, maximum, size):
    output = "`|"
    sep = round(current / maximum * size)
    for i in range(sep + 1):
        output += "#"
    for i in range(sep + 1, size):
        output += " "
    output += "|`"
    return output

def get_usage_msg(info, divergence_with_nvidia_smi):
    return "GPU usage is {:.0f} MB\n{}".format(
        info.used / 1024 / 1024 - divergence_with_nvidia_smi,
        pbar(info.used - divergence_with_nvidia_smi * 1024 * 1024, info.total, 24)
    )

class NotifyBot:
    def __init__(self):
        super().__init__()

        try:
            with open("config.json", "r") as config_file:
                config = json.load(config_file)
                token = os.environ["API_TOKEN"]
                self._whitelist = config["whitelist"]
        except FileNotFoundError:
            print("You need to have a config.json file in this directory")
            exit(1)

        self.deviceCount = pynvml.nvmlDeviceGetCount()
        self.states = [None] * self.deviceCount
        self.utilization_threshold = config["utilization_threshold"]
        self.divergence_with_nvidia_smi = config["divergence_with_nvidia_smi"]

        self._updater = Updater(token, use_context=True)
        dp = self._updater.dispatcher
        dp.add_handler(CommandHandler("start", self._register))
        dp.add_handler(CommandHandler("gpu", self._get_gpu))
        self._updater.start_polling()

        self._poll_gpu(5)

    def _register(self, update: Update, context: CallbackContext):
        user_id = update.message.from_user.id
        if user_id not in self._whitelist:
            update.message.reply_text("You are not yet on the whitelist. " +
                f"Add {user_id} to your config to receive notifications from me")
        else:
            update.message.reply_text("Hi! I will notify you when someone starts " +
                "to use the GPU and when it's available again")

    def _get_gpu(self, update: Update, context: CallbackContext):
        print(update.message.from_user.username, "requested gpu usage")
        for index in range(self.deviceCount):
            handle = pynvml.nvmlDeviceGetHandleByIndex(index)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            update.message.reply_text(get_usage_msg(info, self.divergence_with_nvidia_smi), parse_mode=telegram.ParseMode.MARKDOWN)

    def _poll_gpu(self, interval):

        while True:
            for index in range(self.deviceCount):
                handle = pynvml.nvmlDeviceGetHandleByIndex(index)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                used_mb = info.used / 1024 / 1024 - self.divergence_with_nvidia_smi
                if used_mb <= self.utilization_threshold and (self.states[index] == "busy" or self.states[index] == None):
                    for chat_id in self._whitelist:
                        try:
                            self._updater.bot.send_message(chat_id, f"The GPU{index} is available", parse_mode=telegram.ParseMode.MARKDOWN)
                        except telegram.error.Unauthorized:
                            print("Unauthorized for", chat_id)
                    self.states[index] = "free"
                elif used_mb >= self.utilization_threshold and (self.states[index] == "free" or self.states[index] == None):
                    for chat_id in self._whitelist:
                        try:
                            self._updater.bot.send_message(chat_id, f"The GPU{index} is in use", parse_mode=telegram.ParseMode.MARKDOWN)
                        except telegram.error.Unauthorized:
                            print("Unauthorized for", chat_id)
                    self.states[index] = "busy"

            time.sleep(interval)

if __name__ == "__main__":
    pynvml.nvmlInit()
    NotifyBot()
