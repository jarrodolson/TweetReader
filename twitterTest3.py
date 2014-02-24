##  Program should search twitter, return results,
## convert results into XML (search as root, tweetID as parent and each
## field as a child and then be in a processable form from XML...
## Could also return data in SQL db format

import urllib2, urlparse, gzip
from StringIO import StringIO
from sgmllib import SGMLParser
import os
from xml.etree import ElementTree
from xml.dom import minidom
import json
import re
import time
import glob

##term = 'http://search.twitter.com/search.json?q=food%20AND%20drought'
##saveas = 'q=foodANDdrought'
saveas = str

## Data gathering and creation
def clearStopWords(dic):
    f1 = open("common-english-words.txt")
    stopWordsData = f1.read()
    stopWordsList = stopWordsData.split(',')
    for words in stopWordsList:
        try:
            del dic[words]
        except KeyError:
            pass
    f1.close()
    return dic

def checkDirectory (allTweets, results):
    fout2 = open(directory+saveas+"directory.txt", 'w')
    for item in results:
        index = item['id']
        try:
            checkDirectory = allTweets[index]
        except KeyError:
            allTweets[index] = True
    for item in allTweets:
        fout2.write(str(item)+" : "+str(allTweets[item])+" \n")
    return allTweets

def createDirectory(directory):
    print "Creating Path"
    newPathCreated = False
    while newPathCreated == False:
        initialPath = ".\\"+directory
        try:
            os.mkdir(initialPath)
            newPathCreated = True
        except OSError:
            print "Folder Exists"
            userInput = raw_input('Do you want to overwrite the directory? (1=yes, 2=no) ')
            if str(userInput) == '2':
                directory = raw_input('What would you like to save it as? ')
                directory = directory+'\\'
            if str(userInput) == '1':
                break
    try:
        os.mkdir(initialPath+"\\JSONOutputs")
    except OSError:
        pass
    try:
        os.mkdir(initialPath+'\\KML')
    except OSError:
        pass
    return directory

def createQuery():
    term = raw_input("What are the words you would like to search? (separated by 'AND')")
    term = str(term)
    term = "q="+term
    saveas = term.replace(' ','')
    term =term.replace(' ', '%20')
    rpp = "&rpp=100"
    address = "http://search.twitter.com/search.json?&"
    query = address+term+rpp
    return address, query, saveas

def createQuery():
    term = raw_input("What are the words you would like to search? (separated by 'AND')")
    term = str(term)
    term = "q="+term
    saveas = term.replace(' ','')
    term =term.replace(' ', '%20')
    rpp = "&rpp=100"
    address = "http://search.twitter.com/search.json?&"
    query = address+term+rpp
    return address, query, saveas

def directoryTest(directoryConfirmation):
    directory = raw_input("What directory would you like to use? (No slashes): ")
    print "You entered "+directory
    confirmation = raw_input("Is this correct? (1=yes, 2=no): ")
    if confirmation == "1":
        directoryConfirmation = True
        directory = directory+"\\"
    return directoryConfirmation, directory

def displayDirectory():
    directoryList = os.listdir(".")
    for items in directoryList:
        print items

def findRefreshQuery(files2, maxIDCompareList):
    for fileName in files2:
        f = open(fileName)
        data = readObjectAsString(f)
        f.close()
        maxIDCompareList.append(fileName+":"+str(data['max_id_str']))
    sortedIDCompareList = sorted(maxIDCompareList, key=lambda x:x[1], reverse = True)
    fileForRefresh = sortedIDCompareList[0]
    fileForRefresh = fileForRefresh.split(':')
    fileForRefresh = fileForRefresh[0]
    print fileForRefresh
    f = open(fileForRefresh)
    data = readObjectAsString(f)
    f.close()
    refreshQuery = data['refresh_url']
    term = 'http://search.twitter.com/search.json?&'+str(refreshQuery)+'&rpp=100'
    return term

def findRTFromMaster(master):
    listOfRT = []
    masterNoRT = {}
    masterRT = {}
    count = 0
    rtIndex = False
    for tweets in master:
        tweet = master[str(tweets)]
        tweetText = tweet['text']
        tweetTextLower = tweetText.lower()
        tweetTextList = tweetTextLower.split(' ')
        for item in tweetTextList:
            rtIndex = item.startswith('rt')
            if rtIndex == True:
                break
        if rtIndex == True:
            masterRT[str(tweets)]=master[str(tweets)]
        if rtIndex == False:
            masterNoRT[str(tweets)]=master[str(tweets)]
    return masterNoRT, masterRT


def getResults(data):
    results = data['results'] ## searches as dictionary, returns list
    numberResults = len(results)
    return results, numberResults

def getTweet(results, tweetNumber):
    tweet = results[tweetNumber] ## searches as a list, returns a dictionary
    tweetKeys = tweet.keys()
##    for item in tweetKeys:
##        print item
##        print tweet[item]
    return tweetKeys, tweet

def IDTopLevelFields (data):
    keyList = data.keys()
    keyList.remove('results')
    keyValueDic = {}
    for item in keyList:
        value = data[item]
        keyValueDic[item]=value
    return keyList, keyValueDic

def newJSONFile(master, files2):
    ##fout = open('TESTREAD.txt', 'w')
    refreshQuery = 'Jim'
    for fileName in files2:
        f = open(fileName)
        data = readObjectAsString(f)
        refreshQuery = data['refresh_url']
        f.close()
        for tweets in data['results']:
            tweetID = tweets['id']
            tweetID = str(tweetID)
            try:
                value = master[tweetID]
            except KeyError:
                master[tweetID] = tweets
    ##for items in master:
    ##    fout.write(str(items)+" : "+str(master[items]))
    ##fout.close()
    return master, refreshQuery

def openWebsite(term):
    opened = False
    while opened==False:
        try:
            obj = urllib2.urlopen(term)
            url = obj.geturl()
    ##          print url
            info = obj.info()
            print info
            opened = True
            return info, obj
        except urllib2.URLError,(ErrorMessage):
            print 'error, trying again'
            print ErrorMessage

