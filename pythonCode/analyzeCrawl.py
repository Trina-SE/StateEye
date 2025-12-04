from runCrawljaxBatch import startProcess, getAllThresholds, getBestThresholds, getExistingCrawl
from pythonDBCreator import find, findDir, splitPathIntoFolders
from htmlCreator import singleCrawlOutput
from importResponses import importJson
from time import sleep
from datetime import datetime
import os
import glob
import sys
import csv
import shutil
import json
from globalNames import VERIFIED_CLASSIFICATION_JSON_NAME, GENERATED_CLASSIFICATION_JSON_NAME, GS_JSON_NAME, RESULT_JSON, CONFIG_JSON, UNALTERED_GS_TAG, APPS, THRESHOLD_SETS, isDockerized, buildCrawlFolderName, ALGOS, RESULTS_FOLDER, getHostName

# def compareCrawl():

JAR_PATH = os.path.join(os.path.abspath("../jars"), "comparator-0.0.1-SNAPSHOT-jar-with-dependencies.jar")

def createClassificationJson(gsCrawl, crawl, appName):

	BASE_COMMAND=['java', '-cp', JAR_PATH, 'runner.RQ2Main']
	
	command = BASE_COMMAND.copy()
	command.append(gsCrawl)
	command.append(crawl)
	command.append(appName)

	logFile = os.path.join(crawl, 'classificationLog.log')
	proc = startProcess(command, logFile)
	if proc==None:
		print("Ignoring error command.")
		return
	done = False
	timeDone = 0
	timeStep = 10
	graceTime = 60
	while not done:
		poll = proc.poll()
		if poll == None:
			print("process still running")
			sleep(timeStep)
			timeDone += timeStep
		else:
			done = True
			break
		# if timeDone >= (RUNTIME*60 + graceTime):
		# 	print("Process still running after allocated runtime. So terminating!! ")
		# 	kill_process(proc.pid)
		# 	done=True
		# 	break

	print("Done : {0}".format(command))
	return done

def getThresholdSet(algoStr, threshold, thresholdMap):
	for thresholdSet in thresholdMap:
		print(thresholdSet)
		if algoStr in thresholdMap[thresholdSet] and threshold == thresholdMap[thresholdSet][algoStr]:
			return thresholdSet
				


###########################################################################
## Config and Result Json Analysis ############
###########################################################################

def getUrl(configJson):
	return configJson['url']

def getCrawlFolderName(crawl):
	folders = splitPathIntoFolders(os.path.join(os.path.abspath(crawl),''))
	appSAFThreshold = folders[2]
	return appSAFThreshold

def getAppSAFThresholdFromFolderName(crawl):
	appSAFThreshold = getCrawlFolderName(crawl)
	split = appSAFThreshold.split("_")
	saf = ""
	threshold = ""
	if len(split) == 5:
		saf = split[1] + "_" + split[2]
		threshold = float(split[3])
	else:
		saf = split[1]
		threshold = float(split[2])

	return split[0], saf, threshold

def getSAFandThreshold(configJson):
	svf = configJson["stateVertexFactory"]
	# print(svf)
	if svf == None:
		return "default", -1
	else:
		return svf

def getCrawlTime(resultJson):
	return resultJson['statistics']['duration']

def getReason(resultJson):
	return resultJson['exitStatus']

###########################################################################
## Classification Analysis ############
###########################################################################
def getAllBins(states):
	allBins = []
	for stateName in states:
		state = states[stateName]
		if state['bin'] not in allBins:
			allBins.append(state['bin'])
	return allBins


def getNumBins(states):
	allBins = getAllBins(states)
	return len(allBins)

def getMaxState(states):
	maxState = 0
	for stateName in states:
		state = states[stateName]
		if state['id'] > maxState:
			maxState = state['id']
	return maxState

def getBinRepresentatives(states):
	binRepresentatives = {}
	for stateName in states:
		state = states[stateName]
		binText = state['bin']
		Id = state['id']
		if state['bin'] not in binRepresentatives:
			binRepresentatives[binText] = sys.maxsize
		if Id < binRepresentatives[binText]:
			binRepresentatives[binText] = Id
	return binRepresentatives

def getClonesAndNearDuplicates(jsonData):
	clones = []
	nearDuplicates = []
	nd2 = []
	states = jsonData['states']
	pairs = jsonData['pairs']

	binRepresentatives = getBinRepresentatives(states)

	# print(binRepresentatives)

	for pair in pairs:
		state1 = states[pair['state1']]
		state2 = states[pair['state2']]
		isState1Representative = (state1['id'] == binRepresentatives[state1['bin']])
		isState2Representative = (state2['id'] == binRepresentatives[state2['bin']])
		if pair['response'] == 0:	
			if (not isState1Representative) and (state1['name'] not in clones):
				clones.append(state1['name'])
			if (not isState2Representative) and (state2['name'] not in clones):
				clones.append(state2['name'])
		if pair['response'] == 1:	
			if (not isState1Representative) and (state1['name'] not in nearDuplicates):
				nearDuplicates.append(state1['name'])
			if (not isState2Representative) and (state2['name'] not in nearDuplicates):
				nearDuplicates.append(state2['name'])

		if pair['response'] == 1 and 'dditional' in ''.join(pair['tags']):
			if (not isState1Representative) and (isState2Representative) and (state1['name'] not in nd2):
				nd2.append(state1['name'])
			if (not isState2Representative) and (isState1Representative) and (state2['name'] not in nd2):
				nd2.append(state2['name'])

	nearDuplicatesFiltered = []
	for stateName in nearDuplicates:
		if stateName not in clones:
			nearDuplicatesFiltered.append(stateName)


	# print(clones)
	# print(nearDuplicates)
	print(nd2)

	return len(clones), len(nearDuplicatesFiltered), len(nd2)





