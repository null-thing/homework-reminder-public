import discord
from discord.ext import commands
import datetime as dt
from dateutil import tz
import asyncio
from mysql import *
import pymysql

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

hostname = "your db hostname here"
username = "your db username here"
password = "your db password here"
database = "your db name here"



async def presenttime(bot: commands.Bot):
    while True:
        now = dt.datetime.now()
        test_channel = bot.get_channel(1154649981395931268)
        alarm_interval = [3600, 26100, 43200, 86400, 172800, 259200, 604800]
        for interval in alarm_interval:
            test_alarm = assignment_alarm(interval)
            if (test_alarm):
                for alarmer in test_alarm:
                    alarm_people = alarmer[2]
                    alarm_list = f''
                    for alarm in alarm_people:
                        alarm_list += f'<@{alarm}> '
                    await test_channel.send(alarm_list)
                    await test_channel.send(f"{alarmer[0]} {alarmer[1]} 과제가 {interval//3600}시간 후에 마감됩니다!")

        # 뭔가 할 일
        test_overdue = assignment_overdue()
        # TODO: ping lazy people
        if (test_overdue):
            for overduer in test_overdue:
                lazy_people = overduer[2]
                sloth_list = f''
                for sloth in lazy_people:
                    sloth_list += f'<@{sloth}> '
                await test_channel.send(sloth_list)
                await test_channel.send(f"{overduer[0]} {overduer[1]} 과제가 기한 초과입니다!")
        await test_channel.send(f" 현재 시간은 " + str(now.hour) + "시 " + str(now.minute) +"분 입니다.")

        await asyncio.sleep(60)

def assignment_overdue():
    db = pymysql.connect(host=hostname, user=username, passwd=password, db=database, charset='utf8')
    result = []
    cur = db.cursor()
    cur.execute("SELECT DISTINCT assignment.id from assignment LEFT JOIN user_assignment ON assignment.id = user_assignment.aid WHERE UNIX_TIMESTAMP(due)- UNIX_TIMESTAMP(NOW()) < 0 AND UNIX_TIMESTAMP(due) - UNIX_TIMESTAMP(NOW()) >= -60")
    assignment_ID = cur.fetchall()

    for aid in assignment_ID:
        current_result = []
        cur.execute(f"SELECT assignment_name, subject FROM assignment WHERE id = {aid[0]}")   
        name, subject = cur.fetchall()[0]
        cur.execute(f"SELECT user.user_id FROM user_assignment join user on user_assignment.uid=user.id WHERE user_assignment.aid='{aid[0]}'") 
        user_name = cur.fetchall()
        user_name = list(map(lambda x: x[0], user_name))
        current_result.append(name)
        current_result.append(subject)
        current_result.append(user_name) #tuple
        
        result.append(current_result)
    
    db.close()
    return result
    

def assignment_alarm(remaining:int):
    db = pymysql.connect(host=hostname, user=username, passwd=password, db=database, charset='utf8')
    result = []
    cur = db.cursor()
    cur.execute(f"SELECT DISTINCT assignment.id from assignment LEFT JOIN user_assignment ON assignment.id = user_assignment.aid WHERE UNIX_TIMESTAMP(due) - UNIX_TIMESTAMP(NOW()) < {remaining} AND UNIX_TIMESTAMP(due) - UNIX_TIMESTAMP(NOW()) >= {remaining}-60")
    assignment_ID = cur.fetchall()

    for aid in assignment_ID:
        current_result = []
        cur.execute(f"SELECT assignment_name, subject FROM assignment WHERE id = {aid[0]}")   
        name, subject = cur.fetchall()[0]
        cur.execute(f"SELECT user.user_id FROM user_assignment join user on user_assignment.uid=user.id WHERE user_assignment.aid='{aid[0]}'") 
        user_name = cur.fetchall()
        user_name = list(map(lambda x: x[0], user_name))
        current_result.append(name)
        current_result.append(subject)
        current_result.append(user_name) #tuple
        
        result.append(current_result)
    
    db.commit()
    db.close()
    
    return result
