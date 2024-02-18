import os
from agent import Agent

agent = Agent("ai-bf")

agent.giveMemory()
print(agent.action("hi"))