###########################################################################
## Gold Standard improvements ############
###########################################################################
def updateGoldStandardJsonWithUrls(gsCrawl):
	resultJson = os.path.join(gsCrawl, RESULT_JSON)
	if not os.path.exists(resultJson):
		print("Result JSON not found at : {0}".format(resultJson))
		return None
	resultJsonData = importJson(resultJson)

	gsJson = os.path.join(gsCrawl, 'gs', GS_JSON_NAME)
	if not os.path.exists(gsJson):
		print("GS JSON not found at : {0}".format(gsJson))
		return None
	gsJsonData = importJson(gsJson)
	if(gsJsonData == None):
		print("Error Import Gold Standard Json")
		return
	states = resultJsonData['states']
	gsStates = gsJsonData['states']
	noUrl = False
	for state in states:
		if state in gsStates:
			if 'id' not in gsStates[state]:
				noUrl = True
				gsStates[state]['url'] = states[state]['url']

	if noUrl:
		shutil.copy2(gsJson, os.path.join(gsCrawl, 'gs', 'gsResults_noUrl.json'))
		with open(gsJson, "w") as write_file:
			json.dump(gsJsonData, write_file)

def updateGoldStandardJsonWithIds(gsCrawl):
	resultJson = os.path.join(gsCrawl, RESULT_JSON)
	if not os.path.exists(resultJson):
		print("Result JSON not found at : {0}".format(resultJson))
		return None
	resultJsonData = importJson(resultJson)

	gsJson = os.path.join(gsCrawl, 'gs', GS_JSON_NAME)
	if not os.path.exists(gsJson):
		print("GS JSON not found at : {0}".format(gsJson))
		return None
	gsJsonData = importJson(gsJson)
	if(gsJsonData == None):
		print("Error Import Gold Standard Json")
		return
	states = resultJsonData['states']
	gsStates = gsJsonData['states']
	noId = False
	for state in states:
		if state in gsStates:
			if 'id' not in gsStates[state]:
				noId = True
				gsStates[state]['id'] = states[state]['id']

	if noId:
		shutil.copy2(gsJson, os.path.join(gsCrawl, 'gs', 'gsResults_noId.json'))
		with open(gsJson, "w") as write_file:
			json.dump(gsJsonData, write_file)

def writeNewGoldStandardJsonAndHtml(newGSJsonData, gsCrawl):
	HTML_OUTPUT_PATH = os.path.join(os.path.abspath(gsCrawl), "gs")
	gsResultsPath = os.path.join(HTML_OUTPUT_PATH, "gsResults.json")
	if os.path.exists(gsResultsPath):
		backup = os.path.join(HTML_OUTPUT_PATH, "gsResultsBackup_" + str(datetime.now().strftime("%Y%m%d-%H%M%S")) + ".json")
		shutil.move(gsResultsPath, backup)

	OUTPUT_HTML_NAME = "gs.html"
	TITLE = "GoldStandard"
	singleCrawlOutput(gsCrawl, HTML_OUTPUT_PATH, OUTPUT_HTML_NAME, TITLE, outputJson = newGSJsonData, saveJsonName = 'gsResults.json', overwrite = True)
	# with open("data_file.json", "w") as write_file:
	#     json.dump(data, write_file)

def getNextId(states):
	maxId = 0
	for state in states:
		if states[state]['id'] > maxId:
			maxId = states[state]['id']
	return maxId + 1

def getStateJsonToAdd(stateToAdd, Id):
	
	Name = "state" + str(Id)
	TimeAdded = -1
	Url = stateToAdd['url']
	Bin = stateToAdd['bin']
	Clones = [] 
	return {
	        "name": Name,
	        "bin": Bin,
	        "clones": [],
	        "timeAdded": TimeAdded,
	        "id": Id,
	        "url": Url
    		}

def getPairJsonToAdd(newStateJson, existingStateJson):
    return {
        "state1": newStateJson['name'],
        "state2": existingStateJson['name'],
        "tags": ["Different Crawls"],
        "response": 2,
        "inferred": 1
    }


