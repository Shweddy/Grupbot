import os
import logging
from flask import Flask, request, jsonify, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

# Load environment variables from a .env file (if you're using one)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Ensure environment variables are set
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')

if not channel_access_token or not channel_secret:
    raise ValueError("Environment variables LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET must be set.")

# Configure logging
logging.basicConfig(level=logging.INFO)

# LINE API configuration using environment variables
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# Dictionary of food recommendations
food_recommendations = {
    "/cnxfood": [
        {"name": "A Restaurant", "contact": "0856676648"},
        {"name": "B Coffee Shop", "contact": "LINE ID: Bcoffee"},
    ],
    "/bkkfood": [
        {"name": "C Restaurant", "contact": "0866676658"},
        {"name": "D Coffee Shop", "contact": "LINE ID: Dcoffee"},
    ]
}

@app.route("/", methods=['GET'])
def home():
    return "Welcome to the LINE bot!", 200

@app.route("/callback", methods=['POST'])
def callback():
    # Get request header signature
    signature = request.headers.get('X-Line-Signature')
    if signature is None:
        abort(400, description="Missing X-Line-Signature header")

    # Get request body as text
    body = request.get_data(as_text=True)
    logging.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logging.error("Invalid signature. Access denied.")
        abort(400, description="Invalid signature. Access denied.")
    except Exception as e:
        logging.error(f"Error handling request: {str(e)}")
        abort(500, description="Internal Server Error")

    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip().lower()
    logging.info(f"Received message: {user_message}")

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
            TextSendMessage(text="Sorry, I don't understand that command. Please try /cnxfood or /bkkfood.")
        )

@app.errorhandler(404)
def page_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def server_error(e):
    logging.error(f"Internal Server Error: {str(e)}")
    return jsonify(error="Internal Server Error"), 500

if __name__ == "__main__":
    app.run(debug=True)