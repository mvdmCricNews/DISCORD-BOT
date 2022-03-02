import requests
import nextcord
from nextcord import Interaction, SlashOption

TOKEN="<token>" #Enter Discord bot client token here

client = nextcord.Client()

import mysql.connector
mycon=mysql.connector.connect(host="localhost", user="root", passwd="12345")

if(mycon.is_connected()):
    print("\nConnection Secure\n")
else:
    print("\nConnection Unsecure, Please Try Again\n")


cursor=mycon.cursor()

num_emoji_list=["0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
def O_Reset():
    url = "https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/allplayers.txt"
    req = requests.get(url, 'html.parser')
    player_record=req.text.split("\n")
    reset_database("reset")
    for i in player_record:
        try:
            p1=i.split("datetime.date(")[0]
            p2=i.split("datetime.date(")[1].replace("))","").split(",")
            p2="-".join(p2).replace(" ","") 
        except:
            break
        command="insert into allplayers values"+p1[5:]+'"'+p2+'");'
        cursor.execute(command)
        mycon.commit()
    
    url = "https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/teamstats.txt"
    req = requests.get(url, 'html.parser')
    player_record=req.text.split("\n")
    for i in player_record:
        try:
            command="insert into teamstats values"+i.split("  ")[1]+";"
        except:
            break
        cursor.execute(command)
        mycon.commit()

    url = "https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/playerrecords.txt"
    req = requests.get(url, 'html.parser')
    player_record=req.text.split("\n")
    for i in player_record:
        try:
            command="insert into playerrecords values"+i.split("  ")[1]+";"
        except:
            break
        cursor.execute(command)
        mycon.commit()
    print("\nFinished Extracting data from online\n")



def reset_database(ty="start"):
    cursor.execute("show databases like 'ipl';")
    database_exist_check=cursor.fetchone()

    if(ty=="reset"):
        cursor.execute("drop database ipldiscord;")
    if(database_exist_check is None or ty=="reset"):
        #print("\nCreating Database and Subsequent tables\n")
        cursor.execute("create database ipldiscord;")
        cursor.execute("use ipldiscord;")
        cursor.execute("""

create table AllPlayers
(
TeamName varchar(50) NOT NULL,
PlayerName varchar(50) PRIMARY KEY,
ShirtNumber int(4),
Economy float(5,2), 
BattingAvg float(5,2), 
Role varchar(25) NOT NULL, 
HighestScore int(4), 
MostWickets int(4), 
Debut date
);

""")
    
        cursor.execute("""

create table Teamstats
(TeamName varchar(50) NOT NULL,
YearsPlayed int(3) NOT NULL,
Wins int(4) NOT NULL, 
FinalsLost int(4) NOT NULL, 
Captain varchar(25), 
Owner varchar(25)
);

""")
    
        cursor.execute("""

create table PlayerRecords 
(TeamName varchar(50), 
PlayerName varchar(50) PRIMARY KEY, 
ShirtNumber int(3), 
Salary float(10,2) NOT NULL, 
Role varchar(30),
Age int(3) NOT NULL,
Record varchar(50),
FOREIGN KEY (PlayerName) REFERENCES AllPlayers(PlayerName)
);

""")
    else:
        cursor.execute("use ipldiscord;")

O_Reset()



def findplayer(name):
    query="select * from allplayers where PlayerName='{}'".format(name)
    cursor.execute(query)
    record=cursor.fetchone()
    return record

def findrecord(rec):
    query="select * from playerrecords where PlayerName='{}'".format(rec)
    cursor.execute(query)
    record=cursor.fetchone()
    return record

def findteam(team):
    query="select * from allplayers where teamname='{}'".format(team)
    cursor.execute(query)
    record1=cursor.fetchall()
    query="select * from teamstats where teamname='{}'".format(team)
    cursor.execute(query)
    record2=cursor.fetchone()
    return (record1,record2)

def displayteamstats():
    query="select * from teamstats "
    cursor.execute(query)
    record=cursor.fetchall()
    return record


emoji_list={"CSK":"<:IPL_CSK_LOGO:944942159650488330>","DC":"<:IPL_DC_LOGO:944942162158698576>","KKR":"<:IPL_KKR_LOGO:944942537204973588>","MI":"<:IPL_MI_LOGO:944942160741027911>","PK":"<:IPL_PK_LOGO:944942835134787584>","RCB":"<:IPL_RCB_LOGO:944942159667281941>","RR":"<:IPL_RR_LOGO:944942163282780271>","SRH":"<:IPL_SRH_LOGO:944943010079211560>","IPL":"<:IPL_MAIN_LOGO:948536566526119956>"}
   # async def callback(self,interaction:nextcord.Interaction):

class Player_Num_Button(nextcord.ui.Button):
    def __init__(self,label,id,team):
        self.team=team
        self.id=id 
        super().__init__(
                        custom_id=id,
                        label=label,
                        style=nextcord.ButtonStyle.gray)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.edit_message(embeds=displayplayer_discordembed(self.id),view =Team_View(self.team)) 

class Player_Team_Button(nextcord.ui.Button):
    def __init__(self,emoji,id):
        self.id=id 
        super().__init__(
                        custom_id=id,
                        emoji=emoji,
                        label="All Teams",
                        style=nextcord.ButtonStyle.blurple)

    async def callback(self, interaction : nextcord.Interaction):

        await interaction.response.edit_message(embeds=displayteams_discordembed(),view=Team_View(["CSK","DC","KKR","MI","PK","RCB","RR","SRH"]))

class Full_Team_View(nextcord.ui.View):
    def __init__(self,player_list,team_name):
        super().__init__()
        self.add_item(Player_Team_Button(emoji_list["IPL"],"IPLTeams"))
        for i in range (len(player_list)):
            self.add_item(Player_Num_Button(num_emoji_list[i],player_list[i],team_name))
        

class Team_Button(nextcord.ui.Button):
    def __init__(self,team):
        self.team=team
        super().__init__(
                        custom_id=team,
                        label=''.join(c for c in team if c.isupper()),
                        emoji=emoji_list[''.join(c for c in team if c.isupper())],
                        style=nextcord.ButtonStyle.gray)

    async def callback(self, interaction: nextcord.Interaction):
        teamname=self.team
        if self.team=="CSK":
            teamname="Chennai Super Kings"
        elif self.team=="DC":
            teamname="Delhi Capitals"
        elif self.team=="KKR":
            teamname="Kolkata Knight Riders"
        elif self.team=="MI":
            teamname="Mumbai Indians"
        elif self.team=="PK":
            teamname="Punjab Kings"
        elif self.team=="RCB":
            teamname="Royal Challengers Bangalore"
        elif self.team=="RR":
            teamname="Rajasthan Royals"
        elif self.team=="SRH":
            teamname="Sunrisers Hyderabad"
        await interaction.response.edit_message(embeds=[displayteam_discordembed(teamname)[0]],view=Full_Team_View(displayteam_discordembed(teamname)[1],teamname))

class Team_View(nextcord.ui.View):
    
    def __init__(self,team):
        super().__init__()
        if isinstance(team, list):
            for i in team:
                self.add_item(Team_Button(i))
            
        else:
            self.add_item(Team_Button(team))

    


def displayplayer_discordembed(player_inp):
    if findplayer(player_inp) is None:
        return None
    else:
        player=findplayer(player_inp)
        team={}

        if player[0]=="Chennai Super Kings":
            team["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_CSK_LOGO.png"
            team["color"]=0xF9CD05

        elif player[0]=="Delhi Capitals":
            team["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_DC_LOGO.png"
            team["color"]=0x282968

        elif player[0]=="Kolkata Knight Riders":
            team["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_KKR_LOGO.png"
            team["color"]=0x3A225D

        elif player[0]=="Mumbai Indians":
            team["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_MI_LOGO.png"
            team["color"]=0x004BA0

        elif player[0]=="Punjab Kings":
            team["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_PK_LOGO.png"
            team["color"]=0xED1B24

        elif player[0]=="Royal Challengers Bangalore":
            team["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_RCB_LOGO.png"
            team["color"]=0xD1AB3E

        elif player[0]=="Rajasthan Royals":
            team["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_RR_LOGO.png"
            team["color"]=0xE73895

        elif player[0]=="Sunrisers Hyderabad":
            team["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_SRH_LOGO.png"
            team["color"]=0xFF822A


        
        Shirtnum=player[2]
        Econ=player[3]
        BatAvg=player[4]

        type={}
        if player[5]=="WicketKeeper":
            type["desc"]="Wicket Keeper"
            type["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/playertypeimages/Wicketkeeper.png"

        elif player[5]=="Batsman":
            type["desc"]="Batsman"
            type["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/playertypeimages/Batsman.png"

        elif player[5]=="AllRounder":
            type["desc"]="All Rounder"
            type["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/playertypeimages/AllRounder.png"

        elif player[5]=="Bowler":
            type["desc"]="Bowler"
            type["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/playertypeimages/Bowler.png"

        else:
            type["desc"]="Player"
            type["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/playertypeimages/Player.png"


        Hisco=player[6]
        Mstwick=player[7]
        Debdate=player[8]
       


        player_embed=nextcord.Embed(title=player[1], description=type["desc"], color=team["color"])
        player_embed.set_author(name=player[0], icon_url=team["icon"])
        player_embed.set_thumbnail(url=type["icon"])
        player_embed.add_field(name="  Shirt Number <:shirt_number_blank:944854502887010335>  ", value=Shirtnum, inline=False)
        player_embed.add_field(name="  Economy <:cricket_ball:944854793581637673>  ", value=Econ, inline=False)
        player_embed.add_field(name="  Batting Average <:cricket_bat:944854523745271828>  ", value=BatAvg, inline=False)
        player_embed.add_field(name="  Highest Score 🏅  ", value=Hisco, inline=False)
        player_embed.add_field(name="  Most Wickets <:wickets:944854536676319232>  ", value=Mstwick, inline=False)
        player_embed.set_footer(text=f"Debut Date 📅: {Debdate}")
        
        if findrecord(player_inp) is not None:
            record=findrecord(player_inp)
            record_embed=nextcord.Embed(title=player[1], description=type["desc"], color=team["color"])
            record_embed.set_author(name=player[0], icon_url=team["icon"])
            record_embed.set_thumbnail(url="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/Cricket_Record.png")
            record_embed.add_field(name="  Salary 💰  ", value=record[3], inline=False)
            record_embed.add_field(name="  Age 🎂  ", value=record[5], inline=False)
            record_embed.add_field(name="  Record 🏆  ", value=record[6], inline=False)
            return [player_embed,record_embed]
        else:
            return[player_embed]

@client.slash_command(force_global=True,description="List all the IPL teams")
async def teams_list(
    interaction: Interaction,
    
):
    await interaction.response.send_message(embeds=displayteams_discordembed(),view=Team_View(["CSK","DC","KKR","MI","PK","RCB","RR","SRH"])) 


@client.slash_command(force_global=True,description="Display Information about the bot")
async def bot_info(
    interaction: Interaction,
    
):

    info_embed=nextcord.Embed(title="Bot Information", description="This is a bot in accordance to the mvdmCricNews\n\nYou can find all of the information and code in the link down below", color=0x00237D)
    info_embed.set_thumbnail(url="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_MAIN_LOGO.png")
    info_embed.add_field(name="GitHub Link:", value="https://github.com/mvdmCricNews?tab=repositories",inline=False)
    info_embed.set_footer(text="Bot made by DSR / Quickdev")
    await interaction.response.send_message(embeds=[info_embed]) 


@client.slash_command(force_global=True,description="Display Player Stats")
async def player_info(
    interaction: Interaction,
    player_inp: str = SlashOption(
        name="player_name",
        description="The player to be found",
        required=True
    ),
):
    player=findplayer(player_inp)
    await interaction.response.send_message(embeds=displayplayer_discordembed(player_inp),view =Team_View(player[0]))

def displayteam_discordembed(team_inp):
    global num_emoji_list
    player_list=[]
    if findteam(team_inp) is None:
        return None
    else:
        team=findteam(team_inp)[1]
        teamplayers=findteam(team_inp)[0]
        team_dic={}

        if team[0]=="Chennai Super Kings":
            team_dic["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_CSK_LOGO.png"
            team_dic["color"]=0xF9CD05

        elif team[0]=="Delhi Capitals":
            team_dic["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_DC_LOGO.png"
            team_dic["color"]=0x282968

        elif team[0]=="Kolkata Knight Riders":
            team_dic["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_KKR_LOGO.png"
            team_dic["color"]=0x3A225D

        elif team[0]=="Mumbai Indians":
            team_dic["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_MI_LOGO.png"
            team_dic["color"]=0x004BA0

        elif team[0]=="Punjab Kings":
            team_dic["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_PK_LOGO.png"
            team_dic["color"]=0xED1B24

        elif team[0]=="Royal Challengers Bangalore":
            team_dic["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_RCB_LOGO.png"
            team_dic["color"]=0xD1AB3E

        elif team[0]=="Rajasthan Royals":
            team_dic["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_RR_LOGO.png"
            team_dic["color"]=0xE73895

        elif team[0]=="Sunrisers Hyderabad":
            team_dic["icon"]="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_SRH_LOGO.png"
            team_dic["color"]=0xFF822A

        team_embed=nextcord.Embed(title="Owner", description=team[5], color=team_dic["color"])
        team_embed.set_author(name=team[0], icon_url=team_dic["icon"])
        team_embed.set_thumbnail(url=team_dic["icon"])
        team_embed.add_field(name="  Years Played 📆  ",value=team[1])
        team_embed.add_field(name="  Wins <:gx_check:722495917017792552>  ",value=team[2])
        team_embed.add_field(name="  Finals Lost ❌  ",value=team[3])
        team_embed.add_field(name="Players 🧍:",value="_ _")
        for i in range(len(teamplayers)):
            player_list.append(teamplayers[i][1])
            if teamplayers[i][5]=="WicketKeeper":
                p="Wicket Keeper"
            elif teamplayers[i][5]=="AllRounder":
                p="All Rounder"
            elif teamplayers[i][5]=="Batsman":
                p="Batsman"
            elif teamplayers[i][5]=="Bowler":
                p="Bowler"
            else:
                p="Player"
            
            team_embed.add_field(name=f"\n{num_emoji_list[i]} {teamplayers[i][1]}\n", value="_ _\n",inline=False)
        team_embed.set_footer(text=f"Captain : {team[4]}")
        return team_embed,player_list

def displayteams_discordembed():
    global emoji_list

    teams_embed=nextcord.Embed(title="IPL Teams:", description="_ _", color=0x00237D)
    teams_embed.set_thumbnail(url="https://raw.githubusercontent.com/mvdmCricNews/REPO/main/Data/logo/IPL_MAIN_LOGO.png")
    teams_embed.set_footer(text="List of all the Teams")
    for i in displayteamstats():

        if i[0]=="Chennai Super Kings":
            teams_embed.add_field(name=f"{emoji_list['CSK']} {i[0]}", value="\n_ _\n",inline=False)

        elif i[0]=="Delhi Capitals":
            teams_embed.add_field(name=f"{emoji_list['DC']} {i[0]}", value="\n_ _\n",inline=False)

        elif i[0]=="Kolkata Knight Riders":
            teams_embed.add_field(name=f"{emoji_list['KKR']} {i[0]}", value="\n_ _\n",inline=False)

        elif i[0]=="Mumbai Indians":
            teams_embed.add_field(name=f"{emoji_list['MI']} {i[0]}", value="\n_ _\n",inline=False)

        elif i[0]=="Punjab Kings":
            teams_embed.add_field(name=f"{emoji_list['PK']} {i[0]}", value="\n_ _\n",inline=False)

        elif i[0]=="Royal Challengers Bangalore":
            teams_embed.add_field(name=f"{emoji_list['RCB']} {i[0]}", value="\n_ _\n",inline=False)

        elif i[0]=="Rajasthan Royals":
            teams_embed.add_field(name=f"{emoji_list['RR']} {i[0]}", value="\n_ _\n",inline=False)

        elif i[0]=="Sunrisers Hyderabad":
            teams_embed.add_field(name=f"{emoji_list['SRH']} {i[0]}", value="\n_ _\n",inline=False)

    return [teams_embed]



client.run(TOKEN)