def	addToGoldStandard(newBins, gsCrawl, crawl, gsJsonData, crawlJsonData):
	errored = []
	gsCrawl_unaltered = os.path.abspath(gsCrawl) + UNALTERED_GS_TAG
	gsStates = gsJsonData['states']
	crawlStates = crawlJsonData['states']
	allBins = getAllBins(gsStates)
	statesToAdd = {}
	pairsToAdd = []
	nextId = getNextId(gsStates)
	for newBin in newBins:
		if newBin not in allBins:
			if not os.path.exists(gsCrawl_unaltered):
				shutil.copytree(gsCrawl,gsCrawl_unaltered)
			stateToAdd = crawlStates[newBins[newBin]]
			newStateJson = getStateJsonToAdd(stateToAdd, nextId)
			
			# Add files to GS Crawl
			newStatePath = os.path.join(gsCrawl, "states", newStateJson['name'] + ".html") 
			newDomPath = os.path.join(gsCrawl, "doms", newStateJson['name'] + ".html") 
			newScreenshotPath = os.path.join(gsCrawl, "screenshots", newStateJson['name'] + ".png") 
			if os.path.exists(newStatePath) or os.path.exists(newDomPath) or os.path.exists(newScreenshotPath):
				errored.append((newBin, newStateJson))
				continue
			oldStatePath = os.path.join(crawl, "states", stateToAdd['name']+ ".html")
			oldDomPath = os.path.join(crawl, "doms", stateToAdd['name'] + ".html") 
			oldScreenshotPath = os.path.join(crawl, "screenshots", stateToAdd['name'] + ".png") 
			shutil.copy2(oldStatePath, newStatePath)
			shutil.copy2(oldDomPath, newDomPath)
			shutil.copy2(oldScreenshotPath, newScreenshotPath)

			statesToAdd[newStateJson['name']] = newStateJson
			for existingState in gsStates:
				newPairJson = getPairJsonToAdd(newStateJson, gsStates[existingState])
				pairsToAdd.append(newPairJson)	

			nextId +=1
			
	returnJson = {'states':statesToAdd, 'pairs':pairsToAdd}
	print("States TO ADD")
	print(statesToAdd)
	print("Errored {0}".format(str(len(errored))))
	print(errored)
	return returnJson, errored

###########################################################################
## Utils ############
###########################################################################
def parseCrawlTime(crawlTime):
	try:
		crawlTime = crawlTime.lower()
		crawlTime = crawlTime.replace('minutes','minute')
		crawlTime =crawlTime.replace('minute','*60+')
		crawlTime =crawlTime.replace('seconds','second')
		crawlTime =crawlTime.replace('second', '')
		# print(crawlTime)
		crawlTime = crawlTime.strip()
		if(crawlTime.endswith('+')):
			crawlTime = crawlTime.replace('+','')

		return eval(crawlTime)
	except Exception as ex:
		print(ex)
		print("unable to parse crawltime {0}".format(crawlTime))

def getThresholdSetName(thresholdSet):
	try:
		threshold = ''
		dataSet = ''
		if thresholdSet[0] == 'gs_db_data':
			dataSet = "_SS"
		else:
			dataSet = "_DS"

		if thresholdSet[2] == 'optimal':
			threshold = 'O_s'
		elif thresholdSet[2] == 'humanND_median':
			threshold = 'St_n'
		elif thresholdSet[2] == 'humanNDDyn_median':
			threshold = 'St_n3'

		return threshold+dataSet

	except Exception as ex:
		print(ex)
		print('Error getting thresholdSetName')
		return None

def getNewDiscoveries(jsonData, oldGsCrawl, crawl):
	newDiscoveries = []
	gsJson = os.path.join(oldGsCrawl, 'gs', GS_JSON_NAME)
	if not os.path.exists(gsJson):
		print("GS JSON not found at : {0}".format(gsJson))
		return None
	gsJsonData = importJson(gsJson)
	allGsBins = getAllBins(gsJsonData['states'])
	allCrawlBins = getAllBins(jsonData['states'])
	binRepresentatives = getBinRepresentatives(jsonData['states'])
	for crawlBin in allCrawlBins:
		if crawlBin == "":
			continue
		if crawlBin not in allGsBins:
			newDiscoveries.append({crawlBin:binRepresentatives[crawlBin]})

	newDiscoveriesPath = os.path.join(crawl, 'comp_output', 'newDiscoveries.json')
	try:
		with open(newDiscoveriesPath, 'w') as write_file:
			json.dump(newDiscoveries, write_file)
	except Exception as ex:
		print("Could not wirte new Discoveries file to {0}".format(newDiscoveriesPath))
		print(ex)

	return len(newDiscoveries)

