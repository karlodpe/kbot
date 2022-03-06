import logging
import openai
import os

from slack_bolt import App
#from slack_bolt.adapter.aws_lambda import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]

openai.api_key =  os.environ["OPENAI_KEY"]

app = App(
    token=SLACK_BOT_TOKEN,
    process_before_response=True)

# processed as we get a message - so that we return within 3 seconds
def ackCommand(body, ack):
    text = body.get("text")
    if text is None or len(text) == 0:
        ack("Usage: /kbtech What is Isto?")
    else:
        ack("thinking...")

# processed as we get a message - so that we return within 3 seconds
def ackEvent(body, ack):
    ack()

# process the command - may take longer than 3 seocnds
def processCommand(respond, body):
    r = openai.Answer.create(
        search_model="ada", 
        model="curie", 
        question=body['text'], 
        file="file-2sxwvWhdbC4iuDFiDUIUm1n0", 
        examples_context="Azure Image Builder: Managed image baking based on Hashicorp Packer - but runs as a service with tight integration to Azure.", 
        examples=[["What is Image Builder?", "Image Builder is managed image baking based on Hashicorp Packer - but runs as a service with tight integration to Azure."]], 
        max_rerank=10,
        max_tokens=100,
        stop=["\n", "<|endoftext|>"])

    response = r.answers[0] + "\n"
    #for doc in r.selected_documents:
    #    response = response + doc.text + "\n"
    respond(response)

# process the event - may take longer than 3 seocnds
def processEvent(body, logger):
    message = body['event']['text']
    if "?" in message:
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

        channel_id=body['event']['channel']
        app.client.chat_postMessage(channel=channel_id, text=response.choices[0].text)


### Main Handlers
app.command("/kbtech")(
    ack=ackCommand,  
    lazy=[processCommand]
    )

app.event("message")(
    ack = ackEvent,
    lazy = [processEvent]
    )    

@app.command("/echo")
def repeat_text(ack, respond, command):
    ack()
    respond(command['text'])

if __name__ == "__main__":
   logging.info("App starting..")
   handler = SocketModeHandler(app, SLACK_APP_TOKEN)
   handler.start()

# def lambda_handler(event, context):
#     slack_handler = SlackRequestHandler(app=app)
#     return slack_handler.handle(event, context)


   