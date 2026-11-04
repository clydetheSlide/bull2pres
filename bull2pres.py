#!/usr/bin/env python
# File: bull2pres.py
#
''' Generate an openSong set from
    a txt-only version of the bulletin.
    It keys off a set of expected headings
    to determine openSong slides.
    It is not intended to make a perfect set,
    but rather to be a good start.'''

Usage="bull2pres.py [-t] [name1 name2]\n \
  where:\n \
    -t          don\'t use the GUI\n \
                (which requires both file name arguments) \n\
     name1       is the text form of the bulletin\n \
and name2       is used to name both the set\n \
                and the XML file to be generated.\n \
    -h          prints the help message\n"

# V1 Sep 1, 2021
#   - conceptual version that assumes Sylvia's bulletin will
#       consist of the same sections in the same format
#       so I can look for specific phrases and add the
#       openSong XML tags to the text
#
# Nov 2021
#   - It is obvious now that the assumption that Sylvia will be consistent
#     is only slightly useful. But at least this provides a start.
#     It has been and I expect will continue to be necessary
#     to add more section identifiers (see enum section)
#     and be careful to review the bulletin to make changes due this
#     erroneous assumption.
#
# V1.1 Dec10, 2021
#   - after several small alterations, save current version as a subversion
#
# V1.2 Dec30, 2021
#   - after several small alterations, save current version as a subversion
#
# V1.3 Feb1, 2022
#   - added announcements loop and Great Thanksgiving ritual
#
# V2.0 Feb10, 2022
#   - added gui
#   - added psalter similar to song
#       - it expects to find the "song" type file 
#          in ../Songs/UMHymnal/Psalter/#.xml
#
# V2.1 Feb26, 2022
#   - remove the multiline formatting in text blocks to 
#      allow OpenSong to do it
#   - recognize and format call and response sections
#
# V2.2 Jun24, 2023
#   - made Communion options a menu selection
#       o UMHymnal ritual A
#       o UMHymnal ritual A responses with prompts
#       o UMHymnal ritual A with Gretchen Nelson mods
#       o custom ritual
#
# V2.3 Apr16, 2025
#       o added error messages to psalter method
#       o minor mods to keyword list
#
# V2.4 Apr17, 2025
#   - look for songs in database
#   - assumes Songs, and Hymns are in ../Songs/{.,UMH,FWS}
#
# V2.4.3 Jul17, 2025
#   - modded PSALTER to treat as regular SCRIPTURE if no page no included
#   - Singing and Sending acts like SONG followed by LASTLINE
#       @ it uses a song name and number
#       @ but if not provided, it uses the hard-wired song
#
# V2.4.4 Sep4, 2025
#   - slight mods due to pratices of new minister (Kerry)
#
# V2.5 Apr2, 2026
#   - allow verses to be declared for songs
#   - allow responses to be declared for Psalter
#   - and more slight mods for practices of minister
#
# TODO:
#   - make communion options accessible from the command line (in addition to the menu)
#   - detect when Meditation is a one-liner rather than a two liner
#   - detect when Blessing and Sending has text
#   - build options to use as a filter
#   - add options to apply specified rule to apply as a filter
#   - "Prayer of ..." could be generic and use whatever the object is
#   - if Singin and Sending denotes a particular hymn, use it
#      otherwise use the default

import sys
from enum import Enum, auto
from textwrap import wrap

import os, io
from tkinter import *
#from tkinter.tix import *
#from tkinter.constants import *
import tkinter.filedialog
from argparse import ArgumentParser, Action
import pathlib
from subprocess import Popen,PIPE,call,run

SONGS = '../Songs/'  # presumes this procedure is called from Sets 
def initialize_old(xml,xmlname):
    xml.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n \
<set name=\"%s\"> \n  <slide_groups> \n'%xmlname)
    xml.write('  <slide_group name=\"welcome\" type=\"song\" presentation=\"\" path=\"\"/> \n\n')
    xml.write(' <slide_group name=\"Announcement loop\" type=\"custom\" print=\"true\" seconds=\"8\" loop=\"true\" transition=\"0\">')
    xml.write('  <title>Announcements</title>\n <subtitle></subtitle>\n <notes></notes>\n <slides>\n <slide>\n')
    xml.write('  <body>place announcement here\n\n some data, 2022\n some time\nContact person: somebody\n')
    xml.write(' </body></slide></slides></slide_group>\n\n')
    xml.write('  <slide_group name=\"Vision\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\"> \n')
    xml.write('  <title/> \n <subtitle/> \n <notes/> \n <slides> \n <slide> \n')
    xml.write('  <body>The Vision of Wesley United Methodist Church is to serve all people with the love of Jesus Christ.</body></slide></slides></slide_group> \n\n')
    xml.write('  <slide_group name=\"Gather\" type=\"custom\" print=\"true\" seconds="0" loop=\"false\" transition=\"0\"> \n')
    xml.write('  <title/> \n <subtitle/> \n <notes/> \n <slides> \n <slide> \n')
    xml.write('  <body>Gather and Spend Time with God Together \n\n \
Day by Day, as they spent much time together in temple, they broke bread at home and ate their food with glad and generous hearts.\n Acts 2:46</body></slide></slides></slide_group> \n\n')

def vision(xml):
    xml.write('  <slide_group name=\"Vision\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\"> \n')
    xml.write('  <title/> \n <subtitle/> \n <notes/> \n <slides> \n <slide> \n')
    xml.write('  <body>The Vision of Wesley United Methodist Church is to serve all people with the love of Jesus Christ.</body></slide></slides></slide_group> \n\n')

def gather(xml):
    xml.write('  <slide_group name=\"Gather\" type=\"custom\" print=\"true\" seconds="0" loop=\"false\" transition=\"0\"> \n')
    xml.write('  <title/> \n <subtitle/> \n <notes/> \n <slides> \n <slide> \n')
    xml.write('  <body>Gather and Spend Time with God Together \n\n \
Day by Day, as they spent much time together in temple, they broke bread at home and ate their food with glad and generous hearts.\n Acts 2:46</body></slide></slides></slide_group> \n\n')

def initialize(xml,xmlname):
    xml.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n \
<set name=\"%s\"> \n  <slide_groups> \n'%xmlname)
    xml.write('  <slide_group name=\"welcome\" type=\"song\" presentation=\"\" path=\"\"/> \n\n')
    xml.write(' <slide_group name=\"Announcement loop\" type=\"custom\" print=\"true\" seconds=\"8\" loop=\"true\" transition=\"0\">')
    xml.write('  <title>Announcements</title>\n <subtitle></subtitle>\n <notes></notes>\n <slides>\n <slide>\n')
    xml.write('  <body>place announcement here\n\n some data, 2022\n some time\nContact person: somebody\n')
    xml.write(' </body></slide></slides></slide_group>\n\n')
    vision(xml)
    #gather(xml)

def customB4(title,xml):
    ''' the title as a heading'''
    xml.write("<slide_group name=\"%s\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\">\n"%title)
    xml.write(" <title/>\n <subtitle/>\n <notes/>\n <slides>\n <slide>\n")
    xml.write("<body>%s\n"%title)

def custom(title,xml):
    ''' the title as a heading'''
    xml.write("<slide_group name=\"%s\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\">\n"%title)
    xml.write(" <title>%s</title>\n <subtitle/>\n <notes/>\n <slides>\n <slide>\n"%title)
    xml.write("<body>%s\n"%title)