def readObjectAsString (obj):
    dataString = obj.read()
    data1 = json.loads(dataString)
##    print data
    return data1

def waitAndSeeTest(waitAndSee, numberOfReps, address, saveas, whichVersion):
    if waitAndSee == True:
        print "Automatic 5 minute delay engaged per twitter cache policy"
        time.sleep(300) ##for proper etiquette querying twitter... cache does not update for 5 minutes
    if numberOfReps==0:
        if whichVersion == 'newData':
            address, term, saveas = createQuery()
            print term
        if whichVersion == 'oldData':
            address = str
            term = str
            saveas = str
    if numberOfReps>0 and waitAndSee == False:
        term = address+data['refresh_url']+"&rpp=100&page="+str(numberOfReps+1)
        print term
    if waitAndSee == True:
        term = address+data['refresh_url']+"&rpp=100&page=1"
        print term
        waitAndSee = False
    return waitAndSee, numberOfReps, address, term, saveas


def writeJSONFile(directory, saveas, numberOfReps, data):
    print "New Results"
    fout = open(directory+"JSONOutputs\\"+saveas+str(numberOfReps)+".txt", "w")
    fout.write(json.dumps(data, indent=2))
    fout.close()
    f = open(directory+"JSONOutputs\\"+saveas+str(numberOfReps)+".txt")
    data = readObjectAsString(f)
    f.close()
    return data

def writeJSONFileOld(directory, saveas, numberOfReps):
    f = open(directory+"JSONOutputs\\"+saveas+str(numberOfReps)+".txt")
    data = readObjectAsString(f)
    f.close()
    return data


## *******Analysis*******

def clearStopWords(dic):
    f1 = open("common-english-words.txt")
    stopWordsData = f1.read()
    stopWordsList = stopWordsData.split(',')
    for words in stopWordsList:
        try:
            del dic[words]
        except KeyError:
            pass
    f1.close()
    return dic

def checkDirectory (allTweets, results):
    fout2 = open(directory+saveas+"directory.txt", 'w')
    for item in results:
        index = item['id']
        try:
            checkDirectory = allTweets[index]
        except KeyError:
            allTweets[index] = True
    for item in allTweets:
        fout2.write(str(item)+" : "+str(allTweets[item])+" \n")
    return allTweets

def createQuery():
    term = raw_input("What are the words you would like to search? (separated by 'AND')")
    term = str(term)
    term = "q="+term
    saveas = term.replace(' ','')
    term =term.replace(' ', '%20')
    rpp = "&rpp=100"
    address = "http://search.twitter.com/search.json?&"
    query = address+term+rpp
    return address, query, saveas

def createMasterWordBubble(tweets, masterWordBubble):
    keyList = tweets.split(" ")
    for key in keyList:
        key = key.lower()
        try:
            wordCount = masterWordBubble[key]
            wordCount = wordCount+1
            masterWordBubble[key]=wordCount
        except KeyError:
            masterWordBubble[key]=1
    return masterWordBubble

def createTimeAverage(sortedNewTimeList, newTimeDict):
    totalMinutes = len(sortedNewTimeList)
    totalTweets = 0
    repetitionCount = 0
    valueList_minute = []
    tweetsPer5Min = {}
    minuteRollingAverage = raw_input('What is the unit of time (in minutes) that you would like the rolling average for? ')## unit of time, to be selected by user that they want the rolling average for
    minuteRollingAverage = int(minuteRollingAverage)
    for items in newTimeDict:
        value_minute = newTimeDict[items]
        totalTweets = totalTweets+value_minute
        valueList_minute.append(value_minute)
        if repetitionCount>minuteRollingAverage-1:## Starts calculating rolling average based on 'minuteRollingAverage'
            ##print 'Calculating Rolling Average in '+str(minuteRollingAverage)+' minute intervals.'
            currentCount = 0
            tempSum = 0
            rollingAverage = 0
            while currentCount<minuteRollingAverage:
                tempValue = long(valueList_minute[currentCount])
                tempSum = tempSum+tempValue
                try:
                    rollingAverage = tempSum/minuteRollingAverage
                except ZeroDivisionError:
                    pass
                currentCount = currentCount+1
            tweetsPer5Min[items]=tempSum
        repetitionCount = repetitionCount+1
    avgTweetsPerMinute = totalTweets/totalMinutes
    print 'Total Tweets = '+str(totalTweets)
    print 'Tweets Per Minute = '+str(avgTweetsPerMinute)
    return tweetsPer5Min

def checkDivision(divisor, count):
    trueFalseTest = False ##When value IS evenly divisable, value = True
    intTest = float
    intTest = float(count)/divisor
    intTest = float(intTest)
    intTest = str(intTest)
    intTestList = intTest.split('.')
    intTestValue = str(intTestList[1])
    if intTestValue=='0':
        trueFalseTest = True
    return trueFalseTest

def createSearchDic(searchTerm, master, searchDic):
    for items in master:
        tweet = master[items]
        tweetText = tweet['text']
        tweetTextList = tweetText.split(' ')
        for each in tweetTextList:
            each = each.lower()
            try:
                wordIndex = each.index(searchTerm)
                try:
                    resultsList = searchDic[searchTerm]
                    resultsList = resultsList+','+str(tweet['id'])
                    searchDic[searchTerm]=resultsList
                except KeyError:
                    searchDic[searchTerm]=str(tweet['id'])
            except:
                pass
    return searchDic

