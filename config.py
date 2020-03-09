import json

Config = {}

with open("config.json","r") as f:
    content = f.read()
    Config = json.loads(content)