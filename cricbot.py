import json
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # for reply keyboard (sends message)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import *
from time import sleep
import telebot
from telebot import types
import requests

import mysql.connector

from dotenv import load_dotenv
import os
load_dotenv()


try:
    mydb=mysql.connector.connect(
    host=os.getenv('HOST'),
    user=os.getenv('USER'),
    password=os.getenv('PASSWORD'),
    database=os.getenv('DATABASE')
    )
except Exception as e:
    print("Error Occured while connecting to Database - ",e)

mycursor=mydb.cursor()
url = 'https://unofficial-cricbuzz.p.rapidapi.com/matches/list'
querystring = {"matchState":os.getenv('matchState')}
headers = {
	"X-RapidAPI-Key": os.getenv('Key'),
	"X-RapidAPI-Host": os.getenv('APIHost')
}


Globalinnings1=' '
booleanValue=True

matchIdList=[]

InternationalLiveMatches=[]
LeagueLiveMatches=[]
DomesticLiveMatches=[]

def summaryInside(matchId):
    print("Summary - ",matchId)
    url = "https://unofficial-cricbuzz.p.rapidapi.com/matches/get-overs"
    querystring = {"matchId":matchId}   
    responsejson=respfunc(url,querystring)
    innnings1="\n"
    innnings2="\n"
    Status='\n'
    if 'custStatus' in responsejson["miniscore"]:
        Status=responsejson["miniscore"]["custStatus"]
    if 'inningsScores' in responsejson['miniscore'].keys() and (len(responsejson['miniscore']['inningsScores'][0]['inningsScore'])>=1):
        tempinnnings1=responsejson['miniscore']['inningsScores'][0]['inningsScore'][0]        
        innnings1=f'''{tempinnnings1['batTeamShortName']}*   {tempinnnings1['runs']}/{tempinnnings1['wickets']}  {int(tempinnnings1['balls']/6)}.{tempinnnings1['balls']%6}overs\n'''
        global Globalinnings1
        if Globalinnings1==' ' or Globalinnings1!=innnings1:
            Globalinnings1=innnings1
        else:
            return 0
        if len(responsejson['miniscore']['inningsScores'][0]['inningsScore'])==2:
            tempinnnings2=responsejson['miniscore']['inningsScores'][0]['inningsScore'][1]
            innnings2=f'''{tempinnnings2['batTeamShortName']}   {tempinnnings2['runs']}/{tempinnnings2['wickets']}  {int(tempinnnings2['balls']/6)}.{tempinnnings2['balls']%6}overs\n'''
    batsmanStriker="\n"
    batsmanNonStriker="\n"
    bowlerStriker="\n"
    bowlerNonStriker="\n"
    if 'batsmanStriker' in responsejson["miniscore"].keys():
        temp=responsejson["miniscore"]["batsmanStriker"]
        name=temp['name'] if 'name' in temp.keys() else ""                
        runs=temp['runs'] if 'runs' in temp.keys() else 0                
        balls=temp['balls'] if 'balls' in temp.keys() else ""                
        strkRate=temp['strkRate'] if 'strkRate' in temp.keys() else ""                
        batsmanStriker=f"{name}*     r{runs}     b{balls}        Sr{strkRate}\n"
    if 'batsmanNonStriker' in responsejson["miniscore"].keys():
        temp=responsejson["miniscore"]["batsmanNonStriker"]
        name=temp['name'] if 'name' in temp.keys() else ""                
        runs=temp['runs'] if 'runs' in temp.keys() else 0                
        balls=temp['balls'] if 'balls' in temp.keys() else ""                
        strkRate=temp['strkRate'] if 'strkRate' in temp.keys() else ""                
        batsmanNonStriker=f"{name}     r{runs}     b{balls}        Sr{strkRate}\n"
    if 'bowlerStriker' in responsejson["miniscore"].keys():
        temp=responsejson["miniscore"]["bowlerStriker"]
        bowlerStrikerId=temp["id"]
        name=temp['name'] if 'name' in temp.keys() else ""                
        runs=temp['runs'] if 'runs' in temp.keys() else ""                
        overs=temp['overs'] if 'overs' in temp.keys() else ""                
        wickets=temp['wickets'] if 'wickets' in temp.keys() else ""                
        economy=temp['economy'] if 'economy' in temp.keys() else ""                
        bowlerStriker=f"{name}*     o{overs}     r{runs}   w{wickets}   e{economy}\n"
    if 'bowlerNonStriker' in responsejson["miniscore"].keys():
        temp=responsejson["miniscore"]["bowlerNonStriker"]
        bowlerNonStrikerId=temp["id"]                
        name=temp['name'] if 'name' in temp.keys() else ""                
        runs=temp['runs'] if 'runs' in temp.keys() else ""                
        overs=temp['overs'] if 'overs' in temp.keys() else ""                
        wickets=temp['wickets'] if 'wickets' in temp.keys() else ""                
        economy=temp['economy'] if 'economy' in temp.keys() else ""                
        bowlerNonStriker=f"{name}     o{overs}     r{runs}   w{wickets}   e{economy}\n"
        
    if 'crr' in responsejson["miniscore"].keys():
        crr=f'''Current Run Rate - {responsejson["miniscore"]["crr"]}''' 
    else:
        crr=""
    if 'lastWkt' in responsejson["miniscore"].keys():
        lastWkt=f'''Last Wicket - {responsejson["miniscore"]["lastWkt"]}'''
    else:
        lastWkt=""
    if 'curOvsStats' in responsejson["miniscore"].keys():
        curOvsStats=f'''Recent" {responsejson["miniscore"]["curOvsStats"]}'''
    else:
        curOvsStats=""
    if(bowlerStrikerId==bowlerNonStrikerId):
        return innnings1 + innnings2 +Status+"\n\n" + str(crr) +"\n"+ lastWkt + "\n"+ curOvsStats + "\n\n"  +batsmanStriker +batsmanNonStriker + "\n" + bowlerNonStriker    
    return innnings1 + innnings2 +Status+"\n\n"+ str(crr) +"\n"+ lastWkt + "\n"+ curOvsStats + "\n\n"+ batsmanStriker +batsmanNonStriker + "\n" +bowlerStriker +bowlerNonStriker    

