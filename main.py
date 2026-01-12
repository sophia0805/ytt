import discord
from discord.ext import commands
import os
import asyncio
import threading
from dotenv import load_dotenv
from flask import Flask
import vonage
import requests
import base64
import json

load_dotenv()
token = os.getenv("token")

# Vonage API credentials (using the required environment variables)
vonage_api_key = (os.getenv("VONAGE_API_KEY"))
vonage_api_secret = (os.getenv("VONAGE_API_SECRET"))
vonage_phone_number = (os.getenv("VONAGE_FROM_NUMBER"))
recipient_phone_number = (os.getenv("RECIPIENT_PHONE_NUMBER"))
print(vonage_api_key, vonage_api_secret, vonage_phone_number, recipient_phone_number)

# Using direct HTTP requests with Basic Auth - no need to initialize Vonage client
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Required to read message content and process commands
client = commands.Bot(command_prefix="soph ", intents=intents, case_insensitive=True)

async def isSophia(ctx):
  return ctx.author.id == 704038199776903209 or ctx.author.id == 701792352301350973
 
client.snipes = {}

@client.event
async def on_ready():
  await client.change_presence(activity=discord.watching(name=" the AI & Data Science Club!"))
  print('Ready!')

async def send_sms(text_message):
    """Send text-only MMS via Vonage Messages API using image message_type with null URL
    This avoids the '[FREE SMS DEMO, TEST MESSAGE]' prefix that appears with SMS
    """
    if not vonage_api_key or not vonage_api_secret or not recipient_phone_number or not vonage_phone_number:
        print("MMS not configured - missing required environment variables")
        print("Required: VONAGE_API_KEY, VONAGE_API_SECRET, VONAGE_FROM_NUMBER, RECIPIENT_PHONE_NUMBER")
        return
    
    try:
        # Run synchronous SDK call in executor to avoid blocking event loop
        def _send_sms():
            # Format phone numbers (remove + if present, as per Vonage documentation)
            # Don't use leading + or 00, start with country code (e.g., 14155550105)
            to_number = recipient_phone_number
            from_number = vonage_phone_number
            
            # For MMS text messages, use the simple structure
            message_data = {
                "message_type": "text",
                "text": text_message,
                "to": to_number,
                "from": "14258189935",
                "channel": "mms"
            }
            
            # Use Basic Auth (API key/secret) - this is what the example code uses
            if not vonage_api_key or not vonage_api_secret:
                raise Exception("API key and secret required for MMS messages")
            
            credentials = f"{vonage_api_key}:{vonage_api_secret}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            response = requests.post(
                "https://api.nexmo.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Basic {encoded_credentials}"
                },
                json=message_data
            )
            
            if not response.ok:
                error_data = response.json()
                print(f"Full error response: {error_data}")
                error_detail = error_data.get('detail', 'Unknown error')
                
                if response.status_code == 401:
                    raise Exception(
                        f"Authentication failed (401): {error_detail}. "
                        "Check that your VONAGE_API_KEY and VONAGE_API_SECRET are correct, "
                        "and that your account has MMS messaging enabled. "
                        "You may need to enable MMS in your Vonage account settings."
                    )
                raise Exception(f"Message failed: {response.status_code} - {error_detail}")
            
            return response.json()
        
        response = await asyncio.get_event_loop().run_in_executor(None, _send_sms)
        
        # Check response status
        # Messages API returns a response with message_uuid on success
        if hasattr(response, 'message_uuid'):
            print(f"MMS message sent successfully. Message UUID: {response.message_uuid}")
        elif hasattr(response, 'model_dump'):
            response_dict = response.model_dump(exclude_unset=True)
            if response_dict.get('message_uuid'):
                print(f"MMS message sent successfully. Message UUID: {response_dict.get('message_uuid')}")
            else:
                error_text = response_dict.get('error_text', 'Unknown error') or response_dict.get('error-text', 'Unknown error')
                print(f"MMS message failed with error: {error_text}")
        elif isinstance(response, dict):
            if response.get('message_uuid'):
                print(f"MMS message sent successfully. Message UUID: {response.get('message_uuid')}")
            else:
                error_text = response.get('error_text', 'Unknown error') or response.get('error-text', 'Unknown error')
                print(f"MMS message failed with error: {error_text}")
        else:
            print(f"MMS message response: {response}")
            
    except Exception as e:
        print(f"Error sending MMS: {e}")
        import traceback
        traceback.print_exc()

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  # Check if message is in the specific guild
  if message.guild and message.guild.id == 764284315906736128:
    print(message.content, message.channel.name, message.author.name)
    sms_message = f"[Discord] {message.author.name} in #{message.channel.name}: {message.content[:1600]}"  # SMS supports longer messages via concatenation
    await send_sms(sms_message)
  await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    print("ERROR:")
    print(error)
    if isinstance(error, discord.ext.commands.UnexpectedQuoteError) or isinstance(error, discord.ext.commands.InvalidEndOfQuotedStringError):
        return await ctx.send("Sorry, it appears that your quotation marks are misaligned, and I can't read your query.")
    if isinstance(error, discord.ext.commands.ExpectedClosingQuoteError):
        return await ctx.send("Oh. I was expecting you were going to close out your command with a quote somewhere, but never found it!")
    if isinstance(error, discord.ext.commands.MissingRequiredArgument):
        return await ctx.send("Oops, you are missing a required argument in the command.")
    if isinstance(error, discord.ext.commands.ArgumentParsingError):
        return await ctx.send("Sorry, I had trouble parsing one of your arguments.")
    if isinstance(error, discord.ext.commands.TooManyArguments):
        return await ctx.send("Woahhh!! Too many arguments for this command!")
    if isinstance(error, discord.ext.commands.BadArgument) or isinstance(error, discord.ext.commands.BadUnionArgument):
        return await ctx.send("Sorry, I'm having trouble reading one of the arguments you just used. Try again!")
    if isinstance(error, discord.ext.commands.CheckAnyFailure):
        return await ctx.send("It looks like you aren't able to run this command, sorry.")
    if isinstance(error, discord.ext.commands.PrivateMessageOnly):
        return await ctx.send("Pssttt. You're going to have to DM me to run this command!")
    if isinstance(error, discord.ext.commands.NoPrivateMessage):
        return await ctx.send("Ope. You can't run this command in the DM's!")
    if isinstance(error, discord.ext.commands.NotOwner):
        return await ctx.send("Oof. You have to be the bot's master to run that command!")
    if isinstance(error, discord.ext.commands.MissingPermissions) or isinstance(error, discord.ext.commands.BotMissingPermissions):
        return await ctx.send("Er, you don't have the permissions to run this command.")
    if isinstance(error, discord.ext.commands.MissingRole) or isinstance(error, discord.ext.commands.BotMissingRole):
        return await ctx.send("Oh no... you don't have the required role to run this command.")
    if isinstance(error, discord.ext.commands.MissingAnyRole) or isinstance(error, discord.ext.commands.BotMissingAnyRole):
        return await ctx.send("Oh no... you don't have the required role to run this command.")
    if isinstance(error, discord.ext.commands.NSFWChannelRequired):
        return await ctx.send("Uh... this channel can only be run in a NSFW channel... sorry to disappoint.")
    if isinstance(error, discord.ext.commands.ConversionError):
        return await ctx.send("Oops, there was a bot error here, sorry about that.")
    if isinstance(error, discord.ext.commands.UserInputError):
        return await ctx.send("Hmmm... I'm having trouble reading what you're trying to tell me.")
    if isinstance(error, discord.ext.commands.CommandNotFound):
        return await ctx.send("Sorry, I couldn't find that command.")
    if isinstance(error, discord.ext.commands.CheckFailure):
        return await ctx.send("Sorry, but I don't think you can run that command.")
    if isinstance(error, discord.ext.commands.DisabledCommand):
        return await ctx.send("Sorry, but this command is disabled.")
    if isinstance(error, discord.ext.commands.CommandInvokeError):
        return await ctx.send("Sorry, but an error incurred when the command was invoked.")
    if isinstance(error, discord.ext.commands.CommandOnCooldown):
        return await ctx.send(f"Slow down! This command's on cooldown. Wait {error.retry_after} seconds!")
    if isinstance(error, discord.ext.commands.MaxConcurrencyReached):
        return await ctx.send("Uh oh. This command has reached MAXIMUM CONCURRENCY. *lightning flash*. Try again later.")
    if isinstance(error, discord.ext.commands.ExtensionError):
        return await ctx.send("Oh no. There's an extension error. Please ping a developer about this one.")
    if isinstance(error, discord.ext.commands.CommandRegistrationError):
        return await ctx.send("Oh boy. Command registration error. Please ping a developer about this.")
    if isinstance(error, discord.ext.commands.CommandError):
        return await ctx.send("Oops, there was a command error. Try again.")
    return

