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
    conn = pymysql.connect(os.environ['host'], user=os.environ['user'], passwd=os.environ['password'], db=os.environ['dbname'])
    conn.autocommit(True)
    return conn


def main():

    

    token = os.environ['token']



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
    async def opgg(ctx, *, message):

        message = message.replace(" ", "+")

        link = "https://na.op.gg/summoner/userName={}".format(message) 
        await ctx.send(link)



    

    @bot.command(pass_context=True, name='showteams', help = 'Shows the current teams signed up for a specific tourney.')
    async def show_teams(ctx, *, message):
        conn = connect_db()
        msg = ""

        with conn:
            cursor = conn.cursor()
            query = "SELECT team_name FROM teams WHERE tourney_name = '{}'".format(message)
            cursor.execute(query)
            teams = cursor.fetchall()
            if teams:
                await ctx.send("Current teams signed up for **{}**:".format(message))
                for i in teams:
                    msg = msg + "\n" + i[0]

                await ctx.send(msg)
            else:
                await ctx.send("No teams are currently signed up for **{}**.".format(message))

    @bot.command(pass_context=True, name='showopentourneys', help = 'Shows the tournaments open for registration.')
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
    async def showteamsfinal(ctx, *, message):
        conn = connect_db()
        msg = ""

        with conn:
            cursor = conn.cursor()
            query = "SELECT team_name, player1, player2, player3, player4, player5 FROM teams WHERE tourney_name = '{}'".format(message)
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
    async def show_members(ctx, *, message):
        conn = connect_db()
        try:
            team_name, tourney_name = message.split(",")
        except:
            await ctx.send("You forgot to enter a team or tourney name, please try again.")

        with conn:
            cursor = conn.cursor()
            query = '''SELECT player1, player2, player3, player4, player5 FROM teams WHERE team_name = "{}" and tourney_name = "{}"'''.format(team_name, tourney_name.lstrip(' '))

            try:
                cursor.execute(query)
                rows = cursor.fetchall()

                player1 = rows[0][0]
                player2 = rows[0][1]
                player3 = rows[0][2]
                player4 = rows[0][3]
                player5 = rows[0][4]
            except Exception as e:
                await ctx.send("Team name **{}** does not exist in the database. Please try again.".format(message))
            cursor.close()

        await ctx.send("Here are the IGNs for team **{}**:\n{}\n{}\n{}\n{}\n{}".format(team_name, player1, player2, player3, player4, player5))

    @show_members.error
    async def show_members_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You forgot to enter a team name. Please try again.")

    

    @bot.command(pass_context=True, name='opggteam', help = 'Provides you with opgg links for players in a team.')
    
    
    
    async def opgg_team(ctx, *, message):
        conn = connect_db()
        try:
            team_name, tourney_name = message.split(',')
        except:
            await ctx.send("You forgot to enter a team or tourney name, please try again.")

        with conn:
            cursor = conn.cursor()
            query = '''SELECT player1, player2, player3, player4, player5 FROM teams WHERE team_name = "{}" and tourney_name = "{}"'''.format(team_name, tourney_name.lstrip(' '))
            cursor.execute(query)
            rows = cursor.fetchall()

            player1 = rows[0][0].replace(" ", "")
            player2 = rows[0][1].replace(" ", "")
            player3 = rows[0][2].replace(" ", "")
            player4 = rows[0][3].replace(" ", "")
            player5 = rows[0][4].replace(" ", "")
            cursor.close()

            

        link = "https://na.op.gg/multi/query={}%2C{}%2C{}%2C{}%2C{}".format(player1, player2, player3, player4, player5) 
        await ctx.send("Here is the opgg for team **{}**:\n{}".format(team_name, link))

    @opgg_team.error
    async def opgg_team_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You forgot to enter a team name. Please try again.")

    @opgg.error
    async def opgg_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You forgot to enter an ign. Please try again.")


    @bot.command(pass_context=True, name='createtourney', help = 'Allows admin to create a tourney')
    @has_permissions(administrator=True)
    async def create_tourney(ctx, *, message):
        conn = connect_db()

        try:
            name, date, rp, elim = message.split(",")
        except:
            await ctx.send("You are missing a required parameter.")
            return

        with conn:
            cursor = conn.cursor()
            print("creating table")
            query = "CREATE TABLE IF NOT EXISTS tournament_details (tournament_name VARCHAR(25), date VARCHAR(20), rp VARCHAR(5), type VARCHAR(20), primary key(tournament_name))"

            cursor.execute(query)

            query2 = "INSERT INTO tournament_details (tournament_name, date, rp, type) VALUES (%s, %s, %s, %s)"
            tup = (name, date.lstrip(' '), rp.lstrip(' '), elim.lstrip(' '))
            cursor.execute(query2, tup)
            await ctx.send("{} successfully created!".format(name))


    @bot.command(pass_context=True, name='showowner', help = 'Shows owner of a team')
    async def show_owner(ctx, *, message):
        conn = connect_db()
        try:

            team_name, tourney_name = message.split(",")
        except:
            await ctx.send("You forgot to enter a team or tournament name, or a comma between the two. Please try again.")
            return

        with conn:
            cursor = conn.cursor()
            query = '''SELECT disc_user FROM teams where team_name = "{}" and tourney_name = "{}"'''.format(team_name, tourney_name.lstrip(' '))

            try:
                cursor.execute(query)
                resp = cursor.fetchone()
            

                
            except:
                await ctx.send("Unable to find an owner for team **{}** in tournament **{}**, please try again.".format(team_name, tourney_name))
                return

            await ctx.send("The owner for team **{}** is disc user **{}**.".format(team_name, resp[0]))
        

    @bot.command(pass_context=True, name='tournamentdetails', help = 'Allows admin to create a tourney')
    async def tournament_details(ctx, *, message):
        conn = connect_db()
        with conn:
            cursor = conn.cursor()
            query = "SELECT date, rp, type FROM tournament_details where tournament_name = '{}'".format(message)

            try:
                cursor.execute(query)
                resp = cursor.fetchall()
                print(resp)
                date = resp[0][0]
                prize = resp[0][1]
                elim = resp[0][2]
            except:
                await ctx.send("Tournament **{}** does not exist, please try again.".format(message))
                return

            await ctx.send("**{}** is on **{}**. The total prize for the winning team will be **${}**, and is **{}**. ".format(message, date, prize, elim))



    @tournament_details.error
    async def tournament_details_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("You forgot to enter a tourney name. Please try again.")

    
    @bot.command(pass_context=True, name='opensignups', help = 'Allows admin to open signups for a tourney.')
    @has_permissions(administrator=True)
    async def open_signups(ctx, *, message):
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
            cursor.execute(query3, (message, 1))



            cursor.close()

            print("finished")

        ts = time.time()
        today = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        x = datetime.date.today()

        friday = x + datetime.timedelta( (4-x.weekday()) % 7 )
        await ctx.send("Signups for **{}** are now open from **{}** to **{} 11:59 PM EST**. Please visit #towel-boy-help to see how to sign up for a tourney. If you have any questions or need help, please reach out to @rish.".format(message, today, friday))


  



    @bot.command(pass_context=True, name='closesignups', help = 'Allows admin to close signups for a tourney.')
    @has_permissions(administrator=True)
    async def close_signups(ctx, *, message):
        conn = connect_db()

        with conn:
            cursor = conn.cursor()
            
            query = "UPDATE active_tourneys SET active = 0 WHERE tourney_name = '{}'".format(message)
            cursor.execute(query)



            cursor.close()

        await ctx.send("Signups for **{}** are now closed.".format(message))

    
    @bot.command(pass_context=True, name='signup', help = 'Signup for your team for open tourneys.')
    async def signup(ctx, *, message ):

        if message == "":
            await ctx.send("You are missing required parameters. The correct parameters/order = **<tournament name>, <player1>, <player2>, <player3>, <player4>, <player5>, <team name>**. \nPlease try again.")
            return

        try:

            tourney_name, player1, player2, player3, player4, player5, team_name = message.split(",")
        except:
            await ctx.send("You are missing required parameters. The correct parameters/order = **<tournament name>, <player1>, <player2>, <player3>, <player4>, <player5>, <team name>**. \nPlease try again.")
            return

        conn = connect_db()
        with conn:
            cursor = conn.cursor()

            # q = "SELECT ign from solo_signups WHERE tourney_name - '{}'".format(tourney_name.lstrip(' '))
            # cursor.execute(q)
            # igns = cursor.fetchall()[0]

            

            query = "SELECT active FROM active_tourneys WHERE tourney_name = '{}'".format(tourney_name.lstrip(' '))
           
            try:
                cursor.execute(query)
                is_active = cursor.fetchone()[0]

            except Exception as e:
                if 'NoneType' in str(e):

                    await ctx.send("Unable to signup team because **{}** does not exist. Please try again with the correct tourney name.".format(tourney_name.lstrip(' ')))
                    return


            print(is_active)

            if is_active ==1:

         

                query2 = "INSERT INTO teams (disc_user, date, team_name, player1, player2, player3, player4, player5, tourney_name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                ts = time.time()
                date_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                disc_user = str(ctx.message.author)
                tup = (disc_user, date_time, team_name.lstrip(' '), player1.lstrip(' '), player2.lstrip(' '), player3.lstrip(' '), player4.lstrip(' '), player5.lstrip(' '), tourney_name.lstrip(' '))


                #when we run multple tournaments at the same time, need to make it so team_name is not a primary key. need to validate that team_name and tourney_name are not the same instead
                try:
                    cursor.execute(query2, tup)

            
                except:
                    await ctx.send("Team name already exists. Please use a different name, or use the edit command to edit your current team.")
                    return
            
                print("finished")

                cursor.close()
                

                await ctx.send("Successfully signed up **{}**!".format(team_name.lstrip(' ')))
            else:
                await ctx.send("**{}** signups are closed at this time. Please contact @rish or @TimeStoned if you believe this is an error.".format(tourney_name.lstrip(' ')))

    # @signup.error
    # async def signup_error(ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send("You are missing a required parameter. The correct parameters/order = **<tournament name> <player1> <player2> <player3> <player4> <player5> <team name>**. \nPlease try again.")


    @bot.command(pass_context=True, name='removeteam', help = 'Remove a team from a specific tourney.')
    async def remove_team(ctx, *, message ):

        try:

            team_name, tourney_name = message.split(",")
        except:
            await ctx.send("You are missing a required parameter. The correct parameters/order = **<team name>, <tournament name>**")

        conn = connect_db()

        current_disc_user = str(ctx.author)


           
        with conn:

            cursor = conn.cursor()
            query = "SELECT disc_user FROM teams WHERE team_name = '{}' and tourney_name = '{}'".format(team_name.lstrip(' '), tourney_name.lstrip(' '))
            cursor.execute(query)

            try:
                disc_user = cursor.fetchone()[0]
            except:
                await ctx.send("Either team name or tourney name is incorrect. Please try again.")
                return

            if disc_user == current_disc_user or current_disc_user == "rish#3008" or current_disc_user == "TimeStoned#2677":
                
                query2 = '''DELETE FROM teams WHERE team_name = "{}" and tourney_name = "{}"'''.format(team_name.lstrip(' '), tourney_name.lstrip(' '))
                print(query2)
                cursor.execute(query2)
                await ctx.send("Team **{}** was successfully removed from **{}**".format(team_name.lstrip(' '), tourney_name.lstrip(' ')))
                   

            else:
                await ctx.send("You are not able to remove this team, please contact the person who signed up your team to remove it.")
                return
    



    # @remove_team.error
    # async def remove_team_error(ctx, error):
    #     if isinstance(error, commands.MissingRequiredArgument):
    #         await ctx.send("You are missing a required parameter. The correct parameters/order = **<team name> <tournament name>**")


    @bot.command(pass_context=True, name='edit', help = 'Edit/replace members on your team.')
    async def edit(ctx, *, message):
        conn = connect_db()

        try:
            team_name, tourney_name = message.split(",")
        except:
            await ctx.send("You forgot a team or tournament name. Please try again.")
        with conn:
            #when we run multiple tournaments in a week, need to add tourney_name as a parameter and add "and" to the where clause may have to change rows[0]
            cursor = conn.cursor()
            query = '''SELECT disc_user, player1, player2, player3, player4, player5 FROM teams WHERE team_name = "{}" and tourney_name = "{}"'''.format(team_name, tourney_name.lstrip(' '))
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


            if disc_user == current_disc_user or current_disc_user == "rish#3008" or current_disc_user == "TimeStoned#2677":
                await ctx.send('''Here are the members of **{}**: \n1) {}\n2) {}\n3) {}\n4) {}\n5) {}\n\nPlease choose the number corresponding to the player you want to edit and enter the new IGN. For example: 1, newign. 
                '''.format(message, player1, player2, player3, player4, player5))

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel


                try:

                    msg = await bot.wait_for('message', check=check, timeout=30.0)
                    resp = msg.content.split(",")
                    
                except asyncio.TimeoutError:
                    await ctx.send('\nYou took too long, try again.')
                

                print(resp[0])
                resp[1] = resp[1].lstrip(' ')
                print(resp[1])
                if int(resp[0]) == 1:
                    query = "UPDATE teams SET player1 = '{}' WHERE team_name = '{}'".format(resp[1], message)
                    cursor.execute(query)
                    
                    await ctx.send("Successfully replaced **{}** with **{}**!".format(player1, resp[1]))
                    return

                if int(resp[0]) == 2:
                    query = "UPDATE teams SET player2 = '{}' WHERE team_name = '{}'".format(resp[1], message)
                    cursor.execute(query)

                    await ctx.send("Successfully replaced **{}** with **{}**!".format(player2, resp[1]))
                    return

                if int(resp[0]) == 3: 
                    query = "UPDATE teams SET player3 = '{}' WHERE team_name = '{}'".format(resp[1], message)
                    cursor.execute(query)

                    await ctx.send("Successfully replaced **{}** with **{}**!".format(player3, resp[1]))
                    return

                if int(resp[0]) == 4:
                    query = "UPDATE teams SET player4 = '{}' WHERE team_name = '{}'".format(resp[1], message)
                    cursor.execute(query)

                    await ctx.send("Successfully replaced **{}** with **{}**!".format(player4, resp[1]))
                    return

                
                if int(resp[0]) == 5:
                    query = "UPDATE teams SET player5 = '{}' WHERE team_name = '{}'".format(resp[1], message)
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

    @bot.command(pass_context=True, name='signupsolo', help = 'Signup for your team for open tourneys.')
    async def signup_solo(ctx, *, message ):

        if message is None:
            await ctx.send("You are missing required parameters. The correct parameters/order = **<tournament name>, <IGN>, <primary role>, <secondary role>, <solo/duo rank>**. \nPlease try again.")
            return


        try:

            tourney_name, ign, primary, secondary, rank = message.split(",")
        except:
            await ctx.send("You are missing required parameters. The correct parameters/order = **<tournament name>, <IGN>, <primary role>, <secondary role>, <solo/duo rank>**. \nPlease try again.")
            return

        conn = connect_db()
        with conn:
            cursor = conn.cursor()

            q = '''CREATE TABLE IF NOT EXISTS solo_signups (disc_user VARCHAR(75), date VARCHAR(20), tourney_name VARCHAR(25), ign VARCHAR(75), primary_role VARCHAR(25), secondary_role VARCHAR(25), rank VARCHAR(25), picked TINYINT(1))'''
            cursor.execute(q)

            query = "SELECT active FROM active_tourneys WHERE tourney_name = '{}'".format(tourney_name.lstrip(' '))
           
            try:
                cursor.execute(query)
                is_active = cursor.fetchone()[0]

            except Exception as e:
                if 'NoneType' in str(e):

                    await ctx.send("Unable to signup team because **{}** does not exist. Please try again with the correct tourney name.".format(tourney_name.lstrip(' ')))
                    return


            print(is_active)

            if is_active ==1:

         

                query2 = "INSERT INTO solo_signups (disc_user, date, ign, primary_role, secondary_role, rank, tourney_name) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                ts = time.time()
                date_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                disc_user = str(ctx.message.author)
                tup = (disc_user, date_time, ign.lstrip(' '), primary.lstrip(' '), secondary.lstrip(' '), rank.lstrip(' '), tourney_name.lstrip(' '))


                #when we run multple tournaments at the same time, need to make it so team_name is not a primary key. need to validate that team_name and tourney_name are not the same instead
                try:
                    cursor.execute(query2, tup)

            
                except:
                    await ctx.send("Unable to signup **{}** please try again, or contact @rish or @Timestoned for help.")
                    return
            
                print("finished")

                cursor.close()
                

                await ctx.send("Successfully signed up **{}** as a solo player!".format(ign.lstrip(' ')))
            else:
                await ctx.send("**{}** signups are closed at this time. Please contact @rish or @TimeStoned if you believe this is an error.".format(tourney_name.lstrip(' ')))









    @bot.command(pass_context=True, name='showfreeagents', help = 'Shows the current teams signed up for a specific tourney.')
    async def show_free_agents(ctx, *, message):
        conn = connect_db()
        tourney_name = message

        with conn:
            cursor = conn.cursor()
            q = "SELECT ign from solo_signups WHERE tourney_name - '{}'".format(tourney_name.lstrip(' '))
            cursor.execute(q)
            igns = cursor.fetchall()[0]

            print(igns)


            # query = "SELECT ign, primary_role, secondary_role, rank FROM solo_signups WHERE tourney_name = '{}'".format(message)
            # cursor.execute(query)
            # players = cursor.fetchall()
            # if teams:
            #     await ctx.send("Current teams signed up for **{}**:".format(message))
            #     for i in teams:
            #         msg = msg + "\n" + i[0]

            #     await ctx.send(msg)
            # else:
            #     await ctx.send("No teams are currently signed up for **{}**.".format(message)




    bot.run(token)


if __name__ == "__main__":
    main()





