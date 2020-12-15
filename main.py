import requests
import discord
import os
import pandas as pd
import time
import csv
import progressbar

url = 'YOUT WEBHOOK URL HERE'
token = 'YOUR TOKEN HERE'
#Change it to something your set of messages doesn't contain.
separator = "^"
message_limit = 200 #Put any number om messages you want, limited by your storage
ratelimit = 5 #In seconds, time between actions (sent), limited by Discord API
# If you're loosing messages, try increasing this number.

# Saves all messages from the current channel to a csv
async def messages_to_file(message,bot):
  messages = await message.channel\
  .history(limit=message_limit).flatten()
  if os.path.exists('messages.csv'):
    os.remove("messages.csv")
  f = open("messages.csv","a")
  f.write("content"+separator+"name"+separator+"avatar"+"\n")
  for i in range(len(messages)):
    f.write(str(messages[-i].content.replace("\n","\\n"))+separator+\
    str(messages[-i].author.display_name)+separator+\
    str(messages[-i].author.avatar_url)+"\n")
  f.close()
  await message.add_reaction("✅")


# Sends all messages from csv throught the webhook set above
async def file_to_messages(message,bot):
  widgets = [' [', progressbar.Timer(\
  format= 'elapsed time: %(elapsed)s'),\
  '] ', progressbar.Bar('*'),' (', progressbar.ETA(), ') ',]

  messages = pd.read_csv("messages.csv",\
  delimiter=separator, quoting=csv.QUOTE_NONE,\
  error_bad_lines=False)

  bar = progressbar.ProgressBar(max_value=len(messages),\
  widgets=widgets).start()

  for i in range(len(messages)):
    myobj = {'content': messages["content"][i].replace("\\n","\n").replace("@everyone","@everybody").replace("@here","@active"),\
    'username': messages["name"][i],\
    'avatar_url': messages["avatar"][i]}
    x = requests.post(url, data = myobj)
    bar.update(i)
    time.sleep(ratelimit)
  print("Done!")


# Checks if message is a command
async def commands(message,bot):
  if(message.system_content == "!messages2file" and\
  not(message.author.bot)):
    await messages_to_file(message,bot)
  elif(message.system_content == "!file2messages" and\
  not(message.author.bot)):
    await file_to_messages(message,bot)


# Discord bot event listener
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        await commands(message,self)


# Run
client = MyClient()
client.run(token)

