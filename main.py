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
        message_content = message.content.split(' ')
        if len(message_content) < 2:
            await message.channel.send("Must specify a number of draws. e.g. $draw_u 2")
            return
        if not message_content[1].isdigit():
            await message.channel.send("Second argument must be an integer")
            return

        num_draws = int(message_content[1])
        selections = random.sample(range(0,22), num_draws)
        for i in selections:
            card = base_deck[str(i)]
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
                roll_result = str((random.sample(range(int(die_nums[0]), int(die_nums[1])+1), 1)[0] + roll_add))
                desc = desc.replace(roll_string, roll_result)

            card_info = "```\n" + card['Name'] + "\n----------\n" + desc + "\n```"

            await message.channel.send(card_info, file=discord.File(card['Image']))

            if "End_Draws" in card.keys():
                break
            
            if 'Add_Draw' in card.keys():
                #Add that many new cards to list
                re_selections = random.sample(range(0,22), 22)
                additions = [x for x in re_selections if x not in selections]
                additional_selections = additions[0:int(card['Add_Draw'])]
                selections.extend(additional_selections)
        
            if 'Choose_Draw' in card.keys():
                await message.channel.send("```\nYou have the option to draw " + str(card['Choose_Draw']) + " more cards. Refer to descriptions above for the option details. Say 'draw' to draw more cards, or 'continue' to keep the original effect.\n```")
                def check(m):
                    return (m.content == 'draw' or m.content == 'continue') and m.channel == message.channel
                try:
                    msg = await client.wait_for('message', timeout=300.0, check=check)
                except asyncio.TimeoutError:
                    await message.channel.send('```Defaulting to continue```')
                else:
                    if msg.content == 'draw':
                        re_selections = random.sample(range(0,22), 22)
                        additions = [x for x in re_selections if x not in selections]
                        additional_selections = additions[0:int(card['Choose_Draw'])]
                        selections.extend(additional_selections)
    

    
    if message.content.startswith('$draw_r'):
        message_content = message.content.split(' ')
        if len(message_content) < 2:
            await message.channel.send("Must specify a number of draws. e.g. $draw_r 2")
            return
        if not message_content[1].isdigit():
            await message.channel.send("Second argument must be an integer")
            return

        num_draws = int(message_content[1])
        selections = random.sample(range(0,30), num_draws)
        for i in selections:
            card = refined_deck[str(i)]
            card_info = "```\n" + card['Name'] + "\n----------\n" + card['Description'] + "\n```"
            await message.channel.send(card_info, file=discord.File(card['Image']))
            if 'Add_Draw' in card.keys():
                #Draw that many new cards
                re_selections = random.sample(range(0,30), 30)
                additions = [x for x in re_selections if x not in selections]
                additional_selections = additions[0:int(card['Add_Draw'])]
                selections.extend(additional_selections)


client.run(token)