def customH2T(title,xml):
    ''' just the title, no heading '''
    xml.write("\n<slide_group name=\"%s\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\">\n"%title)
    xml.write(" <title>%s</title>\n <subtitle/>\n <notes/>\n <slides>\n <slide>\n"%title)
    xml.write("<body>\n")

def endslide(xml):
    xml.write("</body></slide></slides></slide_group>\n\n")

def scripture(line,key,xml):
    ''' scripture text has the book and verse in the line'''
    booknverse = line[len(key):].strip()
    custom(key,xml)
    xml.write("\n%s\n"%booknverse)
    endslide(xml)

def psalter(line,key,xml):
    ''' type= psalter; extract the title and page '''
    # presumes the title is on the same line as the key
    # ie  Psalter   Psalm 1  UMH Page 738
    # ie  Psalter   Psalm 1  UMH 738
    # ie  Psalter   Psalm 1  UMH 738 R. 1
    # ie  Psalter   Psalm 1  UMH Page 738 R. 1
    title = line[len(key):].strip()
    path=''
    umh=title.find("UMH")
    nindex=-999
    if umh > 0:
        nindex = 1
        if title[:umh].find("Page") > 0:
            nindex=2
        nums = title[umh:].strip().split(maxsplit=nindex+2)
        num = nums[nindex]
        if len(nums) >nindex+1: resp = nums[nindex+1]
        else: resp=""
    path='UMHymnal/Psalter/'
    try:
        xml.write("\n  <slide_group name=\"%s.xml\" type=\"song\" presentation=\"%s\" path=\"%s\"/>\n\n"%(num,resp,path))
    except UnboundLocalError as e:
        print(e)
        print("Error in psalter, cannot parse title for page number")
        if options.verbose: print(title)
        if options.verbose: print(title[umh:].strip().split())
        if options.verbose: print("looked for num as %dth element"%nindex);
        print("     Used simply as scripture in set.");
        scripture(line,key,xml)

def song(line,key,xml,verse=""):
  ''' type= song; extract the title '''
  # presumes the title is on the same line as the key
  # eg. line like
  # Hymn	When I Survey the Wondrous Cross 	UMH 298 
  # Hymn	When I Survey the Wondrous Cross v. 1, 3	UMH 298 
  try:
    titlel = line[len(key):].strip()
    if options.verbose: print("SONG: title=%s, len=%d"%(titlel,len(titlel)))
    if len(titlel)<1:
        return -1
    path=''
    titlel=titlel.replace("TFWS","FWS")  # just in case
    umh=titlel.find("UMH")
    if umh > 0:
        title=titlel[:umh].strip()
        path='UMHymnal/'
        hnum = titlel[umh:].split()[1]
        averse = title[:umh].find("v.")
        if averse < 0: averse = title[:umh].find("Refrain")
        if averse < 0: averse = title[:umh].find("Chorus")
        if averse > 0:
            verse = title[averse:]
            title = title[:averse]
    else:
        umh=titlel.find("FWS")
        if umh > 0:
            title=titlel[:umh].strip()
            path='FWS/'
            hnum = titlel[umh:].split()[1]
            averse = title[:umh].find("v.")
            if averse > 0:
                verse = title[averse:]
                title = title[:averse]
        else:
            title=titlel
            hnum=""
    # check to see if there exists a song file of this or similar name
    title,score,rating = likeFiles(title, SONGS+path
    #, debug=True
    )
    if score.value > Ratings.NOT.value: 
        print("found "+title)
        print(score)
    else: 
        print('\n!!!!!!\n    %s not found in %s %s; you may need to build it.\n!!!!!\n'%(title,path, hnum))
        title=title+'.xml'
    xml.write("\n  <slide_group name=\"%s\" type=\"song\" presentation=\"%s\" path=\"%s\"/>\n\n"%(title,verse,path))
    return 0
  except:
    print(sys.exception())
    print(line)
    print(key)
    print(titlel)
    sys.exit(1)

def prayerAfterComm(xml):
    '''strait out of the ritual in the UMHymnal'''
    xml.write("<slide_group name=\"Prayer of Thanksgiving\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\">\n")
    xml.write(" <title/>\n <subtitle/>\n <notes/>\n <slides>\n <slide>\n")
    xml.write("  <body>Prayer of Thanksgiving\n\n")
    xml.write("Eternal God, we give you thanks\n")
    xml.write("for this holy mystery in which you\n")
    xml.write("have given yourself to us.\n")
    nextSlide(xml)
    xml.write("Grant that we may go into the world\n")
    xml.write("in the strength of your Spirit,\n")
    xml.write("to give ourselves for others,\nin the name of\n")
    xml.write("Jesus Christ our Lord.\nAmen.\n</body></slide></slides></slide_group>\n")

def imageCredits(xml):
    #customH2T("Image Credits",xml)
    customH2T("Credits",xml)
    xml.write("All images used by permission:\n\n")
    xml.write("Vanderbilt Divinity School Library\n")
    xml.write("CreationSwap.com\n")
    xml.write("UMC Discipleship Ministries\n")
    xml.write("Unsplash.com\n")
    xml.write("individual church members</body></slide>\n")
    xml.write("<slide>\n <body>Liturgies:</body></slide>\n")
    xml.write("<slide>\n <body>Music and lyrics:\n")
    #xml.write("CCLI #752546</body></slide>\n")
    xml.write("CCLI #752546\n")
    #xml.write("<slide>\n  <body>")
    endslide(xml)

def lordsPrayer(xml):
    ''' tried and true presentation of the Lord's Prayer '''
    xml.write("<slide_group name=\"The Lord\'s Prayer\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\">\n")
    xml.write(" <title>The Lord\'s Prayer</title>\n\n")
    xml.write(" <subtitle/>\n <notes/>\n <slides>\n <slide>\n")
    xml.write(" <body>The Lord\'s Prayer\n\nOur Father, who art in heaven\n")
    xml.write("hallowed be thy name.\n")
    xml.write("Thy kingdom come, thy will be\n")
    xml.write("done on earth as it is in heaven.</body></slide>\n")
    xml.write("<slide>\n<body>Give us this day our daily bread.\n")
    xml.write("And forgive us our trespasses\n")
    xml.write("as we forgive those who\n")
    xml.write("trespass against us.\n")
    xml.write("And lead us not into temptation,\n")
    xml.write("but deliver us from evil.</body></slide>\n")
    xml.write("<slide>\n <body>For thine is the kingdom,\n")
    xml.write("and the power,\n")
    xml.write("and the glory forever.\n")
    xml.write("Amen.</body></slide></slides></slide_group>\n")

#CommLit = Enum('CommLit','UMHA UMHAabridged UMHAgretchen CUSTOM')
class CommLit (Enum):
    #UMHA = auto()
    #UMHAabridged = auto()
    #UMHAgretchen = auto()
    #CUSTOM = auto()
    UMHA = 'UMH p12 liturgy'
    UMHAabridged = 'UMH p12 prompts and responses'
    UMHAgretchen = 'UMH liturgy ala gNelsen'
    CUSTOM = 'Custom liturgy'
