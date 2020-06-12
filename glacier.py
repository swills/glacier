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
        loop.create_task(self.get_conversation_list())
        loop.create_task(self.rtm_main())

    async def rtm_main(self):
        await asyncio.sleep(1)
        await rtm_client.start()

    @RTMClient.run_on(event="message")
    async def message_received(**payload):
        data = payload['data']
        # channel_id = data['channel']
        # user = data['user']
        # print("channel_id: {}".format(channel_id))
        # print("user: {}".format(user))
        # print("text: {}".format(data['text']))
        text = "{}: {}".format(data['user'], data['text'])
        print(text)
        mainWindow.textBrowser.append(text)
        # self.textBrowser.append(text)
        # self.textBrowser.append(text)

    def button_click_send_message(self) -> None:
        message = self.textEdit.toPlainText()
        channel = self.current_channel_id
        loop.create_task(self.send_message_async(channel=channel,
                                                 message=message))
        self.textEdit.clear()

    async def send_message_async(self, channel: str, message: str) -> None:
        await self.web_client.chat_postMessage(channel=channel, text=message)

    async def get_history(self, chan_id):
        # print("get_history called")
        self.textBrowser.clear()
        history = await self.web_client.conversations_history(channel=chan_id)
        history_messages = history['messages']
        history_messages.reverse()
        for message in history_messages:
            # print("-------------")
            # print(message['type'])
            # if 'subtype' in message.keys():
            #     print(message['subtype'])
            if 'user' in message.keys():
                # print(message['user'])
                user_id = message['user']
                user_real_name = await self.get_user_real_name(user_id=user_id)
                # print("user name: {}".format(user_real_name))
                # handle <@USER_ID> joined/set topic etc
                message_text: str = message['text']
                if "<@{}>".format(user_id) in message['text']:
                    message_text = message['text'].replace("<@{}>".format(user_id),
                                                           user_real_name)
                else:
                    for at_user in re.findall(r'<@U.*?>', message_text):
                        at_user_id = at_user.replace('<@', '').replace('>', '')
                        at_user_name = await self.get_user_real_name(user_id=at_user_id)
                        # print("found at_user: {} {}".format(at_user, at_user_id))
                        # print("at_user name: {}".format(at_user_name))
                        message_text = message_text.replace(
                            at_user, "@" + at_user_name)
                    message_text = "{}: {}".format(user_real_name, message_text)
                self.textBrowser.append(message_text)
            # else:
            #     print(message)
            # print(message['text'])

    async def get_user_real_name(self, user_id):
        user_info = await self.get_user_info(user_id=user_id)
        # print("user_info 2: {}".format(user_info))
        # print("user_info 3: {}".format(user_info['real_name']))
        return user_info['real_name']

    async def get_user_info(self, user_id):
        if user_id not in self.user_info_cache:
            user_info_resp = await self.web_client.users_info(user=user_id)
            self.user_info_cache[user_id] = user_info_resp['user']
        # print("user_info: {}".format(self.user_info_cache[user_id]))
        return self.user_info_cache[user_id]

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