def getStats(jsonData, gsJsonData, resultJson, configJson, crawl, thresholdEntry):
	app, saf, threshold = getAppSAFThresholdFromFolderName(crawl)
	thresholdSet = thresholdEntry
	crawlTime = getCrawlTime(resultJson)
	reason = getReason(resultJson)
	numStates=-1
	numCrawledStates=-1
	numClones=-1
	numNearDuplicates=-1
	numUniqueStates = -1
	numNd2 = -1
	coverage=-1
	totalBins = getNumBins(gsJsonData['states'])
	foundBins = getNumBins(jsonData['states'])
	coverage = foundBins/totalBins
	numStates = len(jsonData['states'])
	numAddedStates = numStates
	numCrawledStates = getMaxState(jsonData['states']) + 1
	numClones, numNearDuplicates, numNd2 = getClonesAndNearDuplicates(jsonData)
	numUniqueStates = numStates - (numClones + numNearDuplicates)

	thresholdSetName = getThresholdSetName(thresholdSet)

	duration = parseCrawlTime(crawlTime)

	returnMap = {"Application" : app,
	"SAF" : saf,
	"ThresholdSet" : thresholdSet,
	"ThresholdSetName" : thresholdSetName,
	"Threshold" : threshold,
	"CrawlTime" : duration,
	"Reason" : reason,
	"numStates":numStates, "numCrawledStates":numCrawledStates, "numClones":numClones, "numNearDuplicates":numNearDuplicates,
				 "numNd2": numNd2, "numUniqueStates":numUniqueStates, "coverage":coverage}
	
	return returnMap

def getStats_old(jsonData, gsJsonData, resultJson, configJson, crawl, thresholdMap = getAllThresholds()):
	app, saf, threshold = getAppSAFThresholdFromFolderName(crawl)
	thresholdSet = getThresholdSet(saf, threshold, thresholdMap)
	crawlTime = getCrawlTime(resultJson)
	reason = getReason(resultJson)
	numStates=-1
	numCrawledStates=-1
	numClones=-1
	numNearDuplicates=-1
	numUniqueStates = -1
	coverage=-1
	totalBins = getNumBins(gsJsonData['states'])
	foundBins = getNumBins(jsonData['states'])
	coverage = foundBins/totalBins
	numStates = len(jsonData['states'])
	numAddedStates = numStates
	numCrawledStates = getMaxState(jsonData['states']) + 1
	numClones, numNearDuplicates = getClonesAndNearDuplicates(jsonData)
	numUniqueStates = numStates - (numClones + numNearDuplicates)
	
	returnMap = {"Application" : app,
	"SAF" : saf,
	"ThresholdSet" : thresholdSet,
	"Threshold" : threshold,
	"CrawlTime" : crawlTime,
	"Reason" : reason,
	"numStates":numStates, "numCrawledStates":numCrawledStates, "numClones":numClones, "numNearDuplicates":numNearDuplicates, "numUniqueStates":numUniqueStates, "coverage":coverage}
	
	return returnMap
	
STATUS_GS_UPDATED = "GoldStandardUpdated"

STATUS_FOUND_VERIFIED_CLASSIFICATION = "found_verified_classification_json"
STATUS_CREATED_CLASSIFICATION_HTML = "created_classification_json"
STATUS_STATS_CREATED= "stats_created"
STATUS_JSON_NOT_FOUND = "required_json_not_found"
STATUS_ERROR_CREATING_CLASSIFICATION = "ERROR_CREATING_CLASSIFICATION json"
STATUS_GSJSON_NOT_FOUND = "gsJson not found"
STATUS_SKIPPED_CLASSIFICATION_HTML_CREATION = "Classification skipped"