#print(list (CommLit))
CommLits = {
        'UMH p12 liturgy': CommLit.UMHA,
        'UMH p12 prompts and responses': CommLit.UMHAabridged,
        'UMH liturgy ala gNelsen': CommLit.UMHAgretchen,
        'Custom liturgy': CommLit.CUSTOM,
        }
#standardCommunion = CommLit.UMHAgretchen.value
standardCommunion = CommLit.UMHA.value
def greatThanksgivingAabr(xml):
    '''The Great Thanksgiving from the UMHymnal
       Ritual p 12-16
       Abridged, ie leaving out most of the Pastor words'''
    #customH2T("The GreatThanksgiving",xml)
    xml.write("<slide_group name=\"The Great Thanksgiving\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\">\n")
    xml.write(" <title>The Great Thanksgiving</title>\n\n")
    xml.write(" <subtitle/>\n <notes/>\n <slides>\n <slide>\n")
    xml.write(" <body>The Great Thanksgiving\n\n")
    xml.write(" Pastor: The Lord be with you.\n\n")
    xml.write(" People: And also with you.\n\n")
    xml.write(" Pastor: Lift up your hearts.\n\n") 
    xml.write(" People: We lift them up to the Lord.\n\n")
    nextSlide(xml)
    xml.write(" Pastor: Let us give thanks to the Lord our God.\n\n")
    xml.write(" People: It is right to give our thanks and praise.\n")
    nextSlide(xml)
    xml.write(" Pastor: It is right, and a good and joyful thing, always and everywhere to give thanks to you, Almighty God, creator of heaven and earth...\n\n")
    nextSlide(xml)
    xml.write("... And so, with your people on earth and all the company of heaven we praise your name and join their unending hymn:\n\n")
    xml.write(" ALL: Holy, holy, holy Lord,\n")
    xml.write(" God of power and might,\n")
    xml.write(" heaven and earth are full of your glory.\n")
    xml.write(" Hosanna in the highest.\n")
    nextSlide(xml)
    xml.write(" Blessed is he who comes\n")
    xml.write(" in the name of the Lord.\n")
    xml.write(" Hosanna in the highest.\n")
    nextSlide(xml)
    xml.write(" Pastor: Holy are you, and blessed is your Son Jesus Christ...\n\n")
    nextSlide(xml)
    xml.write(" ... in union with Christ\'s offering for us, as we proclaim the mystery of faith.\n\n")
    xml.write(" ALL: Christ has died;\n Christ is risen;\n Christ will come again.\n")
    nextSlide(xml)
    xml.write(" Pastor: Pour out your Holy Spirit on us gathered here, ...\n\n")
    #xml.write(" Through your Son Jesus Christ, with the Holy Spirit in your holy Church,\n")
    nextSlide(xml)
    xml.write("... all honor and glory is yours, Almighty God, now and forever.\n\n")
    xml.write(" ALL: Amen.\n")
    xml.write("</body></slide></slides></slide_group>\n")

def greatThanksgiving(xml):  # {
    '''The Great Thanksgiving from the UMHymnal
       Ritual p 12-16 
       with slight revisions by Pastor G'''
    #customH2T("The GreatThanksgiving",xml)
    xml.write("<slide_group name=\"The Great Thanksgiving\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\">\n")
    xml.write(" <title>The Great Thanksgiving</title>\n\n")
    xml.write(" <subtitle/>\n <notes/>\n <slides>\n <slide>\n")
    xml.write(" <body>The Great Thanksgiving\n\n")
    xml.write("Pastor: The Lord be with you.\n\n")
    xml.write("People: And also with you.\n\n")
    xml.write("Pastor: Lift up your hearts.\n\n") 
    xml.write("People: We lift them up to the Lord.")
    nextSlide(xml)
    xml.write("Pastor: Let us give thanks to the Lord our God.\n\n")
    xml.write("People: It is right to give our thanks and praise.")
    nextSlide(xml)
    xml.write("Pastor: It is right, and a good and joyful thing, always and everywhere to give thanks to you, Almighty God, creator of heaven and earth.")
    nextSlide(xml)
    xml.write("You are here to meet us -\nreside with us in strange\nand alienating times,\nalways faithful,\nalways present in this Body.\nin this Body.")
    nextSlide(xml)
    xml.write("And so, together we proclaim\nthe praise-filled truth of your glory\nalong with all the saints:\n\n")
    xml.write("ALL: Holy, holy, holy Lord,\n")
    xml.write("God of power and might,\n")
    xml.write("heaven and earth are full of your glory.\n")
    xml.write("Hosanna in the highest.")
    nextSlide(xml)
    xml.write("Blessed is he who comes\n")
    xml.write("in the name of the Lord.\n")
    xml.write("Hosanna in the highest.")
    nextSlide(xml)
    xml.write("Pastor: Holy are you, and blessed is your Son Jesus Christ. By the baptism of his suffering, death, and resurrection you gave birth to your Church, delivered us from slavery to sin and death, and made with us a new covenant by water and the Spirit.")
    nextSlide(xml)
    xml.write("On the night in which he gave himself up for us, he took bread, gave thanks to you, broke the bread, gave it to his disciples, and said:\n \"Take, eat; this is my body which is given for you.\n Do this in remembrance of me.")
    nextSlide(xml)
    xml.write("When the supper was over, he took the cup, gave thanks to you, gave it to his disciples, and said: \"Drink from this, all of you; this is my blood of the new covenant, poured out for you and for many for the forgiveness of sins.  Do this, as often as you drink it, in remembrance of me.\" ")
    nextSlide(xml)
    xml.write("And so, in remembrance of these your mighty acts in Jesus Christ, we offer ourselves in praise and thanksgiving as a holy and living sacrifice,")
    nextSlide(xml)
    xml.write("in union with Christ\'s offering for us, as we proclaim the mystery of faith.\n\n")
    xml.write(" ALL: Christ has died;\n Christ is risen;\n Christ will come again.")
    nextSlide(xml)
    xml.write(" Pastor: Pour out your Holy Spirit on us gathered here, and on these gifts of bread and fruit of the vine.  Make them be for us the body and blood of Christ, that we may be for the world the body of Christ, redeemed by his blood.")
    nextSlide(xml)
    xml.write("By your Spirit make us one with Christ, one with each other, and one in ministry to all the world, until Christ comes in final victory, and we feast at his heavenly banquet.")
    nextSlide(xml)
    xml.write("Through your Son Jesus Christ,\nwith the Holy Spirit in your holy Church,\n")
    xml.write("all honor and glory is yours,\nAlmighty God, now and forever.\n\n")
    xml.write("ALL: Amen.\n")
    xml.write("</body></slide></slides></slide_group>\n")
    # }

