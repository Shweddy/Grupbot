from flask import Flask, request, jsonify, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# LINE API configuration
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

# Dictionary of food recommendations
food_recommendations = {
    "/cnxfood": [
        {"name": "A Restaurant", "contact": "0856676648"},
        {"name": "B Coffee Shop", "contact": "LINE ID: Bcoffee"},
        # Add more entries here
    ]
}

@app.route("/callback", methods=['POST'])
def callback():
    # Get request header signature
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip().lower()

    if user_message in food_recommendations:
        response_text = ""
        for item in food_recommendations[user_message]:
            response_text += f"{item['name']}\nContact: {item['contact']}\n\n"
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Sorry, I don't understand that command.")
        )

if __name__ == "__main__":
    app.run(debug=True)