def analyze(gsCrawl, crawl, appName, thresholdEntry, preDefinedSaveJsonLocation=None):
	status = None
	gsJson = os.path.join(gsCrawl, 'gs', GS_JSON_NAME)
	if not os.path.exists(gsJson):
		print("GS JSON not found at : {0}".format(gsJson))
		status = STATUS_GSJSON_NOT_FOUND
		return status, None
	gsJsonData = importJson(gsJson)
	saveJsonName = getCrawlFolderName(crawl) + "_" + VERIFIED_CLASSIFICATION_JSON_NAME
	verifClassificationJson = os.path.join(crawl, 'comp_output', VERIFIED_CLASSIFICATION_JSON_NAME)
	HTML_OUTPUT_PATH = os.path.join(os.path.abspath(crawl), "html_classification")

	if (not os.path.exists(verifClassificationJson)) and (preDefinedSaveJsonLocation!=None) and (os.path.exists(HTML_OUTPUT_PATH)):
		saveJsons = find(saveJsonName, preDefinedSaveJsonLocation)
		if len(saveJsons) > 0:
			saveJson = saveJsons[0]
			try:
				shutil.copy2(saveJson, verifClassificationJson)
				shutil.move(saveJson, saveJson + "_backup")
				print("Moved classification_verified.json to {0}".format(verifClassificationJson))
			except Exception as ex:
				print(ex)
				print("Could not move classification_verified to the right location.")

	if not os.path.exists(verifClassificationJson):
		classificationJson = os.path.join(crawl, 'comp_output', GENERATED_CLASSIFICATION_JSON_NAME)
		if not os.path.exists(classificationJson) and not DRY_RUN:
			print("classification json not found {0}".format(classificationJson))
			done = createClassificationJson(gsCrawl, crawl, appName)
			print("Done running classification : {0}".format(str(done)))
			sleep(2)

			if not os.path.exists(classificationJson):
				status = STATUS_ERROR_CREATING_CLASSIFICATION
				return status, None

		if os.path.exists(classificationJson):
			jsonData = importJson(classificationJson)
			OUTPUT_HTML_NAME = "classification.html"
			TITLE = "Classification HTML"
			
			preLoadedBins = getAllBins(gsJsonData['states'])
			singleCrawlOutput(crawl, HTML_OUTPUT_PATH, OUTPUT_HTML_NAME, TITLE, outputJson = jsonData, saveJsonName = saveJsonName, preLoadedBins = preLoadedBins, overwrite = 'y' )
			status = STATUS_CREATED_CLASSIFICATION_HTML
			return status, None
		elif DRY_RUN:
			status = STATUS_SKIPPED_CLASSIFICATION_HTML_CREATION
			return status, None
		else :
			status = STATUS_JSON_NOT_FOUND
			return status, None

	else:
		jsonData = importJson(verifClassificationJson)

		resultJson = os.path.join(crawl, RESULT_JSON)
		if not os.path.exists(resultJson):
			print("Result JSON not found at : {0}".format(resultJson))
			status = STATUS_JSON_NOT_FOUND
			return status,None

		configJson = os.path.join(crawl, CONFIG_JSON)
		if not os.path.exists(configJson):
			print("Config JSON not found at : {0}".format(configJson))
			status = STATUS_JSON_NOT_FOUND
			return status,None

		resultJsonData = importJson(resultJson)
		configJsonData = importJson(configJson)
		
		if 'newBins' in jsonData:
			toAdd, errored = addToGoldStandard(jsonData['newBins'], gsCrawl, crawl, gsJsonData, jsonData)
			if len(errored) >0:
				print("Some bins could not be added to the Gold Standard. Find out why ")

				
			toAddStates = toAdd['states']
			toAddPairs = toAdd['pairs']
			if len(toAddPairs) != 0:
				newStatesJson = gsJsonData['states']
				newPairsJson = gsJsonData['pairs']
				for state in toAddStates:
					newStatesJson[state] = toAddStates[state]

				for pair in toAddPairs:
					newPairsJson.append(pair)

				newGSJsonData = {'states' : newStatesJson, 'pairs': newPairsJson}
				writeNewGoldStandardJsonAndHtml(newGSJsonData, gsCrawl)
				status = STATUS_GS_UPDATED
				return status,None

		stats = getStats(jsonData, gsJsonData, resultJsonData, configJsonData, crawl, thresholdEntry)

		if os.path.exists(os.path.abspath(gsCrawl)+UNALTERED_GS_TAG):
			newDiscoveries = getNewDiscoveries(jsonData, os.path.abspath(gsCrawl)  + UNALTERED_GS_TAG, crawl)
			stats["newDiscoveries"] = newDiscoveries
		else:
			stats["newDiscoveries"] = 0

		print(stats)
		status = STATUS_STATS_CREATED
		return status, stats

def writeCSV(csvFields, csvRows, dst):
	# print(csvRows)
	with open(dst, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=csvFields)
		writer.writeheader()

		for row in csvRows:
			writer.writerow(row)

def getCrawlsToAnalyze(crawlPath=None,app=None, host=None, runtime = 5, bestCrawls = False):
	if crawlPath==None:
		crawlPath = os.path.join(".","out")

	crawlMap = {}
	returnCrawls = []
	missingCrawls = []
	for appName in APPS:
		if app!=None and app!=appName:
			continue

		if(bestCrawls):
			thresholds, thresholdPerSAF = getBestThresholds(appName)
		else:
			thresholds, thresholdPerSAF = getAllThresholds(appName)

		for algo in ALGOS:
			algoStr = str(algo).split('.')[1].upper()

			# for thresholdSet in THRESHOLDS:
			safThresholds = thresholdPerSAF[algoStr]

			for thresholdSet in thresholds:
				threshold = thresholds[thresholdSet][algoStr]
				existingCrawlData = getExistingCrawl(appName, algoStr, str(float(threshold)), runtime, ALL_CRAWLS = crawlPath)
				existingValidCrawls = existingCrawlData['existingValidCrawls']
				crawljaxOutputPath = existingCrawlData['path']
				print(existingCrawlData)
			
				if crawljaxOutputPath is None or len(existingValidCrawls) == 0:
					# if(host is None):
					# 	if isDockerized(appName):
					# 		host = "192.168.99.101"
					# 	else :
					# 		host = "localhost"
					crawlFolderName = appName + "_" + algoStr + "_" + str(float(threshold))+ "_" + str(runtime) + "mins"
					crawljaxOutputPath = os.path.abspath(os.path.join(crawlPath, appName, crawlFolderName))
					missingCrawls.append(crawljaxOutputPath)

				for validCrawl in existingValidCrawls:
					if validCrawl not in returnCrawls:
						path,file = os.path.split(validCrawl)
						returnCrawls.append(path)
						crawlMap[path] = thresholdSet


	print(len(returnCrawls))
	return returnCrawls, crawlMap, missingCrawls