def greatThanksgiving_orig(xml):  # {
    '''The Great Thanksgiving from the UMHymnal
       Ritual p 12-16'''
    #customH2T("The GreatThanksgiving",xml)
    xml.write("<slide_group name=\"The Great Thanksgiving\" type=\"custom\" print=\"true\" seconds=\"0\" loop=\"false\" transition=\"0\">\n")
    xml.write(" <title>The Great Thanksgiving</title>\n\n")
    xml.write(" <subtitle/>\n <notes/>\n <slides>\n <slide>\n")
    xml.write(" <body>The Great Thanksgiving\n\n")
    xml.write("Pastor: The Lord be with you.\n\n")
    xml.write("People: And also with you.\n\n")
    xml.write("Pastor: Lift up your hearts.\n\n") 
    xml.write("People: We lift them up to the Lord.")
    nextSlide(xml)
    xml.write("Pastor: Let us give thanks to the Lord our God.\n\n")
    xml.write("People: It is right to give our thanks and praise.")
    nextSlide(xml)
    xml.write("Pastor: It is right, and a good and joyful thing, always and everywhere to give thanks to you, Almighty God, creator of heaven and earth.")
    nextSlide(xml)
    xml.write("And so, with your people on earth and all the company of heaven we praise your name and join their unending hymn:\n\n")
    xml.write("ALL: Holy, holy, holy Lord,\n")
    xml.write("God of power and might,\n")
    xml.write("heaven and earth are full of your glory.\n")
    xml.write("Hosanna in the highest.")
    nextSlide(xml)
    xml.write("Blessed is he who comes\n")
    xml.write("in the name of the Lord.\n")
    xml.write("Hosanna in the highest.")
    nextSlide(xml)
    xml.write("Pastor: Holy are you, and blessed is your Son Jesus Christ. By the baptism of his suffering, death, and resurrection you gave birth to your Church, delivered us from slavery to sin and death, and made with us a new covenant by water and the Spirit.")
    nextSlide(xml)
    xml.write("On the night in which he gave himself up for us, he took bread, gave thanks to you, broke the bread, gave it to his disciples, and said:\n \"Take, eat; this is my body which is given for you.\n Do this in remembrance of me.")
    nextSlide(xml)
    xml.write("When the supper was over, he took the cup, gave thanks to you, gave it to his disciples, and said: \"Drink from this, all of you; this is my blood of the new covenant, poured out for you and for many for the forgiveness of sins.  Do this, as often as you drink it, in remembrance of me.\" ")
    nextSlide(xml)
    xml.write("And so, in remembrance of these your mighty acts in Jesus Christ, we offer ourselves in praise and thanksgiving as a holy and living sacrifice,")
    nextSlide(xml)
    xml.write("in union with Christ\'s offering for us, as we proclaim the mystery of faith.\n\n")
    xml.write(" ALL: Christ has died;\n Christ is risen;\n Christ will come again.")
    nextSlide(xml)
    #xml.write(" Pastor: Pour out your Holy Spirit on us gathered here, and on these gifts of bread and wine.  Make them be for us the body and blood of Christ, that we may be for the world the body of Christ, redeemed by his blood.")
    xml.write(" Pastor: Pour out your Holy Spirit on us gathered here, and on these gifts of bread and fruit of the vine.  Make them be for us the body and blood of Christ, that we may be for the world the body of Christ, redeemed by his blood.")
    nextSlide(xml)
    xml.write("By your Spirit make us one with Christ, one with each other, and one in ministry to all the world, until Christ comes in final victory, and we feast at his heavenly banquet.")
    nextSlide(xml)
    xml.write("Through your Son Jesus Christ,\nwith the Holy Spirit in your holy Church,\n")
    xml.write("all honor and glory is yours,\nAlmighty God, now and forever.\n\n")
    xml.write("ALL: Amen.\n")
    xml.write("</body></slide></slides></slide_group>\n")
    # }

def nextSlide(xml):
    xml.write('</body></slide>\n <slide>\n <body>\n')

def blockwrap(xml, block, width= 25,nlines=10):
    ''' format text to fit within a page'''
    curlin = 1
    for each in wrap(block,width):
        xml.write(each+"\n")
        curlin=curlin+1
        if curlin>nlines:
            xml.write('</body></slide>\n <slide>\n <body>\n')
            curlin=1

calls = ['Pastor', 'One', 'Leader', 'Reader', 'Reader 1', 'Reader One', 'Reader 2', 'Reader Two']
responders = ['ALL', 'All', 'Left', 'Right', 'Many', 'People']
def callNresponse(block):
    ''' Separate block of text into separate
        blocks for each call and response.
        Indicate call by preceding it with an empty block.'''
    colonptr=block.find(':')
    if block[:colonptr].strip() not in calls:
        lcalls=[block[:colonptr].strip()]
        if options.verbose: print('found call: ',lcalls[0])
    else: lcalls=[]
    #if options.verbose: print('lcalls:\n',lcalls)
    for each in calls:
        lcalls.append(each)
    #if options.verbose: print('lcalls:\n',lcalls)
    # separate blocks by finding next call or response
    bptr=0
    chunCount=0
    busted=[]
    #TODO
    # starting at a call
    # look for next call or responder
    # save the block and start another
    # if it is a call, add an empty block besides
    chunk=''
    if options.verbose: print(block)
    while bptr < len(block):
        #if options.verbose: print(bptr,' < ',len(block))
        cfind=8000
        rfind=8000
        cfound=''
        rfound=''
        for each in lcalls:
            cptr = block[bptr+1:].find(each+':')
            if cptr >0: 
                #cfind = min(cptr,cfind)
                if cptr< cfind:
                    cfound=each
                    cfind=cptr
        if options.verbose: print('next call: ',cfound, 'at ',cfind)
        for each in responders:
            rptr = block[bptr+1:].find(each+':')
            if rptr >0: 
                if rptr <rfind:
                    rfind = rptr
                    rfound=each
        if options.verbose: print('next resp: ',rfound, 'at ',rfind)
        if rfind==8000 and cfind==8000:  # this is the last part of the block
            chunk =chunk+block[bptr:]
            busted.append(chunk)
            if options.verbose: print(len(busted),' == ',chunCount+1)
            return busted
        if cfind < rfind:   # call starts a new block with an extra empty block
            chunk =chunk+block[bptr:bptr+cfind]
            busted.append(chunk)
            chunCount +=1
            chunk=''
            busted.append(chunk)
            if options.verbose: print('added block of length ',len(chunk))
            chunCount +=1
            bptr+=cfind
            continue
        else:
            # here is where a new line ought to be inserted
            chunk =chunk+block[bptr:bptr+rfind]
            busted.append(chunk)
            chunCount +=1
            chunk=''
            bptr+=rfind

def blockwrapR(xml, block, width= 25,nlines=10):
    ''' format text to fit within a page,
        separate call and response'''
    curlin = 1
    # Identify initial caller by ':'
    for each in wrap(block,width):
        xml.write(each+"\n\n")
        curlin=curlin+1
        if curlin>nlines:
            xml.write('</body></slide>\n <slide>\n <body>\n')
            curlin=1

def eliminate_crap(line):
    # eliminate non-ascii bytes and excess spaces
    # TODO: would rather replace with ' ' than remove completely
    useful=str(line.strip(), encoding="ascii", errors='ignore')
    # eliminate multiple successive spaces
    while "  " in useful:
        useful=useful.replace("  ", " ")
    useful=useful.replace("&", "&amp;")
    return useful

def eliminate_crap_not3(line):
    # eliminate non-ascii bytes
    nonascii=bytearray(range(0x80, 0x100))
    useful = line.strip().translate(None, nonascii)
    #useful=str(useful, encoding="ascii", errors='ignore')
    useful=str(line.strip(), encoding="ascii", errors='ignore')
    # eliminate multiple successive spaces
    while "  " in useful:
        useful=useful.replace("  ", " ")
    return useful