def createTimeCount2(sortedNewTimeList, newTimeDict):
    foutString3 = directory+'\\'+saveas+'timeGraph_byTime.csv'
    tempFout = open('testingAvg.txt', 'w')
    totalMinutes = len(sortedNewTimeList)
    totalTweets = 0
    repetitionCount = 0
    tempTweets = 0
    valueList_user = {}
    minuteRollingAverage = raw_input('What is the unit of time (in minutes) you would like your results in? ')
    minuteRollingAverage = int(minuteRollingAverage)
    count = 0
    for items in sortedNewTimeList:
        ##itemsList = items.split()
        value_minute = int(items[1])
        tempTweets = tempTweets+value_minute
        evenDivisor = checkDivision(minuteRollingAverage, count)
        count = count+1
        key = items[0]
        if evenDivisor==True:
            valueList_user[key]=str(tempTweets)
            print items[0], valueList_user[key]
            tempTweets = 0
    valueList = dictToList(valueList_user)
    sortedValueList = sorted(valueList)
    listTuplesToCSVNumber(sortedValueList, foutString3)
    tempFout.close()
    return sortedValueList

def createTweetWordBubble (tweet):
    tweetWordBubble = {}
    value = tweet['text']
    valueList = value.split(' ')
    for item in valueList:
        item = item.lower()
        try:
            wordCount = tweetWordBubble[item]
            wordCount = wordCount+1
            tweetWordBubble[item]=wordCount
        except KeyError:
            tweetWordBubble[item] = 1
    return tweetWordBubble

def createWordBubble(masterWordBubble, results):
    tweetNumber = 0
##    while tweetNumber<len(results):
##        tweetKeys, tweet = getTweet(results, tweetNumber)
##        tweetWordBubble = createTweetWordBubble(results)
    masterWordBubble = createMasterWordBubble(results, masterWordBubble)
##        tweetNumber = tweetNumber+1
    return masterWordBubble

def findAndCountHash(masterWordBubble):
    fout2 = open(directory+saveas+"hashtags.txt", "w")
    count = 0
    ##tempList = []
    p = re.compile('#')
    hashDic={}
    for item in masterWordBubble:
        match = p.match(item)
        try:
            test = match.group()
            hashDic[item]=masterWordBubble[item]
        except AttributeError:
            pass
    sortedList = sortList (hashDic)
    for item in sortedList:
        fout2.write(str(sortedList[count])+" \n")
        count = count+1
    fout2.close()
    return hashDic

def findAndCountUser(results, tweeterDic):
    count = 0
##    for item in results:
##        userID = item['from_user']
    try:
        tweetCount = tweeterDic[results]
        tweetCount = tweetCount+1
        tweeterDic[results]=tweetCount
    except KeyError:
        tweeterDic[results]=1
    return tweeterDic

def findDates(results, monthDict, dateDict, timeDict):
    yearDict = {}
    hourDict = {}
    monthEquivalents = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    hourANDminuteDict = {}
##    for item in results:
##    date = item['created_at']
    date = results
    dateList = date.split(',')
    day = dateList[0]
    dateANDTime = dateList[1]
    dateANDTimeList = dateANDTime.split(' ')
    day_date = dateANDTimeList[1]
    month_date = dateANDTimeList[2]
    month_date_equiv = monthEquivalents[month_date]
##    print month_date_equiv
    year_date = dateANDTimeList[3]
    date2 = dateANDTimeList[1:4]
    dateString2 = year_date+month_date+dateANDTimeList[1]
    dateString2_equiv = year_date+'-'+str(month_date_equiv)+'-'+dateANDTimeList[1]
    dateString = date2[0]
    dateString = dateString+date2[1]
    dateString = dateString+date2[2]
    time = dateANDTimeList[4]
    ##print newDateString
    timeZone = dateANDTimeList[5]
    timeList = time.split(":")
    hour = timeList[0]
    hourANDMinute = timeList[0:1]
    hourString = timeList[0]
    hourString = hourString+timeList[1]
    dateANDTimeString = dateString2+" "+hourString
    newDateString = year_date+'-'+str(month_date_equiv)+'-'+day_date+' '+hourString
    try:
        monthCount = monthDict[month_date]
        monthCount = monthCount+1
        monthDict[month_date]=monthCount
    except KeyError:
        monthDict[month_date]=1
        ##print month_date
    try:
        dateCount = dateDict[dateString2_equiv]
        dateCount = dateCount+1
        dateDict[dateString2_equiv]=dateCount
    except KeyError:
        dateDict[dateString2_equiv]=1
    try:
        timeCount = timeDict[newDateString]
        timeCount=timeCount+1
        timeDict[newDateString] = timeCount
    except:
        timeDict[newDateString]=1
       ## print dateANDTimeString

##    for items in timeDict:
##        fout4.write(items+" : "+str(timeDict[items])+ "\n")
    return monthDict, dateDict, timeDict

def getGeoCode(results):
    fout2 = open(directory+saveas+"geoCode.txt", "a")
    geoDict = {}
    for tweets in results:
        tweetDict = results[tweets]
        geoCode = tweetDict['geo']
        fout2.write(str(tweets)+":"+str(geoCode)+" \n")
        geoDict[str(tweets)]=str(geoCode)
    fout2.close()
    return geoDict

def getTweetsByList(foutSearchStr, searchTermList, master):
    foutSearch = open(foutSearchStr, 'w')
    for items in searchTermList:
        tweet = master[items]
        tweetText = tweet['text']
        writeString = items+" : "+tweetText+'\n'
        writeString = writeString.encode('utf-8')
        print (writeString)
        try:
            foutSearch.write(writeString)
        except UnicodeEncodeError:
            foutSearch.write(items+" : EncodingError")
            
    foutSearch.close()

def getGeoCodeLimited(geoDict, directory):
    fOutString = directory+'limitedGeoForKML.txt'
    fOut = open(fOutString, 'w')
    limitedGeoDict = {}
    numberTweets = len(geoDict)
    countGeoLocated = 0
    for items in geoDict:
        value = geoDict[items]
        if value != 'None':
            limitedGeoDict[items]=value
            countGeoLocated = countGeoLocated+1
    percentGeo = (float(countGeoLocated)/float(numberTweets))*100
    print 'Out of '+str(numberTweets)+' tweets, '+str(countGeoLocated)+' are geolocated. ('+str(percentGeo)+'%)'
    print countGeoLocated
    for items in limitedGeoDict:
        fOut.write(str(items)+":: "+str(limitedGeoDict[items])+' \n')
    fOut.close()
    return limitedGeoDict, fOutString