def analyzeBestCrawlsForApp(appName, allCrawls = "../out/", gsCrawls = "", runtime=5):
	
	GS_CRAWL = os.path.join(os.path.abspath(gsCrawls), appName, 'crawl-'+appName+'-60min')

	toBeVerified = []
	gsUpdated = []
	analyzed = []
	MissingCrawls = []
	erroredCrawls = []
	preDefinedSaveJsonLocation = os.path.abspath("../saveJsons")

	crawlsToAnalyze, crawlMap, missingCrawls = getCrawlsToAnalyze(allCrawls, appName, runtime= runtime)
	print(crawlMap)
	print(crawlsToAnalyze)
	# print("missing")
	# print(missingCrawls)
	csvRows = []

	thresholds, thresholdPerSAF = getBestThresholds(appName)
	for algo in ALGOS:
		algoStr = str(algo).split('.')[1].upper()

		if algoStr not in bestAlgos:
			continue

		safThresholds = thresholdPerSAF[algoStr]

		for threshold in safThresholds:

			folderName = buildCrawlFolderName(appName, algoStr, threshold, runtime)
			hostName = getHostName(os.path.join(os.path.abspath(allCrawls), appName, folderName))

			if hostName is None:
				print("Could not find hostname for {0}".format(folderName))
				MissingCrawls.append(os.path.join(os.path.abspath(allCrawls), appName, folderName))
				continue
	
			crawl = os.path.join(os.path.abspath(allCrawls), appName, folderName, hostName, 'crawl0')
			print(crawl)
			status, stats = analyze(GS_CRAWL, crawl, appName, preDefinedSaveJsonLocation=preDefinedSaveJsonLocation, thresholdEntry = crawlMap[crawl])
			# print(status)
			# print( stats)
			if status == STATUS_GSJSON_NOT_FOUND or status == STATUS_JSON_NOT_FOUND:
				erroredCrawls.append(crawl)


			if status == STATUS_ERROR_CREATING_CLASSIFICATION:
				if crawl not in erroredCrawls:
					erroredCrawls.append(crawl)

			if status == STATUS_SKIPPED_CLASSIFICATION_HTML_CREATION:
				if crawl not in toBeVerified:
					toBeVerified.append(crawl)

			if status== STATUS_CREATED_CLASSIFICATION_HTML:
				if crawl not in toBeVerified:
					toBeVerified.append(crawl)

			if status == STATUS_GS_UPDATED:
				print("Gold Standard Has been updated from {0}. Please verify and rerun the analysis.". format(crawl))
				gsUpdated.append(GS_CRAWL)
				return {"status" : STATUS_GS_UPDATED, "toBeVerified": toBeVerified, "gsUpdated": gsUpdated, "MissingCrawls": MissingCrawls, "erroredCrawls": erroredCrawls, "analyzed":analyzed, "csvRows":csvRows}
			if stats !=None:
				csvRows.append(stats)
				analyzed.append(crawl)

	
	return {"status" : gsUpdated, "toBeVerified": toBeVerified, "gsUpdated": gsUpdated, "MissingCrawls": MissingCrawls, "erroredCrawls": erroredCrawls, "analyzed":analyzed, "csvRows":csvRows}


def analyzeBestCrawls(GOLDSTANDARDS, ALL_CRAWLS, runtime = 30):
	# csvFields = ["Application", "SAF", "ThresholdSet", "ThresholdSetName", "Threshold", "CrawlTime", "Reason", "numStates", "numCrawledStates", "numClones", "numNearDuplicates", "numUniqueStates", "newDiscoveries", "coverage"]
	csvRows = []
	toBeVerified = []
	gsUpdated = []
	analyzed = []
	MissingCrawls = []
	erroredCrawls = []

	for app in APPS:
		returnObject = analyzeBestCrawlsForApp(app, ALL_CRAWLS, GOLDSTANDARDS, runtime = runtime)
		status = returnObject["status"]
		if status == STATUS_GS_UPDATED:
			print("Gold Standard Has been updated for {0}. Please verify and rerun the analysis.". format(app))
			gsUpdated.extend(returnObject['gsUpdated'])

		toBeVerified.extend(returnObject['toBeVerified'])
		analyzed.extend(returnObject['analyzed'])
		MissingCrawls.extend(returnObject['MissingCrawls'])
		erroredCrawls.extend(returnObject['erroredCrawls'])
		csvRows.extend(returnObject['csvRows'])

	print("Analyzed : {0}".format(str(len(analyzed))))
	print(analyzed)

	print("To be Verified  : {0}".format(str(len(toBeVerified))))
	print(toBeVerified)

	print("GS UPDATED : {0}".format(str(len(gsUpdated))))
	print(gsUpdated)

	print("Missing Crawls : {0}".format(str(len(MissingCrawls))))
	print(MissingCrawls)

	print("ErroredCrawls : {0}".format(str(len(erroredCrawls))))
	print(erroredCrawls)

	#### WRITE OUTPUT ########
	writeCSV(csvFields, csvRows, os.path.join(os.path.abspath(".."), RESULTS_FOLDER, "analysis_BestCrawls_" + str(runtime) + "min.csv"))


