from telethon.sync import TelegramClient, events
import asyncio
from open_ai_analysis import SimpleGptAgent
from dotenv import load_dotenv
import os
from streamlit import secrets
import tiktoken
import pandas as pd

class TelegramBot(object):
    
    def __init__(self, channel_username = -1):    
        
        # Your details from the step above
        load_dotenv()
        self.api_id = os.environ.get('api_id')
        self.api_hash = os.environ.get('api_hash')
        self.channel_username = int(os.environ.get('channel_username', -1))
        self.api_id = secrets['api_id']
        self.api_hash = secrets['api_hash']
        
        #self.client = TelegramClient('anon', self.api_id, self.api_hash)
        self.reply = ''
        self.messages = ''
        self.messages_df = pd.DataFrame(columns=['message_id', 'sender_id', 'sender_name', 'date', 'text', 'is_reply',
            'reply_to_msg_id', 'reply_message_sender_id', 'reply_message_text'])
        self.debug_1 = ''
        self.debug_2 = ''
        self.messages_limit = 10
        self.tokens = 0
        self.analysis = ''
        self.all_messages = ''

        # id shall be used with prefix -100, else it leads to an error
        #channel_username = -1001717592521  # replace with the channel's username
        self.channel_username = channel_username
        #self.channel_username = -1001949867218
        #self.channel_username = -1001872324786
        self.channel_title = ""
        # Register the event handler
        #self.client.on(events.NewMessage(chats=[self.channel_username]))(self.handler)

        try:
            self.json_file = f'channel/{self.channel_username}.json'  # Replace with your JSON file path
            self.messages_df = pd.read_json(self.json_file)
        except:
            print(f'no json file for current channel')

    async def start_bot(self):
        if not self.client.is_connected():
            print('connect client')
            await self.client.connect()


    async def get_title(self):
        async with TelegramClient('anon', self.api_id, self.api_hash) as client:
            await client.start()
            channel = await client.get_entity(self.channel_username)
            self.channel_title = channel.title
    
    async def get_historical(self, limit: int = None, find_str = None):
        # note: searching crypto add extra space, else each text which contains the name will be added
        # [' CAU ', 'canxium'], add extra space cause CAU can be find in many words, which will return wrong answer
        #limit = limit or self.messages_limit
        self.messages = ''

        # Initialize the tokenizer
        encoding = tiktoken.get_encoding("cl100k_base")

        # Variable to store the total token count
        self.tokens = 0

        if find_str is not None:
            pattern = '|'.join(find_str)
            #filtered_df = self.messages_df[self.messages_df['text'].isin(find_str)]
            filtered_df = self.messages_df[self.messages_df['text'].str.contains(pattern, case=False, na=False, regex=True)]
        elif find_str is None and limit is not None:
            filtered_df = self.messages_df.iloc[:limit]
        else:
            print('no filtered df returned')
            return

        self.debug_1 = filtered_df

        # Looping through DataFrame
        for index, row in filtered_df.iterrows():

            if row['reply_message_text'] is not None:
                self.messages += '*** ' + str(row.reply_message_text) + '  \n'
            self.messages += str(row.text) + '  \n  \n'

        # Tokenize the message text
        self.tokens = len(encoding.encode(self.messages))

        print("historical done")
    
    # get all data of a channel
    async def get_all_historical(self, save = False, update = True):
        # update means there is already an historical, it will get last missing messages and add them to the df
        # if update is False, get all messages, save them to the df. Content of df will be overwritten
        
        print('start')
        self.all_messages = []
        reply_message = None
            
        # if update, set min id
        if update:
            min_id = self.messages_df.loc[0].message_id + 1     # +1 needed else get the last message too
            print(f'min id calculated is {min_id}')
        else:
            min_id = 0
            
        async with TelegramClient('anon', self.api_id, self.api_hash) as client:
            await client.start()
            channel = await client.get_entity(self.channel_username)
            
            try:
                async for message in client.iter_messages(channel, limit= None, min_id = min_id):
                    print(message.id)
                    #then if you want to get all the messages text
                    if message.is_reply == True:
                        #reply_message = await message.get_reply_message()
                        async for reply_message in client.iter_messages(channel, ids = message.reply_to_msg_id):
                            pass
                    attributes = {
                        'message_id': message.id,
                        'sender_id': message.sender_id,
                        'sender_name': message.post_author, 
                        'date': message.date,
                        'text': message.message,
                        'is_reply': message.is_reply,
                        'reply_to_msg_id': message.reply_to_msg_id,
                        'reply_message_sender_id': None if reply_message is None else reply_message.sender_id,
                        'reply_message_text': None if reply_message is None else reply_message.message
                    }
                    self.all_messages.append(attributes)
            except Exception as e:
                print(e)
            
            print("historical done")
            
            # if update, add data on top
            if update:
                temp_df = pd.DataFrame(self.all_messages)
                self.messages_df = pd.concat([temp_df, self.messages_df], axis = 0, ignore_index = True)
            # else overwrite the dataframe
            else:
                self.messages_df = pd.DataFrame(self.all_messages)
            
            if save :
                self.messages_df.to_json(self.json_file)
                print ('json saved')

            print("function done")

if __name__ == '__main__':
    bot = TelegramBot(channel_username = -1)
    bot.messages_limit = 10
    #bot.client.start()
    loop = asyncio.get_event_loop()
    #loop.run_until_complete(bot.get_historical())
    #loop.run_until_complete(bot.get_all_historical(update = True, save = True))
    #bot.reply = agent.ask(bot.messages)
    print(bot.messages)
    print('---------')
    print('analysis ongoing')
    print('---------')
    print(bot.reply)

    