@client.event
async def on_message_delete(message):
   client.snipes[message.channel.id] = message
   return

@client.command()
async def ping(ctx):
    embed = discord.Embed(
      title = f'Pong! Catch that :ping_pong:! {round(client.latency * 1000)}ms ',
      description = "",
      colour = discord.Colour.teal()
      )
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, nick):
    await member.edit(nick=nick)
    embed = discord.Embed(
        description=f" :white_check_mark: | Nickname changed. ",
        colour=0x224B8B)
    await ctx.send(embed=embed) 

@client.command()   
async def purge(ctx, amount = 10000):
    await ctx.message.delete()
    authorperms = ctx.author.permissions_in(ctx.channel)
    if authorperms.manage_messages:
      await ctx.channel.purge(limit=amount)

@client.group(invoke_without_command=True)
@commands.has_permissions(manage_messages=True)
async def embed(ctx, *, text):
    embed = discord.Embed(
      description=text,
    )
    await ctx.send(embed=embed)

@client.command()
async def snipe(ctx):
    channel_id = ctx.channel.id
    match = client.snipes.get(channel_id)
    if match is None:
      await ctx.send(f"{ctx.author.name}, there's nothing to snipe!")
    else:
      embed = discord.Embed(
        title=f'Snipe:',
        description=f'**Last Deleted Message:** \n{match.content} \n - {match.author}', 
        color = discord.Color.purple()
      )
      embed.set_footer(text= f"Snipe requested by {ctx.author.name}")
      await ctx.send(embed=embed)

# Flask app for keeping the bot alive on Render
app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return "Bot is running!"

@app.route('/health', methods=['GET', 'HEAD'])
def health():
    return {"status": "ok", "bot": "online"}, 200

@app.route('/test', methods=['GET', 'HEAD'])
def test():
    return {"message": "Flask is working!", "app": "main"}, 200

# Catch-all route for debugging
@app.errorhandler(404)
def not_found(e):
    return {"error": "Not Found", "message": "Route not found. Available routes: /, /health, /test"}, 404

def run_bot():
    """Run Discord bot in background thread"""
    try:
        async def bot_main():
            async with client:
                await client.start(token)
        asyncio.run(bot_main())
    except Exception as e:
        print(f"Error starting Discord bot: {e}")
        import traceback
        traceback.print_exc()

# Initialize bot thread after Flask app is set up
# Delay bot start slightly to ensure Flask is ready
def start_bot_thread():
    if token:
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        print("Discord bot thread started")
    else:
        print("Warning: No Discord token found, bot will not start")

# Start bot thread when module loads (but after Flask routes are registered)
start_bot_thread()

# For local development
if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)