def eliminate_crap_not2(line):
    result=line.strip().encode("ascii", errors="ignore").decode()
    return result

def eliminate_crap_not1(line):
    ''' get rid of non-ascii characters, etc'''
    result=""
    for cc in line.strip():
        if cc.isalpha() or cc.isnumeric() or cc in ";:,.-":
            result=result+cc
    return result

Modes = Enum('Modes', 'INIT SKIP RESPONSIVE RESPONSECONT SONG ONELINER PARAGRAPH PARAGRAPHCONT LASTLINE SANDS SCRIPTURE LORDSPRAYER PRAYERTHANKS GREATTHANKSGIVING PSALTER DOXOLOGY APOSTLESCREED DONE')

sections={
          "Threshold"   :Modes.RESPONSIVE,  # Lent '22
          "Call to Worship"           :Modes.RESPONSIVE,
          "Lords Prayer"              :Modes.LORDSPRAYER,
          "The Lords Prayer"          :Modes.LORDSPRAYER,
          "Prayer of Thanksgiving"    :Modes.PRAYERTHANKS,
          "Prayer after Thanksgiving"    :Modes.PRAYERTHANKS,
          "Opening Prayer"            :Modes.RESPONSIVE,
          # "Faith Response"            :Modes.RESPONSIVE,
          "Responsive Reading"                :Modes.RESPONSIVE,
          "Faith Response"                :Modes.PARAGRAPH,
          "Affirmation of Faith"      :Modes.RESPONSIVE,
          "Acclamations of Faith"     :Modes.RESPONSIVE,
          "Litany"     :Modes.RESPONSIVE,
          "Reconciliation and Assurance of Pardon" :Modes.RESPONSIVE,
          "Call to Reconciliation and Assurance of Pardon" :Modes.RESPONSIVE,
          "Assurance of Pardon"         :Modes.RESPONSIVE,
          "Opening Praise"            :Modes.SONG,
          "Centering Hymn"              :Modes.SONG,
          "Opening Hymn"              :Modes.SONG,
          "Closing Hymn"              :Modes.SONG,
          "Responsive Hymn"           :Modes.SONG,
          "Prayer Hymn"              :Modes.SONG,
          "Communion Hymn"              :Modes.SONG,
          "Canticle"                  :Modes.SONG,
          "Carol"                     :Modes.SONG,
          "Hymn of Commitment"            :Modes.SONG,
          "Hymn of Preparation"            :Modes.SONG,
          "Hymn of Prayer"            :Modes.SONG,
          "Hymn of Praise"            :Modes.SONG,
          "Song of Praise"            :Modes.SONG,
          "Hymn"                      :Modes.SONG,
          "Gathering Praise"            :Modes.SONG,
          "Doxology"                  :Modes.DOXOLOGY,
          "Sung Praise"                  :Modes.SONG,
          "Affirming Our Faith"                  :Modes.SONG,
          "Apostles Creed"            :Modes.APOSTLESCREED,
          "Psalter"                   :Modes.PSALTER,
          "Children Time"      :Modes.ONELINER,
          "Childrens Message"         :Modes.ONELINER,
          "Thanksgiving and Communion":Modes.ONELINER,
          #"The Great Thanksgiving"    :Modes.ONELINER,
          "Holy Communion and Thanksgiving"    :Modes.GREATTHANKSGIVING,
          "Great Thanksgiving"    :Modes.GREATTHANKSGIVING,
          "The Great Thanksgiving"    :Modes.GREATTHANKSGIVING,
          "Invitation to Christs Table"    :Modes.ONELINER,
          "Invitation"    :Modes.PARAGRAPH,
          #"Invitation to Christs Table"    :Modes.GREATTHANKSGIVING,
          "Generosity Moment"         :Modes.ONELINER,
          "Stewardship Sharing"         :Modes.ONELINER,
          "Stewardship Moment"         :Modes.ONELINER,
          "Special Music"             :Modes.ONELINER,
          "Anthem"                    :Modes.PARAGRAPH,
          "Choral Anthem"             :Modes.ONELINER,
          "Choir Anthem"             :Modes.ONELINER,
          "Gospel"             :Modes.SCRIPTURE,
          "Epistle Reading"           :Modes.SCRIPTURE,
          "Epistle"           :Modes.SCRIPTURE,
          "First Testament Reading"   :Modes.SCRIPTURE,
          "Hebrew Scripture"   :Modes.SCRIPTURE,
          "New Testament Reading"     :Modes.SCRIPTURE,
          "New Testament"     :Modes.SCRIPTURE,
          "First Reading"             :Modes.SCRIPTURE,
          "Second Reading"            :Modes.SCRIPTURE,
          "First Scripture Reading"   :Modes.SCRIPTURE,
          "Second Scripture Reading"  :Modes.SCRIPTURE,
          "Hebrew Scripture Reading"  :Modes.SCRIPTURE,
          "Scripture Reading"         :Modes.SCRIPTURE,
          "Prophesy"                  :Modes.SCRIPTURE,
          "Psalm"                  :Modes.SCRIPTURE,
          "Reading"              :Modes.SCRIPTURE,
          "Welcome and Orientation"   :Modes.PARAGRAPH,
          "Greetings"                 :Modes.PARAGRAPH,
          "Greeting"                 :Modes.RESPONSIVE,
          "Centering Music" :Modes.PARAGRAPH,
          "Gathering Centering Music" :Modes.PARAGRAPH,
          "Gathering/Centering Music" :Modes.PARAGRAPH,
          "Glory Sightings"           :Modes.PARAGRAPH,
          "Reflection"                :Modes.PARAGRAPH,
          "Sermon"                    :Modes.PARAGRAPH,
          "Meditation"                :Modes.PARAGRAPH,
          "Sharing Christs Peace"     :Modes.PARAGRAPH,
          "Sharing Peace"     :Modes.PARAGRAPH,
          "Musical Offering"          :Modes.PARAGRAPH,
          "Offertory Prayer"  :Modes.PARAGRAPH,
          "Offertory Music"  :Modes.PARAGRAPH,
          #"Offertory Music/Offering"  :Modes.PARAGRAPH,
          "Music and Offering"        :Modes.PARAGRAPH,
          "Offering"                  :Modes.PARAGRAPH,  # Offering must succeed Musical offering
          "Sharing and Receiving the Bread and Cup" :Modes.PARAGRAPH,
          "Receiving the Bread and Cup" :Modes.PARAGRAPH,
          "Giving the Bread and Cup"     :Modes.PARAGRAPH,
          "Receiving Bread and Cup"     :Modes.PARAGRAPH,
          "Receiving the Bread and the Cup" :Modes.PARAGRAPH,
          "Sharing &amp; Receiving the Bread &amp; Cup" :Modes.PARAGRAPH,
          "Sharing and Receiving the Bread and Cup" :Modes.PARAGRAPH,
          "Sharing and Receiving the Bread &amp; Cup" :Modes.PARAGRAPH,
          "Breaking the Bread" :Modes.PARAGRAPH,
          "Break Open Our Hearts With Prayer" :Modes.PARAGRAPH,
          "Break Open Our Hearts with Prayer" :Modes.PARAGRAPH,
          "Break Open our Hearts with Prayer" :Modes.PARAGRAPH,
          "Intercessory Prayer"       :Modes.PARAGRAPH,
          "Confession Prayer"       :Modes.PARAGRAPH,
          "Pastoral/Intercessory Prayer"    :Modes.PARAGRAPH,
          "Pastoral Prayer"    :Modes.PARAGRAPH,
          "Prayers of Your People"    :Modes.PARAGRAPH,
          "Prayers of the People"     :Modes.PARAGRAPH,
          "Prayers for All Saints"    :Modes.PARAGRAPH,     # added Oct 31, 2021
          "Prayer of the Day"         :Modes.PARAGRAPH, 
          "Prayer for the Day"         :Modes.PARAGRAPH, 
          "Prayer:"                   :Modes.PARAGRAPH,     # generic heading for prayer
          "Prayer of "                :Modes.PARAGRAPH,     # generic heading for prayer
          "Prayer for "               :Modes.PARAGRAPH,     # generic heading for prayer
          "Assurance of Forgiveness"  :Modes.PARAGRAPH,
          "Confession and Assurance"  :Modes.PARAGRAPH,
          "Advent Wreath Lighting"    :Modes.PARAGRAPH,     # added Nov 28, 2021
          "Advent Candle Lighting"    :Modes.PARAGRAPH,     # added Nov 28, 2021
          "Advent Candle Liturgy"     :Modes.PARAGRAPH,     # added dec4, 2025
          "Advent Reading"            :Modes.RESPONSIVE,     # added Nov 30, 2023
          "A Tenebrae"                :Modes.PARAGRAPH,     # added Apr  6, 2023
          "Christmas Cantata"                :Modes.PARAGRAPH,     # added Dec 2025
          "Proclamation and Response" :Modes.SKIP,
          "Proclamation &amp; Response" :Modes.SKIP,
          "Praise God!"               :Modes.SKIP,
          "Closing Prayer"                :Modes.PARAGRAPH,
          "Benediction"                :Modes.PARAGRAPH,
          "Commission &amp; Benediction" :Modes.PARAGRAPH,
          "Blessing &amp; Commission" :Modes.PARAGRAPH,
          "Dismissal"   :Modes.PARAGRAPH,      # added Feb 14, 2024
          "Blessing and Commission"   :Modes.PARAGRAPH,      # added Nov 14, 2021
          "Commission and Blessing"   :Modes.PARAGRAPH,      # added Nov 14, 2021
          "Commission &amp; Blessing" :Modes.PARAGRAPH,
          "Sending Blessing"          :Modes.PARAGRAPH,       # added Dec 10, 2021
          "Announcements"          :Modes.PARAGRAPH,       # added May06, 2024
          "Announcements/Action Steps"          :Modes.PARAGRAPH,       # added Jul06, 2023
          "Singing &amp; Sending Forth"          :Modes.SANDS,       # added Jul 2025
          #"Singing and Sending"          :Modes.LASTLINE,       # added Dec21, 2023
          "Singing and Sending"          :Modes.SANDS,       # added Dec21, 2023
          "Singing &amp; Sending"          :Modes.SANDS,       # added Dec21, 2023
          "Sending Song"          :Modes.SANDS,       # added Dec21, 2023
          "Postlude"          :Modes.LASTLINE,       # added Dec21, 2023
          "Please depart in silence"          :Modes.LASTLINE       # added Apr2, 2026
          }

