import configparser
import warnings

import controller.user_controller as user_controller
import controller.stock_controller as stock_controller
import controller.view_controller as view_controller
import controller.confidence_controller as confidence_controller

import module.black_litterman as black_litterman

from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    SetWebhookEndpointRequest,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FollowEvent,
    UnfollowEvent
)

warnings.filterwarnings('ignore')
app = Flask(__name__)

config = configparser.ConfigParser()
config.read('static/config.ini')

configuration = Configuration(access_token=config['line_bot']['channel_access_token'])
handler = WebhookHandler(config['line_bot']['channel_secret'])

with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)
    line_bot_api.set_webhook_endpoint(SetWebhookEndpointRequest(endpoint=config['line_bot']['web_hook'] + '/callback'))


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    res = {
        'msg': "指令無效"
    }
    if "@指令清單" in event.message.text:
        commands = ["@指令清單：", "@關注清單", "\t@關注清單+", "\t@關注清單-", "@觀點矩陣", "\t@觀點矩陣-絕對",
                    "\t@觀點矩陣-相對"]
        res['msg'] = '\n'.join(commands)

    elif "@關注清單+" in event.message.text:
        msg = event.message.text.replace("@關注清單+", "")
        res = stock_controller.create_stock(event.source.user_id, msg)
    elif "@關注清單-" in event.message.text:
        msg = event.message.text.replace("@關注清單-", "")
        res = stock_controller.remove_stock(event.source.user_id, msg)
    elif "@關注清單" in event.message.text:
        res = stock_controller.read_stock(event.source.user_id)
    elif "@觀點矩陣-絕對輸入" in event.message.text:
        msg = event.message.text.replace("@觀點矩陣-絕對輸入\n", "")
        res = view_controller.create_absolute_view(event.source.user_id, msg)
    elif "@觀點矩陣-相對輸入" in event.message.text:
        msg = event.message.text.replace('@觀點矩陣-相對輸入\n', "")
        res = view_controller.create_pq_view(event.source.user_id, msg)
    elif "@觀點矩陣-絕對模板" in event.message.text:
        res = stock_controller.template_absolute_view(event.source.user_id)
    elif "@觀點矩陣-相對模板" in event.message.text:
        msg = event.message.text.replace("@觀點矩陣-相對模板", "")
        res = stock_controller.template_pq_view(event.source.user_id, msg)
    elif "@觀點矩陣" in event.message.text:
        res = view_controller.read_view(event.source.user_id)
    elif "@置信矩陣-輸入" in event.message.text:
        msg = event.message.text.replace("@置信矩陣-輸入\n", "")
        res = confidence_controller.create_confidences(event.source.user_id, msg)
    elif "@置信矩陣-模板" in event.message.text:
        res = stock_controller.template_confidences(event.source.user_id)
    elif "@置信矩陣" in event.message.text:
        res = confidence_controller.read_confidences(event.source.user_id)
    elif "@置信區間-輸入" in event.message.text:
        msg = event.message.text.replace("@置信區間-輸入\n", "")
        res = confidence_controller.create_interval(event.source.user_id, msg)
    elif "@置信區間-模板" in event.message.text:
        res = stock_controller.template_interval(event.source.user_id)
    elif "@置信區間" in event.message.text:
        res = confidence_controller.read_interval(event.source.user_id)
    elif "@策略一" in event.message.text:
        res = black_litterman.check_one(event.source.user_id)
    elif "@策略二" in event.message.text:
        res = black_litterman.check_two(event.source.user_id)
    elif "@策略三" in event.message.text:
        res = black_litterman.check_three(event.source.user_id)
    elif "@策略四" in event.message.text:
        res = black_litterman.check_four(event.source.user_id)
    elif "@策略" in event.message.text:
        res['msg'] = "策略一\n[\n\t絕對觀點、\n\t市場指數、\n\t股票市值、\n\t股票調整後收盤價\n]\
        \n\n策略二\n[\n\t絕對觀點、\n\t市場指數、\n\t股票市值、\n\t股票調整後收盤價、\n\t置信矩陣\n]\
        \n\n策略三\n[\n\t絕對觀點、\n\t市場指數、\n\t股票市值、\n\t股票調整後收盤價、\n\t置信區間\n]\
        \n\n策略四\n[\n\t相對觀點、\n\t市場指數、\n\t股票市值、\n\t股票調整後收盤價\n]"

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=res['msg'])]
            )
        )


@handler.add(FollowEvent)
def handle_follow(event):
    user_controller.create_user(event.source.user_id)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="測試測試")]
            )
        )


@handler.add(UnfollowEvent)
def handle_follow(event):
    user_controller.remove_user(event.source.user_id)


if __name__ == "__main__":
    app.run(host=config['flask']['host'], port=config['flask'].getint('port'))