def analyzeBestCrawls_new(GOLDSTANDARDS, ALL_CRAWLS, folderPattern = ('*/localhost/crawl*/'), runtime = 30):
	toBeVerified = []
	gsUpdated = []
	analyzed = []
	MissingCrawls = []
	erroredCrawls = []

	preDefinedSaveJsonLocation = os.path.abspath("../saveJsons")
	csvRows = []

	for appName in APPS:
		GS_CRAWL = os.path.join(os.path.abspath(GOLDSTANDARDS), appName, 'crawl-' + appName + '-60min')
		# crawlsToAnalyze = glob.glob(os.path.join(os.path.abspath(ALL_CRAWLS), appName) + '/' + appName + folderPattern)
		crawlsToAnalyze, crawlMap, missingCrawls = getCrawlsToAnalyze(ALL_CRAWLS, appName, host="192.168.99.101", runtime = 60)
		print(crawlsToAnalyze)
		MissingCrawls.extend(missingCrawls)
		for crawl in crawlsToAnalyze:
			# if (crawl in toBeVerified) or (crawl in analyzed):
			# 	continue
			status,stats = analyze(GS_CRAWL, crawl, appName, preDefinedSaveJsonLocation=preDefinedSaveJsonLocation, thresholdEntry = crawlMap[crawl])

			if status == STATUS_ERROR_CREATING_CLASSIFICATION:
				if crawl not in erroredCrawls:
					erroredCrawls.append(crawl)

			if status == STATUS_SKIPPED_CLASSIFICATION_HTML_CREATION:
				if crawl not in toBeVerified:
					toBeVerified.append(crawl)


			if status== STATUS_CREATED_CLASSIFICATION_HTML:
				if crawl not in toBeVerified:
					toBeVerified.append(crawl)

			if status == STATUS_GS_UPDATED:
				print("Gold Standard Has been updated from {0}. Please verify and rerun the analysis.". format(crawl))
				gsUpdated.append(GS_CRAWL)
				return

			if stats !=None:
				csvRows.append(stats)
				analyzed.append(crawl)
	
	print("Analyzed : {0}".format(str(len(analyzed))))
	print(analyzed)

	print("To be Verified  : {0}".format(str(len(toBeVerified))))
	print(toBeVerified)

	print("GS UPDATED : {0}".format(str(len(gsUpdated))))
	print(gsUpdated)

	print("Missing Crawls : {0}".format(str(len(MissingCrawls))))
	print(MissingCrawls)
	
	print("ErroredCrawls : {0}".format(str(len(erroredCrawls))))
	print(erroredCrawls)
	#### WRITE OUTPUT ########
	writeCSV(csvFields, csvRows, os.path.join(os.path.abspath(".."), RESULTS_FOLDER, "analysis_BestCrawls_" + str(runtime) + "min.csv"))


def analyzeAllCrawls(GOLDSTANDARDS, ALL_CRAWLS, folderPattern = ('*/localhost/crawl*/')):
	toBeVerified = []
	gsUpdated = []
	analyzed = []
	MissingCrawls = []
	erroredCrawls = []

	preDefinedSaveJsonLocation = os.path.abspath("../saveJsons")
	csvFields = ["Application", "SAF", "ThresholdSet", "ThresholdSetName", "Threshold", "CrawlTime", "Reason", "numStates", "numCrawledStates", "numClones", "numNearDuplicates", "numUniqueStates", "newDiscoveries", "coverage"]
	csvRows = []

	for appName in APPS:
		GS_CRAWL = os.path.join(os.path.abspath(GOLDSTANDARDS), appName, 'crawl-' + appName + '-60min')
		# crawlsToAnalyze = glob.glob(os.path.join(os.path.abspath(ALL_CRAWLS), appName) + '/' + appName + folderPattern)
		crawlsToAnalyze, crawlMap, missingCrawls = getCrawlsToAnalyze(ALL_CRAWLS, appName, host="192.168.99.101")
		print(crawlsToAnalyze)
		MissingCrawls.extend(missingCrawls)
		for crawl in crawlsToAnalyze:
			# if (crawl in toBeVerified) or (crawl in analyzed):
			# 	continue
			status,stats = analyze(GS_CRAWL, crawl, appName, preDefinedSaveJsonLocation=preDefinedSaveJsonLocation, thresholdEntry = crawlMap[crawl])
			
			if status == STATUS_GSJSON_NOT_FOUND or status == STATUS_JSON_NOT_FOUND:
				erroredCrawls.append(crawl)

			if status == STATUS_ERROR_CREATING_CLASSIFICATION:
				if crawl not in erroredCrawls:
					erroredCrawls.append(crawl)

			if status== STATUS_CREATED_CLASSIFICATION_HTML:
				toBeVerified.append(crawl)

			if status == STATUS_GS_UPDATED:
				print("Gold Standard Has been updated from {0}. Please verify and rerun the analysis.". format(crawl))
				gsUpdated.append(GS_CRAWL)
				return

			if stats !=None:
				csvRows.append(stats)
				analyzed.append(crawl)
	
	print("Analyzed : {0}".format(str(len(analyzed))))
	print(analyzed)

	print("To be Verified  : {0}".format(str(len(toBeVerified))))
	print(toBeVerified)

	print("GS UPDATED : {0}".format(str(len(gsUpdated))))
	print(gsUpdated)

	print("Missing Crawls : {0}".format(str(len(MissingCrawls))))
	print(MissingCrawls)
	
	print("ErroredCrawls : {0}".format(str(len(erroredCrawls))))
	print(erroredCrawls)
	#### WRITE OUTPUT ########
	writeCSV(csvFields, csvRows, os.path.join(os.path.abspath(".."), RESULTS_FOLDER, "analysis_AllCrawls_5min.csv"))
	

