import cv2
import time
import agent
import os
from agent import Agent
from dotenv import load_dotenv
from wehead_hack_sdk import Wehead

# Load default environment variables (.env)
load_dotenv()
AGENT_NAME = "ai-boyfriend"

agent = Agent(AGENT_NAME)
agent.giveMemory()

token = "eyJpZCI6IDIsICJ2YWwiOiAidXI2bldyY21pcC1aQXF3bmVvQlBMUmJLRmc2TDlzRVhOaHJPM00wdDJCOEYySHVIQlRTdXM2YUtEcUc5eDlCNE5OM1BMdnVDUlZfeVhmZ3VZVmlrM2cifQ=="
wehead = Wehead(token)

wehead.move(pitch=0, yaw=0)
wehead.say("Hey maya, this is damon")

@wehead.on_phrase
def handle_phrase(text):
    print(text)
    response = agent.action(text)
    print("agent: " + response)
    wehead.say(response, voice="onyx")

while True:
    pass  # Keep the script running