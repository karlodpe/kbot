import logging
import openai
import os

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET") 
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

openai.api_key =  os.environ.get("OPENAI_KEY")

app = App(
    token=SLACK_BOT_TOKEN,
    process_before_response=True)

logging.basicConfig(level=logging.INFO)


@app.event("message")
def question_handler(client, event, logger):

    message = event['text']
    if "?" in message:
        
        logging.info("Question received")
        response = openai.Completion.create(
            engine="davinci",
            prompt="Message: To the guy who invented zero\nResponse: Thanks for nothing\nMessage: Ladies, if he can’t appreciate your fruit jokes\nResponse: You need to let that mango\nMessage: Geology rocks\nResponse: Geography is where it’s at\nMessage: I don’t trust stairs\nResponse: They’re always up to something\nMessage: " + message + "\nResponse:",
            temperature=0.4,
            max_tokens=30,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stop=["Message:"]
        )

        channel_id=event['channel']
        app.client.chat_postMessage(channel=channel_id, text=response.choices[0].text)
        logging.info("Question answered")


def main():
    logging.info("App starting..")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
   main()
   