def timeGraph (sortedTimeList, timeDic, directory, saveas):
    ##Creates CSV file for visualizing time data
    sortedTimeListLength = len(sortedTimeList)
    
    startingDate = sortedTimeList[0]
##    print startingDate
##    startingDateList = startingDate.split(', ')
    startingDate_date = startingDate[0]
    startingDate_dateList = startingDate_date.split(' ')
    startingDate_YrMoDay = startingDate_dateList[0]
    startingDate_time = startingDate_dateList[1]
    startingDate_count = startingDate[1]
    
    endingDate = sortedTimeList[sortedTimeListLength-1]
    endingDate_date = endingDate[0]
    endingDate_dateList = endingDate_date.split(' ')
    endingDate_YrMoDay = endingDate_dateList[0]
    endingDate_time = endingDate_dateList[1]
    endingDate_count = endingDate[1]
    startingDay = startingDate_YrMoDay[len(startingDate_YrMoDay)-2:len(startingDate_YrMoDay)]
    startingYrMo = startingDate_YrMoDay[0:7]
    endingDay = endingDate_YrMoDay[len(endingDate_YrMoDay)-2:len(endingDate_YrMoDay)]

    numberOfDays = int(endingDay)-int(startingDay)
    countDays = 0
    timeList2 = []
    day = int(startingDay)
    YrMo = startingYrMo
    print startingDate_time
    time = str(startingDate_time[0:2])
    minute = str(startingDate_time[2:4])
    while countDays<numberOfDays:
        countHour1 = 0
        while countHour1<3:
            countHour2 = 0
            time2 = str(countHour1)+str(countHour2)
            time2 = int(time2)
            while countHour2<10 and time2<23:
                time2 = str(countHour1)+str(countHour2)
                time2 = int(time2)
                countMin1 = 0
                while countMin1<6:
                    countMin2 = 0
                    while countMin2<10:
                        newDateString = str(YrMo)+str(day)+" "+str(countHour1)+str(countHour2)+str(countMin1)+str(countMin2)
                        timeList2.append(newDateString)
                        countMin2 = countMin2+1
                    countMin1 = countMin1+1
                countHour2 = countHour2+1
            countHour1 = countHour1+1
        countDays = countDays+1
        day = day+1
##    print timeList2
    newTimeDict = timeDict
    for items in timeList2:
        try:
            value = newTimeDict[items]
        except KeyError:
            newTimeDict[items] = 0
    sortedNewTimeList = sortList(newTimeDict)
    sortedNewTimeList = sorted(sortedNewTimeList)
    averageByTime = createTimeCount2(sortedNewTimeList, newTimeDict)
##    totalMinutes = len(sortedNewTimeList)
##    totalTweets = 0
##    for items in newTimeDict:
##        value12 = newTimeDict[items]
##        totalTweets = totalTweets+value12
##    avgTweetsPerMinute = totalTweets/totalMinutes
##    print 'Total Tweets = '+str(totalTweets)
##    print 'Tweets Per Minute = '+str(avgTweetsPerMinute)
    foutString = directory+'\\'+saveas+'timeGraph.csv'
    foutString2 = directory+'\\'+saveas+'timeGraph_rolling.csv'
    listToCSV(sortedNewTimeList, foutString)
    ##rollingAverageList = sortList(rollingAverage)
    ##sortedRollingAverageList = sorted(sortedNewTimeList)
    ##listToCSV(rollingAverageList, foutString2)
##    listToCSV(averageByTime, foutString2)
    return foutString

def findGISData(foutString, key, coordinates):
    termStart = 'http://maps.googleapis.com/maps/api/geocode/json?latlng='
    term = str(termStart)+str(coordinates)+'&sensor=false'
    opened = False
    obj = object
    info = str
    url = str
    printStr = str
    while opened == False:
        try:
            obj = urllib2.urlopen(term)
            url = obj.geturl()
            ##print url
            info = obj.info()
            ##print info
            opened = True
        except urllib2.URLError, (ErrorMessage):
            print ErrorMessage
    dataString = obj.read()
    data1 = json.loads(dataString)
##    foutTEST = open('Test.txt', 'w')
##    foutTEST.write(json.dumps(data1, indent=2))
##    foutTEST.close()

##    f = open('TEST.txt')
    fout = open(foutString, 'a')
    writeString = str(key)+','
    writeString = writeString.encode('utf-8')
    try:
        fout.write(writeString)
    except UnicodeEncodeError:
        fout.write('EntryNA,')
