import discord
import os
from dotenv import load_dotenv
import random
import json
import asyncio

load_dotenv()

token = os.getenv('TOKEN')

info_string = '''
Deck of Many Choices
---------
A character can choose, once and only once, to draw a specified number of cards (max 10) from this deck of 52. They must specify an exact number of cards, and choose to draw from the top (unfettered magics) or the bottom (refined magics) of the deck. Once so declared,the specified number cards will appear from the deck, cause some specified effects, and then return to the deck, which is now inert to the previous user. It can be used by someone else after ten minutes has passed.

Commands are:
$draw_u n to draw n cards from the unfettered magics deck
$draw_r n to draw n cards from the refined magics deck
'''

refined_deck = json.load(open('refined_deck.json'))
base_deck = json.load(open('base_deck.json'))

async def draw_from_deck(deck_json, message):
    message_content = message.content.split(' ')
    if len(message_content) < 2:
        await message.channel.send("Must specify a number of draws. e.g. " + message_content[0] + " 2")
    if not message_content[1].isdigit():
        await message.channel.send("Second argument must be an integer")

    num_draws = int(message_content[1])
    selections = random.sample(range(0,len(deck_json)), num_draws)
    for i in selections:
        card = deck_json[str(i)]
        desc = card['Description']
        if 'Roll' in card.keys():
            # Change description to have roll result
            roll_string = card['Roll']
            try:
                roll_add = int(roll_string.split('+')[1])
                roll_string = roll_string.split('+')[0]
            except:
                roll_add = 0
            die_nums = roll_string.split('d')
            roll_result = str(sum(random.choices(range(1, int(die_nums[1])+1), k = int(die_nums[0]))) + roll_add)
            desc = desc.replace(roll_string, roll_result)

        card_info = "```\n" + card['Name'] + "\n----------\n" + desc + "\n```"

        await message.channel.send(card_info, file=discord.File(card['Image']))

        if "End_Draws" in card.keys():
            break

        if 'Add_Draw' in card.keys():
            #Add that many new cards to list
            re_selections = random.sample(range(0,len(deck_json)), len(deck_json))
            additions = [x for x in re_selections if x not in selections]
            additional_selections = additions[0:int(card['Add_Draw'])]
            selections.extend(additional_selections)
            
        if 'Choose_Draw' in card.keys():
            await message.channel.send("```\nYou have the option to draw " + str(card['Choose_Draw']) + " more cards. Refer to descriptions above for the option details. Enter 'draw' to draw more cards, or 'continue' to keep the original effect.\n```")
            def check(m):
                return (m.content.lower() == 'draw' or m.content.lower() == 'continue') and m.channel == message.channel
            try:
                msg = await client.wait_for('message', timeout=300.0, check=check)
            except asyncio.TimeoutError:
                await message.channel.send('```Defaulting to continue```')
            else:
                if msg.content == 'draw':
                    re_selections = random.sample(range(0,len(deck_json)), len(deck_json))
                    additions = [x for x in re_selections if x not in selections]
                    additional_selections = additions[0:int(card['Choose_Draw'])]
                    selections.extend(additional_selections)

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$draw_info'):
        await message.channel.send("```" + info_string + "```")

    if message.content.startswith('$draw_u'):
        await draw_from_deck(base_deck, message)
    
    if message.content.startswith('$draw_r'):
        await draw_from_deck(refined_deck, message)


client.run(token)