def bull2pres(xml, line, linenum, mode):
    ''' given a line from the bulletin,
        including its linenumber and the previous mode,
        parse it, interpret it, and write the appropriate input on the xml file
        '''
    global block, modeb4, sANDs
    plinenum = "% 4d: "%linenum
    #useful=str(eliminate_crap(line), encoding="ascii")
    useful=eliminate_crap(line)
    useful=useful.strip('*')  # remove preceding "*"
    #if len(useful) > 2: print(useful,end='')
    # is line a new section type?
    modeB4=mode
    for each in sections.keys():
        if each in useful:
          if useful.replace("The ","",1).find(each) > 3:
            plinenum = " *F*: "
          else:
            mode=sections[each]
            key=each
            if modeB4 == Modes.PARAGRAPHCONT:
                #blockwrap(xml,block[0], width=20000, nlines=1000)
                blockwrap(xml,block, width=20000, nlines=1000)
                endslide(xml)
                if options.verbose: print('End PARAGRAPHCONT with '+key)
            elif modeB4 == Modes.RESPONSECONT:
                block=callNresponse(block)
                for each in block:
                    if len(each) == 0:
                        nextSlide(xml)
                        if options.verbose:print('slide mark')
                    else:
                        blockwrapR(xml,each, width=20000, nlines=1000)
                        if options.verbose: print(each[:5])
                endslide(xml)
                if options.verbose: print('End RESPONSECONT with '+key)
            plinenum = " *S*: "
            break

    #print(plinenum+useful)
    if mode == Modes.INIT:
        initialize(xml,'WesleyUMC')
        mode=Modes.SKIP
    elif mode == Modes.PARAGRAPH:
        custom(key, xml)
        xml.write('\n')
        mode=Modes.PARAGRAPHCONT
        block=""
        if options.verbose: print('Start PARAGRAPHCONT with '+key)
    elif mode == Modes.PARAGRAPHCONT:
        block=block+useful+" "
    elif mode == Modes.SCRIPTURE:
        scripture(useful,key, xml)
        mode=Modes.SKIP
    elif mode == Modes.PSALTER:
        psalter(useful,key, xml)
        mode=Modes.SKIP
    elif mode == Modes.APOSTLESCREED:
        song("Creed Apostles Creed  UMH 881", "Creed", xml)
        mode=Modes.SKIP
    elif mode == Modes.DOXOLOGY:
        # if there is a title following, use it
        # song(useful,key, xml)
        #otherwise use the standard doxology
        song("Doxology Praise God, From Whom All Blessings Flow  UMH 94", "Doxology", xml)
        #song("Doxology Doxology (old)  UMH 95", "Doxology", xml)  # for Lent
        mode=Modes.SKIP
    elif mode == Modes.SONG:
        song(useful,key, xml)
        mode=Modes.SKIP
    elif mode == Modes.LORDSPRAYER:
        lordsPrayer(xml)
        mode=Modes.SKIP
    elif mode == Modes.GREATTHANKSGIVING:
        if options.verbose: 
            print('check Communion option %s'%standardCommunion)
            print(type(mode))
            print(type(standardCommunion))
        if standardCommunion == CommLit.UMHA.value:
        #    print('Communion option %s'%standardCommunion)
            greatThanksgiving_orig(xml)
            mode=Modes.SKIP
        elif standardCommunion == CommLit.UMHAabridged.value:
            greatThanksgivingAabr(xml)
            mode=Modes.SKIP
        elif standardCommunion == CommLit.UMHAgretchen.value:
            greatThanksgiving(xml)
            mode=Modes.SKIP
        #else:
        elif standardCommunion == CommLit.CUSTOM.value:
            print('Use Communion option %s'%standardCommunion)
            custom(key, xml)
            xml.write('\n')
            mode=Modes.RESPONSECONT
            block=""
            if options.verbose: print('Start RESPONSECONT with '+key)
        else:
            print('DANGER WIll Robinson\n!! USED UMH option A COMMUNION')
            greatThanksgiving_orig(xml)
            mode=Modes.SKIP
            for each in CommLit:
               print('|||{0}|||'.format(each))
            print('||{0}||'.format(standardCommunion))
    elif mode == Modes.PRAYERTHANKS:
        #if standardCommunion==CommLit.UMHA or \
        #   standardCommunion==CommLit.UMHAabridged or \
        #   standardCommunion==CommLit.UMHAgretchen:
            prayerAfterComm(xml)
            mode=Modes.SKIP
        #else:
        #    custom(key, xml)
        #    xml.write('\n')
        #    mode=Modes.RESPONSECONT
        #    block=""
        #    if options.verbose: print('Start RESPONSECONT with '+key)
    elif mode == Modes.ONELINER:
        custom(key, xml)
        endslide(xml)
        mode=Modes.SKIP
    elif mode == Modes.RESPONSIVE:
        custom(key, xml)
        xml.write('\n')
        mode=Modes.RESPONSECONT
        block=""
        if options.verbose: print('Start RESPONSECONT with '+key)
    elif mode == Modes.RESPONSECONT:
        # accumulate text in block to format when
        # section is complete
        block=block+useful+" "
    elif mode == Modes.SANDS:
        # if there is a hymn listed use it
        if options.verbose: print("sAndS mode!\n\n")
        if options.verbose: print("b4 song sns= ","")
        if options.verbose: print(sANDs)
        returnType= song(useful,key, xml)
        if returnType <0:
            endslide(xml)
            sANDs = True
        # then make it done
        #endslide(xml)
        if options.verbose: print("sAndS returnType,sNs","")
        if options.verbose: print(returnType,"")
        if options.verbose: print(sANDs)
        mode=Modes.DONE
    elif mode == Modes.LASTLINE:
        custom(key, xml)
        endslide(xml)
        # dont include anything after Blessing
        mode=Modes.DONE
        #break

    return (plinenum,useful,mode)