##    dataString = obj.read()
##    data1 = json.loads(dataString)
    status = data1['status']
    status = status.encode('utf-8')
    try:
        print status
    except UnicodeEncodeError:
        pass
    skip = False
    if status == 'ZERO_RESULTS':
        print "Query successful, but no results available. Address may be remote or unmapped."
        skip = True
    if skip == False:
        results = data1['results']
        lengthResults = len(results)
        count = 0
        listHeaders = []
        while 1>count:
            data1 = results[count]
            for elements in data1:
                ##print elements
                listHeaders.append(elements)
            geometry = data1['geometry']
            geomCount = 0
            location_type = geometry['location_type']
            writeString = location_type+','
            writeString = writeString.encode('utf-8')
        ##    print 'Location Type'
            try:
                ##print location_type
                fout.write(writeString)
            except UnicodeEncodeError:
                fout.write('NA,')
        ##        for items in geometry:
        ##            print items
        ##            print geometry[items]
        ##            geomCount = geomCount+1
            address_components = data1['address_components']
            addyCount = 0
            for items in address_components:
        ##        print 'ADDRESS COMPONENTS'
                dict_addyComponents = address_components[addyCount]
         ##       print 'TYPES' + str(dict_addyComponents['types'])
         ##       print 'LONG NAME: '+str(dict_addyComponents['long_name'])
                tempItem = dict_addyComponents['long_name']
                tempItem = tempItem.encode('utf-8')
                writeString = str(tempItem)+','
                ##writeString = writeString.encode('utf-8')
                try:
                    fout.write(writeString)
                except UnicodeEncodeError:
                    fout.write('NA,')
        ##        for elements in dict_addyComponents:
        ##            print str(elements) + str(dict_addyComponents[elements])
                addyCount = addyCount+1
            formatted_address = data1['formatted_address']
            ##print 'Formatted address'
            ##print formatted_address
            writeString = formatted_address.encode('utf-8')
            ##writeString = writeString.encode('utf-8')
            try:
                fout.write(writeString)
            except UnicodeEncodeError:
                fout.write('NA,')
            fout.write('\n')
        ##    types = data1['types']
        ##    typesCount = 0
        ##    print 'TYPES'
        ##    for items in types:
        ##        print types[typesCount]
        ##        typesCount = typesCount+1
            count = count+1
        fout.close()

        
##*********DataType Conversions*************
def createKML(fOutString, directory, master):
    f = open(fOutString)
    count = 0
    newDict = {}
    tweet = str('NA')
    tweetDic = {}
    for lines in f:
        KMLOut = open(directory+'KML\\kml'+str(count)+'.kml', 'w')
        KMLOut.write('<?xml version="1.0" encoding="UTF-8"?> \n<kml xmlns="http://www.opengis.net/kml/2.2"> \n <Placemark> \n')
        data = lines.split(':: {')
        key = data[0]
        key = str(key)
        tweetDic = master[key]
        userName = tweetDic['from_user']
        tweetText = tweetDic['text']
        date = tweetDic['created_at']
        writeString = '  <name>'+str(key)+'</name> \n'
        writeString = writeString.encode('utf-8')
        try:
            KMLOut.write(writeString)
        except UnicodeEncodeError:
            KMLOut.write('  <name>NA</name> \n')
        KMLOut.write('  <description>')
        writeString = '<p><b>User:</b> '+str(userName)+'</p>'
        writeString = writeString.encode('utf-8')
        try:
            KMLOut.write(writeString)
        except UnicodeEncodeError:
            KMLOut.write('<p><b>User:</b> NA</p>')
        writeString = '<p><b>Text:</b> '+tweetText+'</p>'
        writeString = writeString.encode('utf-8')
        try:
            KMLOut.write(writeString)
        except UnicodeEncodeError:
            KMLOut.write('<p><b>Text:</b> NA</p>')
        writeString = '<p><b>Date:</b> '+date+'</p>'
        writeString = writeString.encode('utf-8')
        try:
            KMLOut.write(writeString)
        except UnicodeEncodeError:
            KMLOut.write('<p><b>Date:</b> NA</p>')
        KMLOut.write('</description> \n')
        data[1] = data[1].replace('}',"")
        tweetAttrList = data[1].split('[')
        tweetAttrList[1] = tweetAttrList[1].replace(']','')
        coordinates = tweetAttrList[1]
        coordinates = coordinates.replace('\n','')
        coordinates = coordinates.replace(' ', '')

        findGISData(str(directory)+'gisData.txt', key, coordinates)

        coordinatesList = coordinates.split(',')
        coordinates_y = coordinatesList[0]
        coordinates_x = coordinatesList[1]
        writeString = '  <Point> \n   <coordinates>'+str(coordinates_x)+','+str(coordinates_y)+'</coordinates> \n  </Point> \n'
        writeString = writeString.encode('utf-8')
        try:
            KMLOut.write(writeString)
        except UnicodeEncodeError:
            KMLOut.write('  <Point> \n   <coordinates>NA</coordinates> \n  </Point> \n')
        tweetAttrData = tweetAttrList[0].split(',')
        geoType = tweetAttrData[0]
        coordinatesTuple = str(tweetAttrData[1])+str(coordinates)
        KMLOut.write(' </Placemark>\n</kml>')
        KMLOut.close()
        count = count+1

def dictToList (dic):
    li = []
    for items in dic:
        key = items
        value = dic[items]
        appendString = str(key)+':'+str(value)
        ##print appendString
        li.append(appendString)
    li = sorted(li)
    fout = open('TEST.txt', 'w')
    fout.write(str(li))
    return li

def listTuplesToCSV (li, foutPath):
    fout = open(foutPath, 'w')
    fout.write('Key,Value \n')
    for items in li:
        itemsList = items.split(':')
        key = itemsList[0]
        value = itemsList[1:]
        fout.write(str(key)+','+str(value)+' \n')

def listTuplesToCSVNumber (li, foutPath):
    fout = open(foutPath, 'w')
    fout.write('Key,Value \n')
    for items in li:
        itemsList = items.split(':')
        key = itemsList[0]
        value = itemsList[1]
        fout.write(str(key)+','+str(value)+' \n')
    fout.close()

def listToCSV (li, foutPath):
    fout = open(foutPath, 'w')
    fout.write('Key,Value \n')
    for items in li:
        key = items[0]
        value = items[1]
        writeString = str(key)+','+str(value)+' \n'
        ##print writeString
        fout.write(writeString)
    fout.close()

def sortList (dictionary): ##Sorts a dictionary by the value
    sortedList = []
    for key in dictionary:
        value = dictionary[key]
        appendTuple = key, value
        sortedList.append(appendTuple)
    sortedList = sorted(sortedList, key=lambda x:x[1], reverse = True)
    return sortedList

def printWordBubble(masterWordBubble):
    fout2 = open(directory+saveas+"wordBubble2.txt", "w")
    print directory+saveas
    sortedList = sortList(masterWordBubble)
    count = 0
    for item in sortedList:
        fout2.write(str(sortedList[count])+" \n")
        count = count+1
    fout2.close()
    return sortedList


