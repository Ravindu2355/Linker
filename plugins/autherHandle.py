from pyrogram import Client, filters
from globals import Authers



@Client.on_message(filters.command("addAuth"))
def a_auth(client, message: Message):


@Client.on_message(filters.command("banAuth"))
def b_auth(client, message: Message):
  