def bul2presFinish(xml, sANDs=True):
    # finish
    #custom("Announcements/Action Steps", xml)
    #endslide(xml)
    if sANDs:
        #sing it out
        #song("Sing out  O How He Loves You and Me   FWS 2108", "Sing out", xml,"v1")
        #song("Sing out  From the Rising of the Sun   FWS 2124", "Sing out", xml)
        #song("Sing out  All Hail King Jesus   FWS 2069", "Sing out", xml)
        #song("Sing out  More Precious than Silver   FWS 2065", "Sing out", xml)
        #song("Sing out  Freely, Freely   UMH 389", "Sing out", xml)
        #song("Sing out  Give Thanks", "Sing out", xml, "V1 T")
        #song("Sing out  They'll Know We are Christians by Our Love  FWS 2223", "Sing out", xml)
        #song("Sing out  Bind Us Together  FWS 2226", "Sing out", xml)
        #song("Sing out  Jesus Calls Us  UMH v5", "Sing out", xml, "v5")
        #song("Sing out  Emmanuel  UMH 204", "Sing out", xml)
        #song("Sing Out  The Family of God", "Sing out", xml, "c")
        #song("Sing Out  He Lives UMH 310", "Sing out", xml, "c")
        song("Sing Out  There's a Sweet, Sweet Spirit UMH 334", "Sing out", xml)
        #song("Sing out  He Who Began a Good Work in You   FWS 2163", "Sing out", xml, "c")
        #song("Sing out  Awesome God", "Sing out", xml, "c")
        #song("Sing out  Guide My Feet FWS 2208", "sing out", xml, "v1")
        #song("Sing out  Let All Things Now Living FWS 2008", "sing out", xml, "v1")
        #song("Sing out  Thou Didst Leave Thy Throne FWS 2100", "sing out", xml, "v1")
        #song("Sing out  This Is a Day of New Beginnings UMH 383", "Sing out", xml,"v4")
        #song("Sing out  Lord, Be Glorified", "Sing out", xml,"v1")
    # image credits
    imageCredits(xml)
    xml.write("\n</slide_groups></set>\n")

def pComm(dummy):
    print(standardCommunion)
    print(type(standardCommunion))
    #print(standardCommunion.value)
    print(CommLit)
    print([(name,type(name)) for name in CommLit])
    if standardCommunion == CommLit.UMHA.value:
    #    print('Communion option %s'%standardCommunion)
        #greatThanksgiving_orig(xml)
        print(standardCommunion,'UMHA')
    elif standardCommunion == CommLit.UMHAabridged.value:
        print(standardCommunion,'UMHAabridged')