##*********THE PROGRAM*********


closeProgram = False
while closeProgram == False: 
    userContinue = True
    masterWordBubble = {}
    waitAndSee = False
    oldCheckIfNew = str
    checkIfNew = "jimmie"
    tweeterDic = {}
    monthDict = {}
    dateDict = {}
    timeDict = {}
    allTweets = {}
    dontStop=False
    address = 'http://search.twitter.com/search.json?&'
    masterAll = {}



    newOrOldProject = raw_input("What query do you want to work with? (1=old, 2=new): ")
    if newOrOldProject == "1":
        numberOfReps = 0
        displayDirectory()
        directoryConfirmation = False
        while directoryConfirmation == False:
            directoryConfirmation, directory = directoryTest(directoryConfirmation)
            directory = str(directory)
        update = raw_input("Do you wish to update the query? 1=yes, 2=no ")
        update = str(update)
        files1 = glob.glob(directory+"\\JSONOutputs\\*")
        startingFileCount = len(files1)
        openData = open(directory+"queryData.txt")
        dataImport = openData.read()
        dataList = dataImport.split('\n')
        saveAsTuple = dataList[0]
        updateCountTuple = dataList[2]
        updateList = updateCountTuple.split(':')
        updateCount = updateList[1]
        saveAsList = saveAsTuple.split(':')
        saveas = saveAsList[1]
        saveas1 = saveas
        files2 = glob.glob(directory+"\\JSONOutputs\\*")
        ## OLD update function, now uses "wait and see" approach
##        if update == '3':
##            maxIDCompareList = []
##            noMoreNew = False
##            numberOfReps2 = 1
##            term = findRefreshQuery(files2, maxIDCompareList)
##            while noMoreNew == False:
##                term = term+'&page='+str(numberOfReps2)
##                info, obj = openWebsite(term)
##                data1 = json.load(obj)
##                checkIfNew = data1['max_id_str']
##                try:
##                    hasValue = allTweets[checkIfNew]
##                    noMoreNew = True
##                except KeyError:
##                    saveas = saveas+'0-'
##                    data = writeJSONFile(directory, saveas, startingFileCount,data1)
##                    allTweets[checkIfNew]=checkIfNew
##                numberOfReps2 = numberOfReps+1
##            term = 'jimmie'

            
        if update == '2':
            closeProgram2 = False
            listOfGeoTweets = []
            while closeProgram2==False:
                saveas = saveas1
                foutGeoString = directory+'geoResults.txt'
                print 'Working - May take several minutes'
                masterAll, refreshQuery = newJSONFile(masterAll, files2) ##MasterAll is dictionary for ALL unique tweets
                masterNoRT, masterRT = findRTFromMaster(masterAll) ##MasterNoRT is dictionary for all original tweets, MasterRT is dictionary of all re-tweets

                print "Total Tweets = "+str(len(masterAll))
                print "Unique Tweets = "+str(len(masterNoRT))
                print "Re-tweets = "+str(len(masterRT))

                datasetChoice = raw_input('Do you want to use all tweets (1), original tweets (2) or only re-tweets (3)? ')
                if datasetChoice == '1':
                    master = masterAll
                    saveas = saveas+'-AllTweets'
                if datasetChoice == '2':
                    master = masterNoRT
                    saveas = saveas+'-NoRT'
                if datasetChoice == '3':
                    master = masterRT
                    saveas = saveas+'-OnlyRT'

                
                try:
                    f1 = open(directory+saveas+'_searchList.txt')
                    searchDic = {}
                    f1Data = f1.read()
                    f1Data = f1Data.replace('{', '')
                    f1Data = f1Data.replace('}', '')
                    f1DataList1 = f1Data.split("', '")
                    for items in f1DataList1:
                        ##print items
                        f1DataList = items.split(':')
                        ##print f1DataList
                        listLength = len(f1DataList)
                        count = 0
                        searchTerm = f1DataList[0]
                        ##print searchTerm
                        searchTerm = searchTerm.replace(' ','')
                        searchTerm = searchTerm.replace("'",'')
                        results = f1DataList[1]
                        ##print results
                        results = results.replace(' ','')
                        results = results.replace("'",'')
                        searchDic[searchTerm]=results
                    f1.close()
                except IOError:
                    searchDic = {}
                print searchDic
                dataMode = raw_input('What type of data do you want? 1=User Tweet Count, 2=Word Bubble (very memory intensive)\n3=Timeline, 4=GIS, 5=SearchByTweetIndex, 6=SearchByTerm) ')
                displayWorking = 0
                
                if str(dataMode)=='1':
                    fout2 = open(directory+saveas+"tweeters.txt", 'w')
                    print "Creating user dictionary"
                    for tweets in master:
                        tweets = str(tweets)
                        tweetDic = master[tweets]
                        tweeterDic = findAndCountUser(tweetDic['from_user'], tweeterDic)
                    sortedList = sortList (tweeterDic)
                    count = 0
                    for item in sortedList:
                        fout2.write(str(sortedList[count])+" \n")
                        count = count+1
                    fout2.close()
                    
                if str(dataMode)=='2':
                    print "Creating word bubble"
                    for tweets in master: ##allows to query dictionary for each distinct tweet for each tweet attribute
                        tweets = str(tweets)
                        tweetDic = master[tweets]
                        masterWordBubble = createWordBubble(masterWordBubble, tweetDic['text'])
                    masterWordBubble = clearStopWords(masterWordBubble)
                    sortedWordBubble = printWordBubble(masterWordBubble)##Also sorts
                    hashDic = findAndCountHash(masterWordBubble)
                    
                if str(dataMode)=='3':
                    print "Creating date list"
                    for tweets in master: ##allows to query dictionary for each distinct tweet for each tweet attribute
                        tweets = str(tweets)
                        tweetDic = master[tweets]
                        monthDict, dateDict, timeDic = findDates(tweetDic['created_at'], monthDict, dateDict, timeDict)
                    sortedTimeList = sortList(timeDic)
                    fout2 = open(directory+saveas+"dates.txt", 'w')
                    for items in monthDict:
                        fout2.write(items+" : "+str(monthDict[items])+" \n")
                    fout2.close()
                ##    for items in dateDict:
                ##        fout3.write(items+" : "+str(dateDict[items])+ " \n")
                    sortedDateList = sortList(dateDict)
                    sortedDateList = sorted(sortedDateList)
                    fout3 = open(directory+saveas+"dates.txt", 'w')
                    for items in sortedDateList:
                        fout3.write(str(items)+' \n')
                    fout3.close()
                    sortedTimeList = sortList(timeDict)
                    sortedTimeList = sorted(sortedTimeList)
                    fout4 = open(directory+saveas+"times.txt", 'w')
                    for items in sortedTimeList:
                        fout4.write(str(items)+' \n')
                    fout4.close()
                    sortedTimeList = sorted(sortedTimeList)
                    print 'Creating CSV ouput'
                    foutString_CSV = timeGraph(sortedTimeList, timeDic, directory, saveas)
                    print 'Finished'
                    userWantsExcel = raw_input('Would you like to view the times in Excel? (1=yes, 2=no) ')
                    if userWantsExcel == '1':
                        os.startfile(foutString_CSV)
    ##                dividesEvenly = checkDivision(int(50), displayWorking)
    ##                if dividesEvenly==True:
    ##                    print str(displayWorking)
    ##                displayWorking = displayWorking+1
                    
                if str(dataMode)=='4':
                    geoDict = getGeoCode(master)
                    limitedGeoDict, fOutGeoString = getGeoCodeLimited(geoDict, directory)
                    for items in limitedGeoDict:
                        listOfGeoTweets.append(items)
                    createKML(fOutGeoString, directory, master)
                    limitedGeoList = dictToList(limitedGeoDict)

                if str(dataMode)=='5':
                    searchTerm = raw_input('What are the tweets you want to find? (by tweetIndex, separated by space OR choose List Name\n GIS List) ' )
                    searchTerm = str(searchTerm)
                    if searchTerm == 'GIS List':
                        searchTermList = listOfGeoTweets
                    if searchTerm != 'GIS List':
                        searchTermList = searchTerm.split(' ')
                    foutSearchStr = directory+saveas+searchTerm+".txt"
                    getTweetsByList(foutSearchStr, searchTermList, master)

                if str(dataMode)=='6':
                    searchTerm = raw_input('What is the word you would like to create a dictionary for? ')
                    searchTerm = searchTerm.lower()
                    searchDic = createSearchDic(searchTerm, master, searchDic)
                    results = searchDic[searchTerm]
                    results = results.replace("'","")
                    resultsList = results.split(',')
                    getTweetsByList(directory+saveas+'_'+searchTerm+'_Results.txt', resultsList, master)
                    
                closeProgram2Input = raw_input('Are you finished with this dataset? (1=yes, 2=no) ')
                if str(closeProgram2Input) == '1':
                    closeProgram2 = True
                    foutList = open(directory+saveas+'_searchList.txt', 'w')
                    foutList.write(str(searchDic))
                    foutList.close()

