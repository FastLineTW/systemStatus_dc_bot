import psutil
import asciichartpy
import discord
import threading
import asyncio
import time
import datetime
import os

########## Config ##########
# discord mobile app max width = 26
# discord limit 2000 bytes per msg
char_width = 26
char_height = 5

update_invl = 1

rx_title = 'If Rx Mbps:'
tx_title = 'If Tx Mbps:'
rx_pps_title = 'If Rx Pps:'
tx_pps_title = 'If Tx Pps:'
cpu_title = 'CPU Usage:'
mem_title = 'Mem Usage:'

show_byte_rx_chart = True
show_byte_tx_chart = True
show_pps_rx_chart = True
show_pps_tx_chart = True
show_cpu_chart = True
show_mem_chart = True
show_console_chart = False

bot_name = 'Server Status'
bot_token = ''
channel_id = 123

########## Config ##########

version = '220518v0.2'
discordClient = discord.Client()
loop = asyncio.get_event_loop()
clear = lambda: os.system('cls')

message_id = None

char_data = ''

if char_width > 100:
    char_width = 100

if update_invl < 1:
    update_invl = 1
elif update_invl > char_width:
    update_invl = char_width


def getChart(data, title):
    return title + '\n' + asciichartpy.plot(data, {'height': char_height}) + '\n'


def char_drawing_job(char_width, rx_title, tx_title, rx_pps_title, tx_pps_title, cpu_title, mem_title):
    global char_data
    bytes_recv_arr_data = [0] * char_width
    bytes_sent_arr_data = [0] * char_width
    pps_recv_arr_data = [0] * char_width
    pps_sent_arr_data = [0] * char_width
    cpu_arr_data = [0] * char_width
    mem_arr_data = [0] * char_width
    while (True):
        local_char_data = '\n'
        bytes_recv_a = psutil.net_io_counters().bytes_recv
        bytes_sent_a = psutil.net_io_counters().bytes_sent
        pps_recv_a = psutil.net_io_counters().packets_recv
        pps_sent_a = psutil.net_io_counters().packets_sent
        cpu_arr_data.pop(0)
        cpu_arr_data.append(psutil.cpu_percent(1))

        bytes_recv_b = psutil.net_io_counters().bytes_recv
        bytes_sent_b = psutil.net_io_counters().bytes_sent
        pps_recv_b = psutil.net_io_counters().packets_recv
        pps_sent_b = psutil.net_io_counters().packets_sent
        bytes_recv = (bytes_recv_b - bytes_recv_a) * 8 / 1000 / 1000
        bytes_sent = (bytes_sent_b - bytes_sent_a) * 8 / 1000 / 1000
        pps_recv = pps_recv_b - pps_recv_a
        pps_sent = pps_sent_b - pps_sent_a
        bytes_recv_arr_data.pop(0)
        bytes_recv_arr_data.append(bytes_recv)
        bytes_sent_arr_data.pop(0)
        bytes_sent_arr_data.append(bytes_sent)
        pps_recv_arr_data.pop(0)
        pps_recv_arr_data.append(pps_recv)
        pps_sent_arr_data.pop(0)
        pps_sent_arr_data.append(pps_sent)
        mem_arr_data.pop(0)
        mem_arr_data.append(psutil.virtual_memory().percent)

        if show_byte_rx_chart:
            local_char_data += getChart(bytes_recv_arr_data, rx_title)
        if show_byte_tx_chart:
            local_char_data += getChart(bytes_sent_arr_data, tx_title)
        if show_pps_rx_chart:
            local_char_data += getChart(pps_recv_arr_data, rx_pps_title)
        if show_pps_tx_chart:
            local_char_data += getChart(pps_sent_arr_data, tx_pps_title)
        if show_cpu_chart:
            local_char_data += getChart(cpu_arr_data, cpu_title)
        if show_mem_chart:
            local_char_data += getChart(mem_arr_data, mem_title)
        char_data = '```' + str(datetime.datetime.now()) + local_char_data + '```'
        if show_console_chart:
            clear()
            print(char_data)


async def clean_channel_msg(channelID):
    await discordClient.get_channel(channelID).purge(limit=100)


async def edit_message(msg):
    global message_id
    await message_id.edit(content=msg)


async def send_message(channelID, msg):
    global message_id
    message_id = await discordClient.get_channel(channelID).send(msg)


async def discord_bot_job(update_invl, chID):
    global char_data
    await clean_channel_msg(chID)
    await send_message(chID, 'Start!  ' + version)
    # just show version on channel
    time.sleep(5)
    # loop.create_task(clean_channel_msg(chID))
    # loop.create_task(send_message(chID, 'Start!'))
    while True:
        try:
            if not message_id == None:
                await edit_message(char_data)
        except Exception as err:
            print(err)
            print('Total char_data_len = ' + str(char_data))
        time.sleep(update_invl)


threading.Thread(target=char_drawing_job,
                 args=(char_width, rx_title, tx_title, rx_pps_title, tx_pps_title, cpu_title, mem_title,)).start()


@discordClient.event
async def on_ready():
    await discordClient.user.edit(username=bot_name)
    loop.create_task(discord_bot_job(update_invl, channel_id))
    # threading.Thread(target=discord_bot_job, args=(update_invl, channel_id,)).start()


discordClient.run(bot_token)
