#!/usr/bin/env python3
import asyncio
import os
import re
import sys

from PyQt5 import QtWidgets
from quamash import QEventLoop
from slack import RTMClient
from slack import WebClient

from MainWindow import Ui_PyQT5SlackClient
# import logging
# logging.basicConfig(level=logging.DEBUG)
slack_api_token = os.environ["SLACK_API_TOKEN"]
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]


class MainWindow(QtWidgets.QMainWindow, Ui_PyQT5SlackClient):

    def __init__(self, *args, web_client=None, rtm_client=None, **kwargs):
        super().__init__()

        self.web_client = web_client
        self.rtm_client = rtm_client
        self.setupUi(self)
        self.chan_list: list = []
        self.chan_name_list: list = []
        self.pushButton.clicked.connect(self.button_click_send_message)
        self.pushButton.setEnabled(False)
        self.listWidget.itemClicked.connect(self.channel_item_clicked)
        self.current_channel_id: str = ""
        self.user_info_cache = {}
        self.bots_info_cache = {}
        loop.create_task(self.get_conversation_list())
        loop.create_task(self.rtm_main())

    async def rtm_main(self):
        await asyncio.sleep(1)
        await rtm_client.start()

    @RTMClient.run_on(event="message")
    async def message_received(**payload):
        data = payload['data']
        user_id = data['user']
        content = data['text']
        await mainWindow.append_message_to_chat(user_id=user_id, content=content)

    def button_click_send_message(self) -> None:
        message = self.textEdit.toPlainText()
        channel = self.current_channel_id
        loop.create_task(self.send_message_async(channel=channel,
                                                 message=message))
        self.textEdit.clear()

    async def send_message_async(self, channel: str, message: str) -> None:
        await self.web_client.chat_postMessage(channel=channel, text=message)

    async def get_history(self, chan_id):
        self.textBrowser.clear()
        history = await self.web_client.conversations_history(channel=chan_id)
        history_messages = history['messages']
        history_messages.reverse()
        for message in history_messages:
            if 'type' in message.keys():
                if 'subtype' in message.keys():
                    if message['subtype'] == 'bot_message':
                        # print("processing bot message: {}".format(message))
                        if 'username' in message.keys():
                            content: str = message['username'] + ": " + message['text']
                        else:
                            content = message['text']
                        if 'attachments' in message.keys():
                            for attachment in message['attachments']:
                                if 'fallback' in attachment.keys():
                                    content = content + attachment['fallback']
                        user_id = message['bot_id']
                        await self.append_message_to_chat(content=content,
                                                          user_id=user_id)
                    # else:
                    #     print("unhandled subtype type: {}".format(message))
                if 'user' in message.keys():
                    # print("processing message: {}".format(message))
                    content = message['text']
                    user_id = message['user']
                    await self.append_message_to_chat(content=content, user_id=user_id)
            else:
                print("unhandled message type: {}".format(message))

    async def append_message_to_chat(self, content, user_id):
        if re.match("^U.*", user_id, flags=re.IGNORECASE):
            user_real_name = await self.get_user_real_name(user_id=user_id)
        else:
            user_real_name = await self.get_bots_real_name(bot_id=user_id)
        if "<@{}>".format(user_id) in content:
            content = content.replace("<@{}>".format(user_id), user_real_name)
        else:
            for at_user in re.findall(r'<@U.*?>', content):
                at_user_id = at_user.replace('<@', '').replace('>', '')
                at_user_name = await self.get_user_real_name(user_id=at_user_id)
                content = content.replace(
                    at_user, "@" + at_user_name)
            content = "{}: {}".format(user_real_name, content)
        self.textBrowser.append(content)

    async def get_user_real_name(self, user_id):
        user_info = await self.get_user_info(user_id=user_id)
        if "profile" in user_info.keys():
            return user_info['profile']['real_name']
        elif "real_name" in user_info.keys():
            return user_info['real_name']
        else:
            print("Failed to get real name: {}".format(user_info))
            return "Unknown User"

    async def get_bots_real_name(self, bot_id):
        # print("getting bot info: {}".format(bot_id))
        bots_info = await self.get_bots_info(bot_id=bot_id)
        # print("bots info: {}".format(bots_info))
        if 'user_id' in bots_info['bot'].keys():
            user_id = bots_info['bot']['user_id']
            bot_user_name = await self.get_user_real_name(user_id=user_id)
            return bot_user_name
        elif 'name' in bots_info['bot'].keys():
            return bots_info['bot']['name']
        else:
            print("Failed to get bot name: {}".format(bot_id))
            return "unknown bot user"

    async def get_user_info(self, user_id):
        if user_id not in self.user_info_cache:
            user_info_resp = await self.web_client.users_info(user=user_id)
            self.user_info_cache[user_id] = user_info_resp['user']
        return self.user_info_cache[user_id]

    async def get_bots_info(self, bot_id):
        if bot_id not in self.bots_info_cache:
            bots_info_resp = await self.web_client.bots_info(bot=bot_id)
            # print("raw bot info: {}".format(bots_info_resp))
            self.bots_info_cache[bot_id] = bots_info_resp
        return self.bots_info_cache[bot_id]

    async def get_conversation_list(self):
        conversation_list = await self.web_client.conversations_list(exclude_archived=1)
        channels = conversation_list['channels']
        self.chan_list = channels
        self.listWidget.clear()
        for chan in channels:
            if chan['is_member']:
                self.chan_name_list.append(str(chan['name']))
        self.chan_name_list.sort()
        for name in self.chan_name_list:
            self.listWidget.addItem(name)

    def channel_item_clicked(self, item) -> None:
        chan_name = item.text()
        chan_info_list = [element for element in self.chan_list
                          if element['name'] == chan_name]
        chan_info = chan_info_list[0]
        self.current_channel_id = chan_info['id']
        self.pushButton.setEnabled(True)
        loop.create_task(self.get_history(self.current_channel_id))


app = QtWidgets.QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
web_client = WebClient(token=slack_api_token, run_async=True, loop=loop)
rtm_client = RTMClient(token=slack_bot_token, connect_method='rtm.start',
                       run_async=True, loop=loop)

future = rtm_client.start()

with loop:
    mainWindow = MainWindow(web_client=web_client, rtm_client=rtm_client)
    mainWindow.show()
    loop.run_forever()
