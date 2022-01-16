import discord
from googlesearch import search
import asyncpraw
import time
from discord.ext import tasks
from db import Database

# DISCORD: CHANNEL IDS


# DISCORD: REDDIT BOT ID
TOKEN=''              #Enter Discord token 
CHANNELID_MAIN=''     #Enter a "General" Discord channel id...right click on discord channel and click "CopyID" to get channel id
CHANNELID_CASHBACK='' #Enter a separate Discord channel id...right click on discord channel and click "CopyID" to get channel id

# REDDIT: REDDIT BOT ID 
USERNAME=''           #enter reddit username
PASSWORD=''           #enter reddit password
CLIENTID=''           #enter reddit bot clientid
CLIENTSECRET=''       #enter reddit bot client secret

client = discord.Client()
reddit = asyncpraw.Reddit(client_id = CLIENTID, client_secret = CLIENTSECRET, password = PASSWORD, user_agent = "redditbot_v1.0 by {}".format(USERNAME), username = USERNAME)

database = Database('database.db')
websites = ["retailmenot", "maxrebates", 'befrugal', 'rebatesme', 'givingassistant']
subreddits = None
channel = None
cb_channel = None


already_sent = set()

@tasks.loop(seconds=2)
async def backGroundTasks():
  global already_sent

  if database.getCount() == 0:
    return

  try:
    async for submission_id in subreddits.new(limit=1):
      if (time.time()-submission_id.created_utc) < 59 and submission_id.id not in already_sent:
        already_sent.add(submission_id.id)

        pst = ((submission_id.created_utc/3600)-8)*3600
        f_time = str(time.asctime(time.localtime(pst))).split()
        f_time[3] = f_time[3] + 'AM'
        if int(f_time[3][:2]) >= 12:
          f_time[3] = f_time[3][:-2] + 'PM'
          hour = int(f_time[3][:2])
          if hour > 12:
            f_time[3] = "{0}{1}".format(hour-12, f_time[3][2:])
        f_time = "{} {}, {} {}".format(f_time[1], f_time[2], f_time[-1], f_time[3])   
        await channel.send("Date: {}\nSubreddit: {}\nTitle: {}\nLink: {}\nReddit URL: https://reddit.com{}\n".format(f_time, (submission_id.permalink).split('/')[2], submission_id.title, submission_id.url, submission_id.permalink))  
  except:
    pass

  if len(already_sent) > 2000:
    already_sent = set()  

@client.event
async def on_message(message):
  global subreddits

  if message.author == client.user:
    return

  if message.content.startswith('$help'):
    to_send = "Below is a list of available commands:\n\n"
    to_send += "$hello - Replies with 'hello'\n\n"
    to_send += "$subscribe - to a subrredit in the following format '$subscribe subreddit'\n\n"
    to_send += "$unsubscribe - from a subrredit in the following format '$unsubscribe subreddit'\n\n"
    to_send += "$subscriptions - Replies with list of subreddits currently subscribed to\n\n"
    to_send += "$subscription count - Replies with the number of subreddits subscribed to\n\n"
    to_send += "$cb WEBSITE - Links to cashback wesbites for that store"
    await message.channel.send(to_send) 

  elif message.content.startswith('$hello'):
    await message.channel.send('Hello')

  elif message.content.startswith('$subscribe'):
    sentence = message.content.split()
    if len(sentence) < 2:
      await message.channel.send("Missing subreddit argument. Enter '$help' to view command format")
      return
    sub = sentence[1]
    if sub in database.getValues():
      await message.channel.send("Already subscribed to r/{}".format(sub)) 
      return
    try:
      reddit.subreddits.search_by_name(sub, exact=True)
      database.insertDB(sub)
      subreddits = await reddit.subreddit("+".join(database.getValues()))
      await message.channel.send("Successfully subscribed to r/{}".format(sub)) 
    except:
      await message.channel.send("r/{} is not a valid subreddit".format(sub)) 

  elif message.content.startswith('$unsubscribe'):
    sentence = message.content.split()
    if len(sentence) < 2:
      await message.channel.send("Missing subreddit argument. Enter '$help' to view command format")
      return
    sub = sentence[1]
    if sub not in database.getValues():
      await message.channel.send("Not currently subscribed to r/{}".format(sub))  
    else:
      database.removeDB(sub)
      if database.getCount() > 0:
      	subreddits = await reddit.subreddit("+".join(database.getValues()))
      await message.channel.send("Successfully unsubscribed from r/{}".format(sub))   

  elif message.content.startswith('$subscriptions'):
    to_send = "Subscribed to:\n\n"
    for x in [x for x in sorted(database.getValues())]:
      to_send += "r/{}\n".format(x)
    await message.channel.send(to_send[:-1])  

  elif message.content.startswith('$subscription count'):
    await message.channel.send("Subscription Count:\n\n{} subreddits".format(database.getCount())) 

  elif message.content.startswith('$cb'):
    website = message.content.split()
    if len(website) < 2:
      await message.channel.send("Missing website name argument. Enter '$help' to view command format")
      return
    to_send = ''
    for query in websites:
      for link in search(query + ' {}'.format(website[1]), tld='co.in', start=0, stop=1):
        to_send += '{}\n'.format(link)
    await cb_channel.send(to_send[:-1])

  elif message.content.startswith('$'):
    await message.channel.send("Not a valid command. Enter '$help' for a list of valid commands") 

  else:
    return

@client.event
async def on_ready():
  global channel, cb_channel, subreddits
  channel = client.get_channel(int(CHANNELID_MAIN))
  cb_channel = client.get_channel(int(CHANNELID_CASHBACK))
  subreddits = await reddit.subreddit("+".join(database.getValues()))
  backGroundTasks.start()

client.run(TOKEN)