##            user_continue = True
##            menu1_continue = True
##            menu1 = raw_input('Would you like to save any dictionaries in CSV format? (1=yes, 2=no) ')
##            if menu1 == '1':
##                while menu1_continue == True:
##                    print 'masterWordBubble'
##                    print 'hashDic (Hashtag word bubble)'
##                    print 'geo'
##                    print 'sortedTimeList'
##                    user_wants = raw_input('Please type the object you would like saved as CSV ')
##                    if user_wants == 'masterWordBubble':
##                        masterBubblePath = str(directory+'\\'+saveas+'WordBubble.csv')
##                        listToCSV(sortedWordBubble, masterBubblePath)
##                        print 'Creating CSV output'
##                        print 'Finished'
##                        userWantsExcel = raw_input('Would you like to view the times in Excel? (1=yes, 2=no) ')
##                        if userWantsExcel == '1':
##                            os.startfile(foutString_CSV)
##                        menu1_userContinue = raw_input('Would you like to save another file in CSV? (1=yes, 2=no) ')
##                        if menu1_userContinue == '1':
##                            continue
##                        if menu1_userContinue == '2':
##                            menu1_continue = False
##                        break
##                    if user_wants == 'hashDic':
##                        hashDicPath = str(directory+'\\'+saveas+'HashTagBubble.csv')
##                        print 'Sorry not available at this time'
##                        menu1_userContinue = raw_input('Would you like to save another file in CSV? (1=yes, 2=no) ')
##                        if menu1_userContinue == '1':
##                            continue
##                        if menu1_userContinue == '2':
##                            menu1_continue = False
##                        break
##                    if user_wants == 'geo':
##                        geoDicPath = str(directory+'\\'+saveas+'GeoResults.csv')
##                        listTuplesToCSV(limitedGeoList, geoDicPath)
##                        print 'Creating CSV Output'
##                        print 'Finished'
##                        userWantsExcel = raw_input('Would you like to view the locations in Excel? (1=yes, 2=no) ')
##                        if userWantsExcel == '1':
##                            os.startfile(foutString_CSV)
##                        menu1_userContinue = raw_input('Would you like to save another file in CSV? (1=yes, 2=no) ')
##                        if menu1_userContinue == '1':
##                            continue
##                        if menu1_userContinue == '2':
##                            menu1_continue = False
##                        break
##                    if user_wants == 'sortedTimeList':
##                        sortedTimeList = sorted(sortedTimeList)
##                        print 'Creating CSV ouput'
##                        foutString_CSV = timeGraph(sortedTimeList, timeDic, directory, saveas)
##                        print 'Finished'
##                        userWantsExcel = raw_input('Would you like to view the times in Excel? (1=yes, 2=no) ')
##                        if userWantsExcel == '1':
##                            os.startfile(foutString_CSV)
##                        menu1_userContinue = raw_input('Would you like to save another file in CSV? (1=yes, 2=no) ')
##                        if menu1_userContinue == '1':
##                            continue
##                        if menu1_userContinue == '2':
##                            menu1_continue = False
##                        break
##                    print 'I did not understand, please try again'
                    
        if update == '1':
            numberOfReps = 0
            maxIDCompareList = []
            waitAndSee = False
            saveasTemp = saveas+updateCount+'-'
            print saveas
            while userContinue == True:
                queryDataSave = open(directory+"querydata.txt", "w")
                ##queryDataSave.write("saveas:"+saveas+"\n")
                waitAndSee, numberOfReps, address1, term, saveas1 = waitAndSeeTest(waitAndSee, numberOfReps, address, saveas, 'oldData')
                if numberOfReps == 0:
                    term = findRefreshQuery(files2, maxIDCompareList)
                    print term
                info, obj = openWebsite(term)
                data = json.load(obj)
                checkIfNew = data["max_id_str"]
                tempFile = open('TEMPORARYTEST.txt', 'a')##intended to check the query results coming in
                tempFile.write("currentMaxID:"+checkIfNew+"\n")
                queryDataSave.write("saveas:"+saveas+'\n')
                queryDataSave.write("currentMaxID:"+checkIfNew+"\n")
                queryDataSave.write('updateCount:'+updateCount+'\n')
                print 'Update Count: '+str(updateCount)
                queryDataSave.close()
                if oldCheckIfNew != checkIfNew:
                    data = writeJSONFile(directory, saveasTemp, numberOfReps, data)
                    keyList, keyValueDic = IDTopLevelFields(data)
                    results, numberResults = getResults(data)
                print 'Number of repetitions: '+str(numberOfReps)
                print 'Number of Results: '+str(numberResults)
                if numberOfReps == 0:
                    oldCheckIfNew = data['max_id_str']
                if numberOfReps>=14:
                    waitAndSee = True
                    numberOfReps = 0
                    print 'We Should STOP HERE'
                    updateCount = int(updateCount)
                    updateCount = updateCount+1
                    updateCount = str(updateCount)
                if numberResults < 100:
                    print 'Number of Results: '+str(numberResults)
                    waitAndSee = True
                    numberOfReps = 0
                    updateCount = int(updateCount)
                    updateCount = updateCount+1
                    updateCount = str(updateCount)
                if dontStop == False:
                    if waitAndSee == True:
                        userInput = raw_input("There are no new results... Continue? 1=y, 2=n, 3=Don't Stop)?: ")
                        if userInput == "1":
                            userContinue = True
                            dontStop = False
                            numberOfReps = 0
                        if userInput == "2":
                            userContinue = False
                        if userInput == "3":
                            dontStop=True
                            userContinue = True
                            numberOfReps = 0
                numberOfReps = numberOfReps+1
    
    if newOrOldProject == "2": ## NOTE: Starts new project, currently limited to the exact project I've been working on
        numberOfReps = 0
        directory = "newProject\\"
        directoryConfirmation = False
        while directoryConfirmation == False:
            directory = raw_input("What directory (relative to program root) would you like this saved in?: ")
            print "you entered "+directory
            confirm = raw_input("Is this correct? (1=yes, 2=no) ")
            if confirm == "1":
                directoryConfirmation = True
                directory = directory+"\\"
                directory = createDirectory(directory)
        numberOfReps2 = 0
        while userContinue == True:
            numberResults = 0
            
            waitAndSee, numberOfReps, address, term, saveas = waitAndSeeTest(waitAndSee, numberOfReps, address, saveas, 'newData')
            queryDataSave = open(directory+"querydata.txt", "w")
            queryDataSave.write("saveas:"+saveas+"\n")
            info, obj = openWebsite(term)
            data = json.load(obj)
            checkIfNew = data["max_id_str"]
            
            tempFile = open('TEMPORARYTEST.txt', 'a')##intended to check the query results coming in
            tempFile.write("currentMaxID:"+checkIfNew+"\n")
                           
            queryDataSave.write("currentMaxID:"+checkIfNew+"\n")
            queryDataSave.close()
            if oldCheckIfNew != checkIfNew:
                data = writeJSONFile(directory, saveas, numberOfReps, data)
                keyList, keyValueDic = IDTopLevelFields(data)
                results, numberResults = getResults(data)
    ##            allTweets = checkDirectory(allTweets, results)
    ##            print numberResults
    ##            getGeoCode(results)
    ##            tweeterDic = findAndCountUser(results, tweeterDic)
    ##            monthDict, dateDict, timeDict = findDates(results, monthDict, dateDict, timeDict)
    ##            masterWordBubble = createWordBubble(masterWordBubble, results)
    ##            masterWordBubble = clearStopWords(masterWordBubble)
    ##            printWordBubble(masterWordBubble)
    ##            hashDic = findAndCountHash(masterWordBubble)
            print 'Number of repetitions: '+str(numberOfReps2)
            if numberOfReps == 0:
                oldCheckIfNew = data['max_id_str']
                waitAndSee = False
            if numberOfReps>=14:
                waitAndSee = True
                print 'We Should STOP HERE'
            if numberResults < 100:
                waitAndSee = True
            if dontStop == False:
                if waitAndSee == True:
                    userInput = raw_input("There are no new results... Continue? 1=y, 2=n, 3=Don't Stop)?: ")
                    if userInput == "2":
                        userContinue = False
                        numberOfReps2 = 0
                    if userInput == "3":
                        dontStop=True
                        numberOfReps2 = 0
            numberOfReps = numberOfReps+1
            numberOfReps2 = numberOfReps2+1
    userInputClose = raw_input('Do you wish to close the program? 1=yes, 2=no ')
    if userInputClose == '1':
        closeProgram = True