def recentover(matchId):
    url = "https://unofficial-cricbuzz.p.rapidapi.com/matches/get-overs"
    querystring = {"matchId":matchId}
    responsejson=respfunc(url,querystring)
    overdetail=responsejson["overSepList"][0]["overSep"][0]
    if 'overSepList' in responsejson.keys():
        if 'overSep' in responsejson["overSepList"][0].keys():
            overSummary=overdetail["overSummary"] if 'overSummary' in overdetail.keys() else " "
            batTeamName=overdetail["batTeamName"] if 'batTeamName' in overdetail.keys() else " "
            score=overdetail["score"] if 'score' in overdetail.keys() else " "
            wickets=overdetail["wickets"] if 'wickets' in overdetail.keys() else " "             
            overRuns=overdetail["runs"] if 'runs' in overdetail.keys() else " "
            bowlerName=overdetail["ovrBowlNames"][0] if 'ovrBowlNames' in overdetail.keys() else " "
            return batTeamName + "  " +str(score)+"/"+str(wickets) +"\n\n"+overSummary + "\n" +bowlerName + " ->  " + str(overRuns) +"runs"
    else:
        return 0

async def summaryRecursiveFunction(message):  
    print("Processed Summary Recursive Function")
    sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    val=(message["from"]["first_name"],'Summary Recursive Function')
    mycursor.execute(sql,val)
    mydb.commit()   
    summaryInsideVar=summaryInside(message.text[3:])
    global booleanValue
    if(booleanValue):
        print(booleanValue)
        if(summaryInsideVar):
            await message.answer(summaryInsideVar)           
        time.sleep(20)
        await summaryRecursiveFunction(message)  