class App:
    def __init__(self, master):
        master.title("Bulletin text to OpenSong XML")
        self.master=master
        #self.master.resizable(1,1)
        self.fileVar=StringVar()
        self.xmlVar =StringVar()
        self.fileVar.set(options.names[0])
        self.xmlVar.set(options.names[1])
        self.fileFrame	=Frame(self.master,relief='raised', border=2)
        self.mFileFrame(self.fileFrame)
        self.fileFrame.grid()
        self.resultFrame=Frame(self.master,relief='sunken', border=2)
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.mResultFrame(self.resultFrame)
        self.master.bind('<Key-C>', pComm)
        self.resultFrame.grid(row=1, sticky=N+S+E+W)

    def mFileFrame(self, frame):
        # configure menu with only open and quit
        #self.fLabel=Label(frame, text='File')
        #self.fLabel.grid(columnspan=3)
        self.filenameE = Entry(frame, relief='sunken',
                textvariable=self.fileVar, width=40)
        self.filenameE.bind('<Button-2>', self.useDialog)
        self.filenameE.bind('<Double-Button-1>', self.useDialog)
        #self.filenameE.bind('<Return>', self.getFile)
        self.openLabel=StringVar()
        self.fMenu=Menubutton(frame, text='bulletin text file')
        self.fMenu.menu=Menu(self.fMenu,tearoff=0)
        #self.fMenu.menu.add_command(label='Open',command=self.getFile)
        #self.fMenu.menu.add_command(label='Save',command=self.roloSave)
        self.fMenu.menu.add_command(label='Close', command=self.master.quit)
        self.fMenu["menu"]=self.fMenu.menu
        self.fMenu.grid(sticky=E)
        self.filenameE.grid(row=0,column=1,sticky=E+W)
        #dummy=Label(frame, text='OpenSong XML file:'+os.getcwd())
        dummy=Label(frame, text='OpenSong XML file:')
        dummy2=Label(frame, text='.xml')
        self.xmlE = Entry(frame, relief='sunken',
                textvariable=self.xmlVar, width=40)
        dummy.grid(row=1,column=0)
        self.xmlE.grid(row=1,column=1)
        dummy2.grid(row=1,column=2)

    def communionA(self):
        global standardCommunion
        if options.verbose: print ('communion option',self.commType.get())
        standardCommunion=self.commType.get()
        if options.verbose: print ('communion option %s'%standardCommunion)
        # set menubutton text
        self.commOpts.config(text=standardCommunion)


    def mResultFrame(self, frame):
        # doit and details buttons on top row
        self.commOpts = Menubutton(frame, text='Communion', relief=GROOVE)
        self.commOpts.menu=Menu(self.commOpts,tearoff=0)
        self.commType=StringVar()
        #self.commType=IntVar()
        for each in CommLits:
            self.commOpts.menu.add_radiobutton(
                label=each, 
                variable=self.commType, value=CommLits[each].value, 
                command=self.communionA
                )
            if CommLits[each].value == standardCommunion: 
                me=self.commOpts.menu.index(each)
                self.commOpts.menu.invoke(me)
            if options.verbose: print ('menu %s for %s'%(each,CommLits[each]))
        #each='yoMama'
        self.commOpts["menu"]=self.commOpts.menu
        self.commOpts.grid(sticky=E)

        self.doitButton = Button(frame, text="Doit:",command=self.bull2pres)
        self.doitButton.grid(row=0,column=1)
        self.detailButton = Button(frame, text="Details:",command=self.toggleDetails)
        frame.columnconfigure(1, weight=1)
        self.detailButton.grid(row=0,column=2,sticky='E')
        self.detailFrame = Frame(frame, relief='sunken')
        # removeable frame for text blocks and scroll
        self.stScroll = Scrollbar(self.detailFrame,orient=VERTICAL)
        self.stScroll['command']=self.ayview
        self.lnumV=StringVar()
        self.lnum = Text(self.detailFrame, width=6, height=20,
                yscrollcommand=self.selfScroll)
        self.lLinV=StringVar()
        self.lLin = Text(self.detailFrame, wrap='none',
                yscrollcommand=self.selfScroll)
        #self.detailFrame.rowconfigure(0, weight=1)
        self.lnum.grid(row=0,column=0,sticky=N+S+E+W)
        self.stScroll.grid(row=0,column=1, sticky=N+S+E+W)
        self.detailFrame.columnconfigure(2, weight=1)
        self.lLin.grid(row=0,column=2,sticky=N+S+E+W)
        self.stShowed=False
        # don't show the detailFrame initially
        #self.detailFrame.grid(row=1, columnspan=2, sticky=N+S+E+W)


    def ayview(self, *args):
        self.lLin.yview(*args)
        self.lnum.yview(*args)

    def selfScroll(self, *args):
        self.stScroll.set(*args)
        self.ayview('moveto',args[0])

    def toggleDetails(self):
        if self.stShowed:
            self.detailFrame.grid_remove()
            self.stShowed=False
            self.detailFrame.winfo_toplevel().geometry("")
        else:
            self.detailFrame.rowconfigure(1, weight=1)
            self.detailFrame.grid(row=1, column=0, columnspan=2, sticky=N+S+E+W)
            self.stShowed=True

    def useDialog(self,widget):
        """ use file dialog box to get a filename """
        #tkinter extension
        #self.fileVar.set(tkFileDialog.askopenfilename()
        d=tkinter.filedialog.FileDialog(self.master)
        self.fileVar.set(d.go())
        self.fileVar.set(self.fileVar.get().replace(os.getcwd()+'/',''))
        #tix
        #self.fileVar.set(FileSelectBox.invoke(self))
        #self.fileVar.set(ExFileSelectBox.invoke(self.master))
        pass

    def getFile(self,widget=None):
        name=self.fileVar.get()
        if name[0] == '~':
            name=os.path.expanduser(name)
            if options.verbose: print ('open file: %s'%name)
        if os.path.exists(name):
            self.filenameE.bind('<Return>',self.roloNull)
            self.rebuild(name)
        else:
            self.OhNo=ScreamNdie('%s not found'%name,self.master)

    def bull2pres(self):
        # open the text file to read
        # open the set file to write
        global sANDs
        try:
            bull = open(self.fileVar.get(),'rb')
            xmlname  = self.xmlVar.get()
            xml  = open(xmlname+'.xml','w')
        except IndexError:
            print(Usage)
            sys.exit(1)
        except FileNotFoundError as e:
            print(e)
            #print('%s does not exist\n'%options.names[0])
            print(Usage)
            #sys.exit(1)
            return

        self.lLin.delete('1.0',END)
        self.lnum.delete('1.0',END)
        mode=Modes.INIT
        sANDs=False
        linenum=0
        # read each line of text
        # mode determines how it is used
        # section type determines mode
        for line in bull.readlines():
            linenum=linenum+1
            (pline, uline, mode)=bull2pres(xml, line, linenum, mode)
            self.lnum.insert('end',pline+'\n')
            self.lLin.insert('end',uline+'\n')
            if mode == Modes.DONE: break

        if options.verbose: print("sns setting","")
        if options.verbose: print(sANDs)
        bul2presFinish(xml,sANDs=sANDs)
        
    def runit(self):
        #returncode=call(['echo', './bull2pres.py', self.fileVar.get(), self.xmlVar.get()])
        #returncode=call(['./bull2pres.py', self.fileVar.get(), self.xmlVar.get()])
        process=run(['./bull2pres.py', self.fileVar.get(), self.xmlVar.get()], capture_output='true')
        #print(process.stdout)
        self.lLin.delete('1.0',END)
        self.lnum.delete('1.0',END)
        self.lLin.insert(END,process.stdout)
        #for line in iter(process.stdout.readline,''):
        #for line in io.TextIOWrapper(process.stdout, encoding="utf-8"):
        for line in iter(process.stdout.readline, b''):
            #self.lnum.insert('end',line[0:5])
            #self.lLin.insert('end',line[5:])
            fred=3
            print(line)

 
class CLfile(Action):
    """
    Command Line specification of a filename
      also indicates to set the startup option to True
    """
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, 'startUp',True)
        setattr(namespace, self.dest, values)
        if namespace.verbose:
            print ("in CLFILE: ",option_string,values)
            print ("in CLFILE: ",namespace)

sys.path.append('/home/clyde/lib')
from likeFile import likeFiles,Ratings

def testLikeFile(testee='likeFile'):
    found,score,rating=likeFiles(testee,suffix='.xml'
    ,debug=True
    )
    print(found)
    print(score)
    print(score.value)
    print(rating)

if __name__ == '__main__':
    #gui=True
    parser = ArgumentParser(description='Generate OpenSong set from bulletin text')
    parser.add_argument("-v", action="store_true", dest='verbose', default=False, help='toggle debug print')
    parser.add_argument("-t", action="store_false", dest='gui', default=True, help='dont use GUI')
    parser.add_argument('names', type=pathlib.Path, nargs='*', help='bulletin name and resultant XML file name'
            , default=['bulletin.txt','latest'])
    options = parser.parse_args()
    if not hasattr(options, 'startUp'):
        setattr(options, 'startUp',False)

    if options.verbose: print ("in main: ", options)
    if len(options.names) < 2: 
        setattr(options, 'names', [options.names[0],'latest'])

    if options.gui:
        root = Tk()
        app = App(root)
        root.mainloop()
    else:
        # open the text file to read
        # open the set file to write
        try:
            bull = open(options.names[0],'rb')
            xmlname  = options.names[1]
            xml  = open('%s.xml'%xmlname,'w')
        except IndexError:
            print(Usage)
            sys.exit(1)
        except FileNotFoundError as e:
            print(e)
            #print('%s does not exist\n'%options.names[0])
            print(Usage)
            sys.exit(1)

        mode=Modes.INIT
        sANDs=False
        linenum=0
        # read each line of text
        # mode determines how it is used
        # section type determines mode
        for line in bull.readlines():
            linenum=linenum+1
            (pline, uline, mode)=bull2pres(xml, line, linenum, mode)
            print(pline, end='')
            print(uline)
            if mode == Modes.DONE: break

        bul2presFinish(xml,sANDs=sANDs)
