import agent
import os
from agent import Agent
from dotenv import load_dotenv

# Load default environment variables (.env)
load_dotenv()
AGENT_NAME = "ai-boyfriend"

agent = Agent(AGENT_NAME)

# # Creates Pinecone Index
# agent.createIndex()
agent.giveMemory()

def ai_bot_response(userInput: str):
    return agent.action(userInput)

# while True:
#     userInput = input()
#     if userInput:
#         if (userInput.startswith("read:")):
#             agent.read(" ".join(userInput.split(" ")[1:]))
#             print("Understood! The information is stored in my memory.")
#         elif (userInput.startswith("think:")):
#             agent.think(" ".join(userInput.split(" ")[1:]))
#             print("Understood! I stored that thought into my memory.")
#         elif (userInput.startswith("readDoc:")):
#             agent.readDoc(" ".join(userInput.split(" ")[1:]))
#             print("Understood! I stored the document into my memory.")
#         else:
#             print(agent.action(userInput), "\n")
#     else:
#         print("SYSTEM - Give a valid input")