def fun(a,b):    
    for i in a["seriesAdWrapper"]:
        pos=str(i).find('seriesMatches')
        if(pos!=-1):
            b.append(i["seriesMatches"]["matches"][0])
    for i in b:
        matchIdList.append(str(i["matchInfo"]["matchId"]))   
def scoreboard(matchId):
    url = "https://unofficial-cricbuzz.p.rapidapi.com/matches/get-scorecard"
    querystring = {"matchId":matchId}
    return respfunc(url,querystring)
    
def venue(id):
    url = "https://unofficial-cricbuzz.p.rapidapi.com/venues/get-info"
    querystring = {"venueId":id}
    responsejson=respfunc(url,querystring)
    return responsejson["ground"]+ ' ' + responsejson["city"]+ ' ' + responsejson["country"]

def respfunc(url,querystring):
    response = requests.request("GET", url, headers=headers, params=querystring)    
    return response.json()
    
def startfun():
    responsejson=respfunc(url,querystring)
    global International,League, Domestic   
    print("Connected to Server")
    try:
        if(len(responsejson["typeMatches"])>=1):
            fun(responsejson["typeMatches"][0],InternationalLiveMatches)        
        if(len(responsejson["typeMatches"])>=2):
            fun(responsejson["typeMatches"][1],LeagueLiveMatches)             
        if(len(responsejson["typeMatches"])>=3):
            fun(responsejson["typeMatches"][2],DomesticLiveMatches)    
        print("Started")
    except Exception as e:
        print("Error Occured - ",e)
        for i in responsejson:
            print(i+ " => " +responsejson[i])
startfun()


def scorecardClassification(sc):
    print()
    scwickets=sc["wickets"] if 'wickets' in sc.keys() else " "
    initial = f'''Innings -> {sc["inningsId"]}
Batting Team -> {sc["batTeamName"]}({sc["batTeamSName"]})
Score -> {sc["score"]}
wickets -> {sc["wickets"] if 'wickets' in sc.keys() else " "}
overs -> {sc["overs"]}
'''
    batsman="Name\nRuns    Balls   StrikeRate\n"
    for i in sc["batsman"]:
        name=i["name"] if 'name' in i.keys() else ""
        runs=i["runs"] if 'runs' in i.keys() else ""        
        balls=i["balls"] if 'balls' in i.keys() else ""
        try:
            StrikeRate=round((100*runs)/int(balls),2) if balls!="" else 0
        except:
            StrikeRate=0        
        Out=i["outDec"] if 'outDec' in i.keys() else "notout" if balls!="" else "Yet to Bat"  
        if(balls!=""):
            batsman+=f'''{name}    ({Out})
    r{runs}    b{balls}     {StrikeRate}\n'''
        else:
            batsman+=f'''{name}    ({Out})\n'''
        
    bowler="Name\nOvers   Runs  Wickets     Economy\n"
    for i in sc["bowler"]:
        name=i["name"] if 'name' in i.keys() else ""
        overs=i["overs"] if 'overs' in i.keys() else ""
        runs=i["runs"] if 'runs' in i.keys() else 0
        wickets=i["wickets"] if 'wickets' in i.keys() else 0
        economy=i["economy"] if 'economy' in i.keys() else "--"        
        bowler+=f'''{name}
    o{overs}      r{runs}       w{wickets}            {economy}\n'''
    LegByes=sc["extras"]["legByes"] if 'legByes' in sc['extras'].keys() else 0
    Byes=sc["extras"]["byes"] if 'byes' in sc['extras'].keys() else 0
    Wides=sc["extras"]["wides"] if 'wides' in sc['extras'].keys() else 0  
    totalextras=sc["extras"]["total"] if 'total' in sc['extras'].keys() else 0
    
    extras=f'''LegByes  Byes   Wides   Total\n      {LegByes}            {Byes}          {Wides}         {totalextras}'''
    
    return f'''{initial}\n{batsman}\n\n{bowler}\n{extras}'''
    





keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('Ok', 'Bye')
botTele = telebot.TeleBot(os.getenv('BOT_TOKEN'))

