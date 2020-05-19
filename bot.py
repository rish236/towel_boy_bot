import pymysql
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import CheckFailure, check
from discord.ext.commands import has_permissions
from discord.ext.commands import *
import time
import datetime
import asyncio
from asyncio import TimeoutError
import os



def connect_db():
    conn = pymysql.connect(os.environ['host'], user=os.environ['user'],port=os.environ['port'],
                           passwd=os.environ['password'], db=os.environ['dbname'])

    conn.autocommit(True)
    return conn


def main():

    

    token = config.token


    bot = commands.Bot(command_prefix='!')


    @bot.event
    async def on_ready():
        print(f'{bot.user.name} is now online!')

    @bot.event
    async def on_member_join(member):
        await member.create_dm()
        await member.dm_channel.send(
            f"Hi {member.name}, don't forget to react with the poop emoji on the bottom to gain full access to the server! Welcome to the server, we hope you enjoy your stay here. ^^"
        )




    @bot.command(pass_context=True, name='opgg', help = 'Provides you with an opgg link for a given ign.')
    async def opgg(ctx, user):
        link = "https://na.op.gg/summoner/userName={}".format(user) 
        await ctx.send(link)



    

    @bot.command(pass_context=True, name='showteams', help = 'Shows the current teams signed up for a specific tourney.')
    async def show_teams(ctx, tourney_name):
        conn = connect_db()
        msg = ""

        with conn:
            cursor = conn.cursor()
            query = "SELECT team_name FROM teams WHERE tourney_name = '{}'".format(tourney_name)
            cursor.execute(query)
            teams = cursor.fetchall()

            await ctx.send("Current teams signed up for **{}**:".format(tourney_name))
            for i in teams:
                msg = msg + "\n" + i[0]

            await ctx.send(msg)

    @bot.command(pass_context=True, name='showopentourneys', help = 'Shows the current teams signed up for a specific tourney.')
    async def show_open_tourneys(ctx):
        conn = connect_db()
        msg = ""

        with conn:
            cursor = conn.cursor()
            query = "SELECT tourney_name FROM active_tourneys WHERE active = 1"
            cursor.execute(query)
            tourneys = cursor.fetchall()

            await ctx.send("Tourneys that are open for sign up:")
            for i in tourneys:
                msg = msg + "\n" + i[0]

            await ctx.send(msg)

    @show_teams.error
    async def show_teams_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You forgot to enter a tournament name. Please try again.")


    @bot.command(pass_context=True, name='showteamsfinal', help = 'Shows the finalized list of teams signed up for a tourney')
    @has_permissions(administrator=True)

    async def showteamsfinal(ctx, tourney_name):
        conn = connect_db()
        msg = ""

        with conn:
            cursor = conn.cursor()
            query = "SELECT team_name, player1, player2, player3, player4, player5 FROM teams WHERE tourney_name = '{}'".format(tourney_name)
            cursor.execute(query)
            teams = cursor.fetchall()

            print(teams)
            emoji = ""
            for i in range(len(teams)):
                if i % 2 == 0:
                    emoji = "\U0001F525"
                else:
                    emoji = "\U0001F4A6"
                await ctx.send("**" + teams[i][0] + "**" + "\n" + emoji + emoji + emoji + emoji + emoji + emoji + "\n" + "**Members:**\n" + teams[i][1] + "\n" + teams[i][2] + "\n" + teams[i][3] + "\n" + teams[i][4] + "\n" + teams[i][5] + "\n" + "-----------------------")



    

    @bot.command(pass_context=True, name='showmembers', help = "Provides you with the IGNs for members registered on a team.")
    async def show_members(ctx, team_name):
        conn = connect_db()

        with conn:
            cursor = conn.cursor()
            query = "SELECT player1, player2, player3, player4, player5 FROM teams WHERE team_name = '{}'".format(team_name)

            try:
                cursor.execute(query)
                rows = cursor.fetchall()

                player1 = rows[0][0]
                player2 = rows[0][1]
                player3 = rows[0][2]
                player4 = rows[0][3]
                player5 = rows[0][4]
            except Exception as e:
                await ctx.send("Team name **{}** does not exist in the database. Please try again.".format(team_name))
            cursor.close()

        await ctx.send("Here are the IGNs for team **{}**:\n{}\n{}\n{}\n{}\n{}".format(team_name, player1, player2, player3, player4, player5))

    @show_members.error
    async def show_members_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You forgot to enter a team name. Please try again.")

    

    @bot.command(pass_context=True, name='opggteam', help = 'Provides you with opgg links for players in a team.')
    async def opgg_team(ctx, team_name):
        conn = connect_db()

        with conn:
            cursor = conn.cursor()
            query = "SELECT player1, player2, player3, player4, player5 FROM teams WHERE team_name = '{}'".format(team_name)
            cursor.execute(query)
            rows = cursor.fetchall()

            player1 = rows[0][0]
            player2 = rows[0][1]
            player3 = rows[0][2]
            player4 = rows[0][3]
            player5 = rows[0][4]
            cursor.close()

        link = "https://na.op.gg/summoner/userName=" 
        await ctx.send("Here are the opgg's for team **{}**:\n{}\n{}\n{}\n{}\n{}".format(team_name, link + player1, link + player2, link + player3, link + player4, link + player5))

    @opgg_team.error
    async def opgg_team_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You forgot to enter a team name. Please try again.")
    
    @bot.command(pass_context=True, name='opensignups', help = 'Allows admin to open signups for a tourney.')
    @has_permissions(administrator=True)
    async def open_signups(ctx, tourney_name):
        conn = connect_db()

        with conn:
            cursor = conn.cursor()
            print("creating table")
            query = '''CREATE TABLE IF NOT EXISTS teams (disc_user VARCHAR(25), date DATETIME, team_name VARCHAR(50), player1 VARCHAR(20), player2 VARCHAR(20), 
            player3 VARCHAR(20), player4 VARCHAR(20), player5 VARCHAR(20), tourney_name VARCHAR(20), primary key(team_name))'''
            cursor.execute(query)


            query2 = '''CREATE TABLE IF NOT EXISTS active_tourneys (tourney_name VARCHAR(20), active TINYINT(1), primary key(tourney_name))'''
            cursor.execute(query2)


            query3 = "INSERT INTO active_tourneys (tourney_name, active) VALUES (%s, %s)"
            cursor.execute(query3, (tourney_name, 1))



            cursor.close()

            print("finished")

        ts = time.time()
        today = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        x = datetime.date.today()

        friday = x + datetime.timedelta( (4-x.weekday()) % 7 )
        await ctx.send("Signups for **{}** are now open from **{}** to **{} 11:59 PM EST**.".format(tourney_name, today, friday))


  



    @bot.command(pass_context=True, name='closesignups', help = 'Allows admin to open signups for a tourney.')
    @has_permissions(administrator=True)
    async def close_signups(ctx, tourney_name):
        conn = connect_db()

        with conn:
            cursor = conn.cursor()
            
            query = "UPDATE active_tourneys SET active = 0 WHERE tourney_name = '{}'".format(tourney_name)
            cursor.execute(query)



            cursor.close()

        await ctx.send("Signups for **{}** are now closed.".format(tourney_name))

    
    @bot.command(pass_context=True, name='signup', help = 'Signup for your team for open tourneys.')
    async def signup(ctx, tourney_name, player1, player2, player3, player4, player5, team_name):
        conn = connect_db()
        with conn:
            cursor = conn.cursor()
            query = "SELECT active FROM active_tourneys WHERE tourney_name = '{}'".format(tourney_name)
           
            try:
                cursor.execute(query)
                is_active = cursor.fetchone()[0]

            except Exception as e:
                if 'NoneType' in str(e):

                    await ctx.send("Unable to signup team because **{}** does not exist. Please try again with the correct tourney name.".format(tourney_name))
                    return


            print(is_active)

            if is_active ==1:

         

                query2 = "INSERT INTO teams (disc_user, date, team_name, player1, player2, player3, player4, player5, tourney_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                ts = time.time()
                date_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                disc_user = str(ctx.message.author)
                tup = (disc_user, date_time, team_name, player1, player2, player3, player4, player5, tourney_name)


                #when we run multple tournaments at the same time, need to make it so team_name is not a primary key. need to validate that team_name and tourney_name are not the same instead
                try:
                    cursor.execute(query2, tup)

            
                except pymysql.err.IntegrityError:
                    await ctx.send("Team name already exists. Please use a different name, or use the edit command to edit your current team.")
                    return
            
                print("finished")

                cursor.close()
                

                await ctx.send("Successfully signed up **{}**!".format(team_name))
            else:
                await ctx.send("**{}** signups are closed at this time. Please contact @rish or @TimeStoned if you believe this is an error.".format(tourney_name))

    @signup.error
    async def signup_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing a required parameter. The correct parameters/order = **<tournament name> <player1> <player2> <player3> <player4> <player5> <team name>**. \nPlease try again.")


    @bot.command(pass_context=True, name='removeteam', help = 'Remove a team from a specific tourney.')
    async def remove_team(ctx, team_name, tourney_name):
        conn = connect_db()

        current_disc_user = str(ctx.author)


           
        with conn:

            cursor = conn.cursor()
            query = "SELECT disc_user FROM teams WHERE team_name = '{}' and tourney_name = '{}'".format(team_name, tourney_name)
            cursor.execute(query)

            try:
                disc_user = cursor.fetchone()[0]
            except:
                await ctx.send("Either team name or tourney name is incorrect. Please try again.")
                return

            if disc_user == current_disc_user:
                
                query2 = "DELETE FROM teams WHERE team_name = '{}' and tourney_name = '{}'".format(team_name, tourney_name)
                print(query2)
                cursor.execute(query2)
                await ctx.send("Team **{}** was successfully removed from **{}**".format(team_name, tourney_name))
                   

            else:
                await ctx.send("You are not able to remove this team, please contact the person who signed up your team to remove it.")
                return
    



    @remove_team.error
    async def remove_team_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You are missing a required parameter. The correct parameters/order = **<team name> <tournament name>**")


    @bot.command(pass_context=True, name='edit', help = 'Edit/replace members on your team.')
    async def edit(ctx, team_name):
        conn = connect_db()
        with conn:
            #when we run multiple tournaments in a week, need to add tourney_name as a parameter and add "and" to the where clause
            cursor = conn.cursor()
            query = "SELECT disc_user, player1, player2, player3, player4, player5 FROM teams WHERE team_name = '{}'".format(team_name)
            try:
                cursor.execute(query)
                rows = cursor.fetchall()
            

                disc_user = rows[0][0]
                player1 = rows[0][1]
                player2 = rows[0][2]
                player3 = rows[0][3]
                player4 = rows[0][4]
                player5 = rows[0][5]
               

            except Exception as e:
                await ctx.send("This team name does not exist in the database. Please try again. If you think this is an error, please contact @rish.")

            current_disc_user = str(ctx.author)


            if disc_user == current_disc_user:
                await ctx.send('''Here are the members of **{}**: \n1) {}\n2) {}\n3) {}\n4) {}\n5) {}\n\nPlease choose the number corresponding to the player you want to edit and enter the new IGN. For example: 1 newign. 
                '''.format(team_name, player1, player2, player3, player4, player5))

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel


                try:

                    msg = await bot.wait_for('message', check=check, timeout=30.0)
                    resp = msg.content.split(" ")
                    
                except asyncio.TimeoutError:
                    await ctx.send('\nYou took too long, try again.')
                

                print(resp[0])
                print(resp[1])
                if int(resp[0]) == 1:
                    query = "UPDATE teams SET player1 = '{}' WHERE team_name = '{}'".format(resp[1], team_name)
                    cursor.execute(query)
                    
                    await ctx.send("Successfully replaced **{}** with **{}**!".format(player1, resp[1]))
                    return

                if int(resp[0]) == 2:
                    query = "UPDATE teams SET player2 = '{}' WHERE team_name = '{}'".format(resp[1], team_name)
                    cursor.execute(query)

                    await ctx.send("Successfully replaced **{}** with **{}**!".format(player2, resp[1]))
                    return

                if int(resp[0]) == 3: 
                    query = "UPDATE teams SET player3 = '{}' WHERE team_name = '{}'".format(resp[1], team_name)
                    cursor.execute(query)

                    await ctx.send("Successfully replaced **{}** with **{}**!".format(player3, resp[1]))
                    return

                if int(resp[0]) == 4:
                    query = "UPDATE teams SET player4 = '{}' WHERE team_name = '{}'".format(resp[1], team_name)
                    cursor.execute(query)

                    await ctx.send("Successfully replaced **{}** with **{}**!".format(player4, resp[1]))
                    return

                
                if int(resp[0]) == 5:
                    query = "UPDATE teams SET player5 = '{}' WHERE team_name = '{}'".format(resp[1], team_name)
                    cursor.execute(query)

                    await ctx.send("Successfully replaced **{}** with **{}**!".format(player5, resp[1]))
                    return

                else:
                    await ctx.send("Please choose a number between 1 and 5 and try again.")
                    return

                

                    
            else:
                await ctx.send("You are not able to edit this team, please contact the person who signed up your team to edit.")
                return
    @edit.error
    async def edit_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You forgot to enter a team name. Please try again.")

    bot.run(os.environ['token'])


if __name__ == "__main__":
    main()