###########################################################################
## Tests ############
###########################################################################
def testFindDir():
	ALL_CRAWLS = ''
	found = glob.glob(ALL_CRAWLS + '/petclinic*')
	print(found)

def testGetSAF():
	testConfigData = importJson("/out/petclinic/petclinic_DEFAULT_-1.0_60mins/localhost/crawl0/config.json")
	getSAF(testConfigData)

def test_getAppSAFThresholdFromFolderName():
	testFolderName = "out/petclinic/petclinic_DEFAULT_-1.0_60mins/localhost/crawl0/"
	print(getAppSAFThresholdFromFolderName(testFolderName))

def testCSVWrite():
	testCSVFieldNames = ["Application", "SAF", "Threshold", "crawlTime", "reasonForEndingCrawl", "numStates", "numCrawledStates", "numClones", "numNearDuplicates", "numUniqueStates", "coverage"]
	
	testCSVRows = []
	testCSVRows.append({'Application': 'petclinic', 'SAF': 'VISUAL_BLOCKHASH', 'Threshold': 0.0, 'crawlTime': '5 minutes 8 seconds', 'numStates': 16, 'numCrawledStates': 89, 'numClones': 6, 'numNearDuplicates': 2, 'numUniqueStates': 8, 'coverage': 0.5714285714285714})

	testDst = "analysisTest.csv"


	writeCSV(testCSVFieldNames, testCSVRows, testDst)

def testGetThresholdSet():
	thresholds, thresholdPerSAF  = getAllThresholds()
	for thresholdSet in thresholds:
		print(thresholdSet[2])

def testGoldStandardAddition():
	TEST_GS_CRAWL = 'Addressbook/crawl-addressbook-60min/'

	analyze(TEST_GS_CRAWL, "/addressbook_VISUAL_BLOCKHASH_0.0_5mins/localhost/crawl0/", "addressbook")

def testUpdateGoldStandardJsonWithIds():

	updateGoldStandardJsonWithIds(TEST_GS_CRAWL)


def testUpdateGoldStandardJsonWithUrls():
	TEST_GS_CRAWL = '/Petclinic/crawl-petclinic-60min_old/'

	updateGoldStandardJsonWithUrls(TEST_GS_CRAWL)

def testGetCrawlsToAnalyze():
	print(getCrawlsToAnalyze("/out"))

def testGetCoverage():
	gsJson =importJson("GoldStandards/petclinic/crawl-petclinic-60min/gs/gsResults.json")
	states = gsJson['states']
	print(getNumBins(states))

def testParseCrawlTime():
	print( parseCrawlTime("5 minutes 4seconds"))

###########################################################################
## Main ############
###########################################################################
# bestAlgos = ['DOM_RTED', 'VISUAL_SSIM', 'VISUAL_BLOCKHASH', 'VISUAL_PDIFF', 'DOM_LEVENSHTEIN', 'VISUAL_HYST', 'HYBRID']
bestAlgos = ['DOM_RTED', 'HYBRID', 'VISUAL_HYST']

csvFields = ["Application", "SAF", "ThresholdSet", "ThresholdSetName", "Threshold", "CrawlTime", "Reason", "numStates", "numCrawledStates", "numClones", "numNearDuplicates", "numNd2", "numUniqueStates", "newDiscoveries", "coverage"]

DRY_RUN= False

if __name__=="__main__":
	# testFindDir()
	# testGetSAF()
	# test_getAppSAFThresholdFromFolderName()
	# testCSVWrite()
	# testGetThresholdSet()
	# testGoldStandardAddition()
	# testUpdateGoldStandardJsonWithIds()
	# testUpdateGoldStandardJsonWithUrls()
	# testGetCrawlsToAnalyze()
	# testGetCoverage()
	# testParseCrawlTime()

	# print(str(len(crawlsToAnalyze)))
	# print(str(len(missingCrawls)))
	# print(crawlsToAnalyze)


	GS_CRAWL = '/home/fraggen/fraggen/GroundTruth'

	ALL_CRAWLS = "/home/fraggen/fraggen/out"

	# ALL_CRAWLS = "../paper-crawls"
	runtime = 60

	# analyzeBestCrawls(GOLDSTANDARDS=GS_CRAWL, ALL_CRAWLS=ALL_CRAWLS, runtime=runtime)
	returnObject = analyzeBestCrawlsForApp('addressbook', ALL_CRAWLS, GS_CRAWL, runtime=runtime)
	