t = Bot(token=os.getenv('BOT_TOKEN'))
bot = Dispatcher(t)

format=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
format.row("International","League","Domestic")

@bot.message_handler(commands=["stop"])
async def stopProgram(message):
    print("stop program triggered, Username => " + message["from"]["first_name"])
    sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    val=(message["from"]["first_name"],'Stop Program Triggered')
    mycursor.execute(sql,val)
    mydb.commit()
    time.sleep(2)
    await message.answer("Thanks for using our CricBot Live")
    global booleanValue       
    booleanValue=False


@bot.message_handler(commands=['namaste', 'vanakam'])
async def send_welcome(message):
    print("Namaste, Username => " + message["from"]["first_name"]) 
    sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    val=(message["from"]["first_name"],'NAMASTE')
    mycursor.execute(sql,val)
    mydb.commit()
    await message.answer("Hello, Welcome to CricketLive Score")
    botTele.send_message(message.chat.id, 'Please select your Cricket Format', reply_markup=format)

@bot.message_handler(commands=['int'])
async def inlinekeyboardMatchesList(message,typelist):
    print(message.text + ", Username => "+message["from"]["first_name"])
    sql="INSERT INTO POST_SEARCH (NAME,DESCRIPTION) VALUES(%s,%s)"
    val=(message["from"]["first_name"],message.text)
    mycursor.execute(sql,val)
    mydb.commit()
    newkb=InlineKeyboardMarkup(resize_keyboard=True)    
    for i in typelist:        
        s1=i["matchInfo"]["seriesName"]
        s2=i["matchInfo"]["matchDesc"]        
        nametext=i["matchInfo"]["seriesName"] + ' ' + i["matchInfo"]["matchDesc"]        
        a = InlineKeyboardButton(text=nametext, callback_data=i["matchInfo"]["matchId"])
        newkb.add(a)
   
    await message.answer(f"List of Matches : ",reply_markup=newkb)   


@bot.message_handler(commands=["sc" + i for i in matchIdList])
async def botscoreboard(message):
    print("Scoreboard - "+message.text[3:]+", Username => " + message["from"]["first_name"]) 
    sql="INSERT INTO POST_SEARCH(NAME,DESCRIPTION) VALUES(%s,%s)"
    val=(message["from"]["first_name"],"Scoreboard -  "+message.text[3:])
    mycursor.execute(sql,val)
    mydb.commit()
    score=scoreboard(message.text[3:])
    if "scorecard" in score.keys():        
        if(len(score["scorecard"])>=1):
            innnings1=scorecardClassification(score["scorecard"][0])
            await message.answer(innnings1)
        if(len(score["scorecard"])>=2):
            innnings2=scorecardClassification(score["scorecard"][1])
            await message.answer(innnings2)
            
@bot.message_handler(commands=["su" + i for i in matchIdList])
async def Summary(message):
    print("Summary - "+message.text[3:]+", Username => " + message["from"]["first_name"]) 
    sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    val=(message["from"]["first_name"],'Summary - '+message.text[3:])
    mycursor.execute(sql,val)
    mydb.commit()
    global booleanValue
    booleanValue=True
    await summaryRecursiveFunction(message)
    
@bot.message_handler(commands=["ro" + i for i in matchIdList])
async def RecentOver(message):
    print("Recent - "+message.text[3:]+", Username => " + message["from"]["first_name"])  
    sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    val=(message["from"]["first_name"],'Recent - '+message.text[3:])
    mycursor.execute(sql,val)
    mydb.commit()  
    temprecentover=recentover(message.text[3:])
    if(temprecentover):
        await message.answer(temprecentover)
    else:
        await message.answer("Unable to connect to server")           

        

def matchInfofun(callData,typelist):
    for i in typelist:
        if(callData==str(i["matchInfo"]["matchId"])):
            vartemp=i["matchInfo"]["seriesName"] + ' ' + i["matchInfo"]["matchDesc"]+"\n\nMatch Id -> "+str(i["matchInfo"]["matchId"])+"\nSeries Id -> "+str(i["matchInfo"]["seriesId"])+"\nMatch Format -> "+i["matchInfo"]["matchFormat"]+"\nState -> "+i["matchInfo"]["state"]+"\nStatus -> "+i["matchInfo"]["status"]+"\nVenue ->"+venue(i["matchInfo"]["venueInfo"]["id"])+"\n\nScoreboard -> "+"/sc"+str(i["matchInfo"]["matchId"])
            summary="\nLiveScores -> " + "/su" + str(i["matchInfo"]["matchId"])
            LiveScores="\nSummary -> " + "/ro" + str(i["matchInfo"]["matchId"])
            return vartemp +summary +LiveScores
    

    
@bot.callback_query_handler()
async def matchScore(call: types.CallbackQuery):
    print("MatchInfo - "+call.data)
    # sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    # val=(message["from"]["first_name"],'MatchInfo - '+call.data)
    # mycursor.execute(sql,val)
    # mydb.commit()
    if(matchInfofun(call.data,InternationalLiveMatches)):
        await call.message.answer(matchInfofun(call.data,InternationalLiveMatches))
    elif(matchInfofun(call.data,LeagueLiveMatches)):
        await call.message.answer(matchInfofun(call.data,LeagueLiveMatches))        
    else:
        await call.message.answer(matchInfofun(call.data,DomesticLiveMatches))
     
@bot.message_handler(commands=['International'])
async def International(message):
    print("International "+", Username" + message["from"]["first_name"])     
    sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    val=(message["from"]["first_name"],'International Format')
    mycursor.execute(sql,val)
    mydb.commit()   
    await inlinekeyboardMatchesList(message,InternationalLiveMatches)

@bot.message_handler(commands=['League'])
async def League(message):
    print("League, Username => " + message["from"]["first_name"])   
    sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    val=(message["from"]["first_name"],'League Format')
    mycursor.execute(sql,val)
    mydb.commit()     
    await inlinekeyboardMatchesList(message,LeagueLiveMatches)
    
@bot.message_handler(commands=['Domestic'])
async def Domestic(message):
    print("Domestic, Username => " + message["from"]["first_name"])  
    sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    val=(message["from"]["first_name"],'Domestic Format')
    mycursor.execute(sql,val)
    mydb.commit()         
    await inlinekeyboardMatchesList(message,DomesticLiveMatches) 

@bot.message_handler(commands=['help'])
async def help(message:types.Message):
    print("Help, Username => " + message["from"]["first_name"])   
    sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
    val=(message["from"]["first_name"],'Help')
    mycursor.execute(sql,val)
    mydb.commit()        
    await message.answer(f'''Commands : \nTo start with Bot -> /namaste.\nTo View the International Matches List -> /International.\nTo View the League Matches List -> /League.\nTo View the Domestic Matches List -> /Domestic
To View the Scoreboard (if matchId=123) -> /sc123
To View the Summary (if matchId=123) -> /su123
To View the Live Score (if matchId=123) -> /ro123''')

@bot.message_handler(content_types=['text'])
async def send_text(message):
    if message.text.lower() =='international':
        await inlinekeyboardMatchesList(message,InternationalLiveMatches)        
    elif message.text.lower() =='league':
        await inlinekeyboardMatchesList(message,LeagueLiveMatches)
    elif message.text.lower() == 'domestic':
        await inlinekeyboardMatchesList(message,DomesticLiveMatches)
    else:
        print("Unknown Message -  "+message.text+", Username => " + message["from"]["first_name"])
        sql="INSERT INTO POST_SEARCH(Name,DESCRIPTION)VALUES(%s,%s)"   
        val=(message["from"]["first_name"],'Unknown Message requested')
        mycursor.execute(sql,val)
        mydb.commit()   
        await message.answer("Hi Welcome to CricketLive Score.\nTo Start with type command /namaste.\nFor any kind of help type command /help")
       
executor.start_polling(bot)
