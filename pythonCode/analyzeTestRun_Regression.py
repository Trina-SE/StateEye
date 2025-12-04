import random
from datetime import datetime
import shutil
from subprocess import Popen

from analyzeTestRun import getTestRun, getMethodNumber, createOracleJsons, JAR_PATH
from analyzeCrawl import getCrawlsToAnalyze, writeCSV, getCrawlFolderName, getAllBins, getNumBins
import os

from analyzeTestRun_alt import initStateMap
from htmlCreator import oracleClassification, testFailureAnalysis
from importResponses import importJson
from globalNames import RESULTS_FOLDER, APPS, TEST_ANALYSIS_JSON, RESULT_JSON, TEST_ANALYSIS_FOLDER, RESULT_SKEL_JSON, \
	VERIFIED_CLASSIFICATION_JSON_NAME, APP_CHANGE_ANALYSIS_JSON, GS_JSON_NAME
from runCrawljaxBatch import startProcess, getBestThresholds
from time import sleep

from utils import exportJson

testStats = []
stateMap = {}
failedAnalyses = []


def analyzeTestRuns(crawlPath="/home/fraggen/fraggen/paper-crawls", runtime=60, app=None, bestCrawls=True,
					toBeAnalyzed=None):
	returnCrawls, crawlMap, missingCrawls = getCrawlsToAnalyze(crawlPath=crawlPath,
															   app=app, host="localhost", runtime=runtime,
															   bestCrawls=bestCrawls)
	global testStats
	global failedAnalyses

	testRows = []
	# returnMap = []
	for crawl in returnCrawls:
		testRunList = getTestRun(crawl)
		if len(testRunList) == 0:
			print("No Test run found for {0}".format(crawl))
			continue

		crawlStats = analyzeTestSource(crawl)

		for testRun in testRunList:
			testRunJson = os.path.join(testRun, "testRun.json")
			if not os.path.isdir(testRun) or not os.path.exists(testRunJson):
				# testRunToAnalyze = testRun
				continue

			testRunToAnalyze = testRun

			if not (testRunToAnalyze is None):
				stateMap = {}
				testStats = []
				eventStats = []
				mutationRecords = None

				fullCrawl = crawl
				if FULL_CRAWL is not None:
					fullCrawl = crawl.replace(crawlPath, FULL_CRAWL)

				success = analyzeTestRunFolder(testRunToAnalyze, app, crawlStats,
											   runOfflineOracles=RUN_OFFLINE_ORACLES,
											   crawlPath=fullCrawl, toBeAnalyzed=toBeAnalyzed)

				if success:
					testRows.extend(testStats)

				else:
					print("{0} analysis did not succeed".format(testRunToAnalyze))
					failedAnalyses.append(testRunToAnalyze)

	return testRows


ORACLES = ['hybrid', 'rted', 'hist']


def initStateResult(state):
	global mutationRecords

	Id = state['id']

	initMap = {'id': Id, 'traceId': state['traceState'], 'hybridwarn': 0, 'hybrid_oraclewarn': 0}

	for oracle in ORACLES:
		initMap[oracle] = 0
	# initMap['hybrid'] = 0
	return initMap


def analyzeState(state, oracle):
	global stateMap

	Id = state['id']
	name = state['name']

	origId = name
	if name not in stateMap:
		stateMap[name] = initStateMap(state)

	traceState = state['traceState']
	identical = state['identical']

	# warnLevel = state['warnLevel']
	# compResult = state['compResult']

	traceStateName = "state" + str(traceState)
	stats = {}
	if traceStateName not in stateMap[name]['comps']:
		stats = initStateResult(state)
	else:
		stats = stateMap[name]['comps'][traceStateName]

	if not identical:
		# and compResult=="DIFFERENT":
		stats[oracle] += 1

	# TODO: Use warn level here
	# if warnLevel == "LEVEL2" or warnLevel == "LEVEL3" or warnLevel=="LEVEL1":
	# 	stats[oracle+'warn'] += 1

	stateMap[name]['comps'][traceStateName] = stats


def getTestRunJson(testRun, oracle):
	if oracle == 'hybrid':
		# return os.path.join(testRun, "testRun.json")
		return os.path.join(testRun, "analysis", getOracleFile(oracle))
	else:
		return os.path.join(testRun, "analysis", getOracleFile(oracle))


def analyzeTestRun(testRun, appName, oracle, SAF, version, crawlStats, crawlPath=None, runOfflineOracles=False,
				   threshold=0):
	testRunFile = getTestRunJson(testRun, oracle)
	if oracle == 'hybrid':
		if not os.path.exists(testRunFile):
			print("{0} not found".format(testRunFile))
			if runOfflineOracles:
				createOracleJsons(testRun, appName, runner='runner.OfflineOracleRunner_oldCrawljax', args=[oracle])
			else:
				return None
			# return None
	else:
		if not os.path.exists(testRunFile):
			if runOfflineOracles:
				createOracleJsons(testRun, appName, runner='runner.OfflineOracleRunner_oldCrawljax', args=[oracle])
			else:
				return None

	testRunJson = importJson(testRunFile)

	methods = list(testRunJson.values())
	# methods.sort(key=getMethodNumber)
	coverageStats, crawlCoverageStats = getCoverageStats(appName=appName, crawlPath=crawlPath, methods=methods, threshold=threshold)

	testStatsNow = {}
	if oracle=='hybrid':
		technique = 'FragGen'
	else:
		technique = 'CrawlJax'
	testStatsNow['technique'] = technique
	testStatsNow['appName'] = appName
	testStatsNow['SAF'] = SAF
	testStatsNow['oracle'] = oracle
	testStatsNow['version'] = version
	testStatsNow.update(coverageStats)
	testStatsNow.update(crawlCoverageStats)
	testStatsNow = getTestAndEventStats(methods, appName, crawlStats, testStatsNow, threshold=threshold)

	#
	# eventStats['appName'] = appName
	# eventStats['oracle'] = oracle
	# eventStats['runType'] = runtype

	for method in methods:
		methodResult = method['methodResult']
		for state in methodResult['crawlStates']:
			analyzeState(state, oracle)

	return testStatsNow


def getTestAndEventStats(methods, appName, crawlStats, testStatsNow, threshold=0):
	global testStats

	# totalEvents = 0
	eventSuccess = 0
	eventFailures = 0

	totalMethods = len(methods)
	numSuccess = 0
	numFailures = 0
	numSkips = 0
	duration = 0

	methodFailure_event = 0
	methodSuccess_event = 0

	# totalStateComps = 0
	failedStates = 0
	identicalStates = 0

	distOracleUnknown = 0
	distOracleSuccess = 0
	distOracleFailure = 0

	for method in methods:
		failed = False
		eventFailed = False
		# if method['testStatus'] == "success":
		# 	eventFailed=False
		# 	# numSuccess += 1
		# el
		if method['testStatus'] == "skipped":
			numSkips += 1
		elif method['testStatus'] == "failure":
			failed = True

		duration += method['duration']

		methodResult = method['methodResult']
		for event in methodResult['crawlPath']:
			# totalEvents += 1
			if event['success']:
				eventSuccess += 1
			else:
				failed = True
				eventFailed = True
				eventFailures += 1

		for state in methodResult['crawlStates']:
			if (not state['identical']):
				# and (state['compResult'] == "DIFFERENT"):
				failed = True
				failedStates += 1

			else:
				identicalStates += 1

			if not "distance" in state:
				continue
			distance = state['distance']
			if distance == -1:
				distOracleUnknown += 1
			else:
				if distance <= threshold:
					distOracleSuccess += 1
				else:
					distOracleFailure += 1

		if failed:
			numFailures += 1
		else:
			numSuccess += 1

		if eventFailed:
			methodFailure_event += 1
		else:
			methodSuccess_event += 1

	eventSkips = -1
	oracleSkips = -1
	eventSuccessShare = -1
	oracleSuccessShare = -1
	distOracleSuccessShare = -1
	if "totalEvents" in crawlStats:
		eventSkips = crawlStats["totalEvents"] - (eventSuccess + eventFailures)
		eventSuccessShare = 100 * eventSuccess / crawlStats["totalEvents"]
	if "totalStateComps" in crawlStats:
		oracleSkips = crawlStats["totalStateComps"] - (identicalStates + failedStates)
		oracleSuccessShare = 100 * identicalStates / crawlStats["totalStateComps"]
		distOracleSuccessShare = 100 * distOracleSuccess / crawlStats["totalStateComps"]

	oracleStatsNow = {"oracleSuccess": identicalStates,
					  "oracleFailures": failedStates, "oracleSkips": oracleSkips,
					  "oracleSuccessShare": oracleSuccessShare}
	distOracleStats = {"distOracleSuccess": distOracleSuccess, "distOracleFailure": distOracleFailure,
					   "distanceOracleUnknown": distOracleUnknown, "distOracleSuccessShare": distOracleSuccessShare}

	eventStatsNow = {"eventFailures": eventFailures, "eventSuccess": eventSuccess,
					 "eventSkips": eventSkips,
					 "eventSuccessShare": eventSuccessShare,
					 "eventFailureShare": 100*eventFailures/crawlStats['totalEvents'],
					 "eventSkipShare": 100*eventSkips/crawlStats['totalEvents']}
	testStatsNow.update(
		{"totalMethods": totalMethods,
		 "success_any": numSuccess,
		 "failed_any": numFailures,
		 "numSkips": numSkips,
		 "failed_event": methodFailure_event,
		 "success_event": methodSuccess_event})

	testStatsNow.update(crawlStats)
	testStatsNow.update(eventStatsNow)
	testStatsNow.update(oracleStatsNow)
	testStatsNow.update(distOracleStats)

	testStats.append(testStatsNow)

	return testStatsNow


def analyzeTestSource(crawl):
	testSource = os.path.join(crawl, "src", "test", "java", "generated", "GeneratedTests.java")
	if not os.path.exists(testSource):
		print("Error: Could not find the tests source at {0}".format(testSource))
	try:
		totalEvents = open(testSource).read().count("testSuiteHelper.fireEvent(")
		print(totalEvents)
		totalStateComps = open(testSource).read().count("testSuiteHelper.addStateToReportBuilder(")
		print(totalStateComps)
		return {"totalEvents": totalEvents, "totalStateComps": totalStateComps}
	except Exception as ex:
		print(ex)
		print("Error while getting crawl stats for {0}".format(crawl))
		return {"totalEvents": -1, "totalStateComps": -1}


def analyzeManualTestAnalysis(analysisJson, testStatsNow={}):
	labelledData = importJson(analysisJson)
	clone = 0
	nd2 = 0
	nd3 = 0
	different = 0
	stateNA = 0
	eventAvail = 0
	eventUnavail = 0
	eventNA = 0
	brokenLocator = 0  # clone/nd2 & eventAvail
	invalidAction = 0  # anything else. Also includes dependencies
	unknown = 0
	appChange = 0
	appChangeUnknown = 0

	for item in labelledData:
		stateCat = item["response"]
		eventCat = item["eventResponse"]
		appChangeCat = item["appChangeResponse"]
		if item["response"] == 0:
			stateCat = 0
			clone += 1
		elif item["response"] == 1:
			# if 'dditional' in ''.join(tags):
			# 	stateCat = 3
			# 	nd3 += 1
			# else:
			stateCat = 1
			nd2 += 1
		elif item["response"] == 2:
			stateCat = 2
			different += 1
		elif item["response"] == 3:
			stateCat = 3
			nd3 += 1
		else:
			stateCat = -1
			stateNA += 1

		if eventCat == 1:
			eventAvail += 1
		elif eventCat == 0:
			eventUnavail += 1
		else:
			eventNA += 1

		if appChangeCat == 1:
			appChange += 1
		elif appChangeCat == 0:
			invalidAction += 1
		else:
			appChangeUnknown += 1

		if (stateCat == 0 or stateCat == 1) and eventCat == 1:
			# clone or nd and event available, locator fragility likely
			brokenLocator += 1
	# elif (stateCat >= 2) and eventCat == 1:
	# 	invalidAction += 1
	# elif stateCat >= 2 and eventCat == 0:
	# 	invalidAction += 1
	# else:
	# 	unknown += 1

	testStatsNow.update({"clone": clone,
						 "nd2": nd2,
						 "nd3": nd3,
						 "different": different,
						 "stateNA": stateNA,
						 "eventAvail": eventAvail,
						 "eventUnavail": eventUnavail,
						 "eventNA": eventNA,
						 "brokenLocator": brokenLocator,
						 "invalidAction": invalidAction,
						 "unknown": unknown,
						 "appChange": appChange})
	print(testStatsNow)

	return testStatsNow


def analyzeTestRunFolder(testRun, appName, crawlStats, runOfflineOracles=False,
						 crawlPath=None, toBeAnalyzed=[]):
	global failedAnalyses

	split = os.path.split(os.path.split(os.path.split(os.path.split(os.path.split(testRun)[0])[0])[0])[0])
	# appName = os.path.split(split[0])[1]

	runInfoFile = os.path.join(testRun, "testRunInfo.json")
	runInfo = importJson(runInfoFile)
	crawlInfo = split[1]
	print(crawlInfo)
	print(runInfo)

	# oracle = getOracleName(crawlInfo)

	oracleMapping = getOracleAndThreshold(crawlInfo=crawlInfo, appName=appName)
	oracle = oracleMapping["oracle"]
	threshold = oracleMapping["threshold"]
	testStatsNow = analyzeTestRun(testRun, appName, oracle=oracle,
								  SAF=oracleMapping["SAF"],
								  version=runInfo['version'],
								  crawlStats=crawlStats,
								  crawlPath=crawlPath,
								  runOfflineOracles=runOfflineOracles,
								  threshold=threshold)

	if testStatsNow is None:
		failedAnalyses.append(testRun)
		return

	print("Done processing testRUn file")

	analysisDir = os.path.join(testRun, TEST_ANALYSIS_FOLDER)
	analysisFinalJson = os.path.join(analysisDir, APP_CHANGE_ANALYSIS_JSON)
	analysisJson = os.path.join(analysisDir, TEST_ANALYSIS_JSON)
	if not os.path.exists(analysisFinalJson):
		analysisBackupJson = os.path.join(os.path.abspath("../saveJsons"),
										  getSaveJsonFile_AppChange(crawlPath, runInfo['version'], oracle))
		if os.path.exists(analysisBackupJson):
			if not os.path.exists(analysisDir):
				os.mkdir(analysisDir)
			shutil.copy2(analysisBackupJson, analysisFinalJson)
			shutil.move(analysisBackupJson, analysisBackupJson + "_backup")
		else:
			if GENERATE_CLASSIFICATION_HTML:
				testAnalysisJson = None
				if os.path.exists(analysisJson):
					testAnalysisJson = analysisJson
				generateAppChangeAnalysisHTML(crawlPath, testRun, oracle, app_version=runInfo['version'],
											  testAnalysisJson=None)
				toBeAnalyzed.append(os.path.join(testRun, "html_classification", "testAnalysis.html"))

			else:
				print("manual test analysis json not found!! Run HTML generation")
				print(analysisFinalJson)

	# if not os.path.exists(analysisJson):
	# 	analysisBackupJson = os.path.join(os.path.abspath("../saveJsons"),
	# 									  getSaveJsonFile(crawlPath, runInfo['version'], oracle))
	# 	if os.path.exists(analysisBackupJson):
	# 		if not os.path.exists(analysisDir):
	# 			os.mkdir(analysisDir)
	# 		shutil.copy2(analysisBackupJson, analysisJson)
	# 	else:
	# 		if GENERATE_CLASSIFICATION_HTML:
	# 			print("Generating html for manual analysis")
	# 			generateTestAnalysisHTML(crawlPath, testRun, oracle, app_version=runInfo['version'])
	# 			toBeAnalyzed.append(os.path.join(testRun, "html_classification", "testAnalysis.html"))
	# 		else:
	# 			print("manual test analysis json not found!! Run HTML generation")
	# 			print(analysisJson)

	if os.path.exists(analysisFinalJson):
		# generateAppChangeAnalysisHTML(crawlPath, testRun, oracle, app_version=runInfo['version'], testAnalysisJson=analysisJson)
		testStatsNow = analyzeManualTestAnalysis(analysisFinalJson, testStatsNow)
	else:
		failedAnalyses.append(testRun)


	#coverage stats


	return testStatsNow

def generateRandomFailedOracleHTML(allFailedOracles, outputroot, oracleName, limit=100):
	outputFolder = os.path.join(os.path.abspath(outputroot), oracleName)
	randomFailures = random.choices(allFailedOracles[oracleName], k=limit)
	for failure in randomFailures:
		try:
			screenshotsFolder = os.path.join(os.path.abspath(outputFolder), "screenshots")
			if not os.path.exists(screenshotsFolder):
				os.makedirs(screenshotsFolder)

			dst = os.path.join(screenshotsFolder, failure['copiedLimg'])
			shutil.copy2(failure['origLimgSrc'], dst)

			dst = os.path.join(screenshotsFolder, failure['copiedRimg'])
			shutil.copy2(failure['origRimgSrc'], dst)
		except Exception as ex:
			print(ex)
			print("Error copying image for {0}".format(failure))

	TITLE = "Manual Test Oracle Analysis"
	OUTPUT_HTML_NAME = "testOracleAnalysis.html"
	HTML_OUTPUT_PATH = os.path.join(outputFolder, "html_classification")
	oracleClassification(HTML_OUTPUT_PATH, OUTPUT_HTML_NAME, TITLE, outputJson=randomFailures,
						 saveJsonName=oracleName+"analysisResults.json", overwrite='y')

def getFailedOraclesInFolder(crawlRoot, returnCrawls, app, allFailedOracles):
	for crawl in returnCrawls:
		testRunList = getTestRun(crawl)
		if len(testRunList) == 0:
			print("No Test run found for {0}".format(crawl))
			continue

		fullCrawl = crawl
		if FULL_CRAWL is not None:
			fullCrawl = crawl.replace(crawlRoot, FULL_CRAWL)

		for testRun in testRunList:
			split = os.path.split(os.path.split(os.path.split(os.path.split(os.path.split(testRun)[0])[0])[0])[0])
			crawlInfo = split[1]
			oracleName = getOracleAndThreshold(crawlInfo, app)['oracle']
			failedOracles = getFailedOracles(fullCrawl, testRun, oracleName, app)

			allFailedOracles[oracleName] += failedOracles

def getAllFailedOracles():
	allFailedOracles = {"hybrid":[], "rted":[], "hist":[]}
	for app in APPS:

		crawlPath = "/home/fraggen/fraggen/test-results_rhel"
		returnCrawls1, crawlMap, missingCrawls = getCrawlsToAnalyze(crawlPath=crawlPath,
																   app=app, host="localhost", runtime=60,
																   bestCrawls=True)
		getFailedOraclesInFolder(crawlRoot=crawlPath, returnCrawls=returnCrawls1, app=app, allFailedOracles=allFailedOracles)

		crawlPath = "/home/fraggen/fraggen/test-results_mac"
		returnCrawls2, crawlMap, missingCrawls = getCrawlsToAnalyze(crawlPath=crawlPath,
																   app=app, host="localhost", runtime=60,
																   bestCrawls=True)
		getFailedOraclesInFolder(crawlRoot=crawlPath, returnCrawls=returnCrawls2, app=app, allFailedOracles=allFailedOracles)

	return allFailedOracles

def getFailedOracles(fullCrawl, testRun, oracleName, appName):

	testRunFile = getTestRunJson(testRun, oracleName)
	try:
		testInfo = importJson(os.path.join(testRun, "testRunInfo.json"))
		version = testInfo['version']
		url = testInfo['url']
	except Exception as ex:
		print(ex)
		version = 'unknown'
		url = 'unknown'


	testRunJson = importJson(testRunFile)
	methods = list(testRunJson.values())
	failedOracles = []

	for method in methods:
		methodResult = method['methodResult']
		for oracle in methodResult['crawlStates']:
			if not oracle['identical']:
				origlimgSrc = os.path.join(fullCrawl, "screenshots", oracle['name']+".png")
				origrimgSrc = os.path.join(testRun, "screenshots", "state" + str(oracle["traceState"]) + ".png")

				copiedLimg = appName + "_" + str(version) + "_" + oracleName + "_" + oracle['name'] + ".png"
				copidRimg = appName + "_" + str(version) + "_" + oracleName + "_"+ "state" + str(oracle["traceState"]) + ".png"


				failedOracles.append({"oracle":oracle,
									"response": -1,
									"appChangeResponse": -1,
									"tags": "",
									"origLimgSrc": origlimgSrc,
									 "origRimgSrc": origrimgSrc,
									"copiedLimg": copiedLimg,
									"copiedRimg": copidRimg,
									 "testURL": url})
	return failedOracles

def getFailedEvents(testRunFile):
	testRunJson = importJson(testRunFile)

	methods = list(testRunJson.values())

	failedEvents = []

	for method in methods:
		methodResult = method['methodResult']
		eventNum = 0
		for event in methodResult['crawlPath']:

			# totalEvents += 1
			if not event['success']:
				# print(event)
				stateComp = methodResult['crawlStates'][eventNum]
				# print(stateComp)
				failedEvent = {}
				failedEvent.update(event)
				failedEvent.update({"oracle": stateComp})
				failedEvents.append(failedEvent)

			eventNum += 1

	return failedEvents


def getOracleFile(oracle):
	fileName = ""
	if oracle == 'hyst' or oracle == 'hist':
		fileName = 'histResults'
	elif oracle == 'hybrid':
		fileName = 'hybrid_oracleResults'
	elif oracle == 'rted':
		fileName = 'rtedResults'

	if USE_DISTANCE_ORACLES and (fileName == "histResults" or fileName == "rtedResults"):
		fileName = fileName + "_dist"

	fileName = fileName + ".json"

	return fileName


# USE RTED FOR HIST CRAWLS AS WELL
def getOracleAndThreshold(crawlInfo, appName):
	thresholds, thresholdPerSAF = getBestThresholds(appName)
	oracle = 'hybrid'
	SAF = "HYBRID"
	oracle_SAF = "HYBRID"
	if 'DOM_RTED' in crawlInfo:
		SAF = "DOM_RTED"
		oracle = 'rted'
		oracle_SAF = "DOM_RTED"

	elif 'VISUAL_HYST' in crawlInfo:
		SAF = "VISUAL_HYST"
		oracle = 'hist'
		oracle_SAF = "VISUAL_HYST"
		# oracle_SAF = "DOM_RTED"
		# oracle = 'rted'

	threshold = 0
	try:
		threshold = thresholdPerSAF[oracle_SAF][0]
	except:
		print("warn: Cant find threshold for {0} in {1}".format(SAF, appName))

	return {"oracle": oracle, "SAF": SAF, "threshold": threshold}


def getSaveJsonFile(crawlPath, app_version, oracle):
	return getCrawlFolderName(crawlPath) + "_" + str(app_version) + "_" + oracle + "_" + TEST_ANALYSIS_JSON


def getSaveJsonFile_AppChange(crawlPath, app_version, oracle):
	return getCrawlFolderName(crawlPath) + "_" + str(app_version) + "_" + oracle + "_" + APP_CHANGE_ANALYSIS_JSON


def getInfoFromSaveJsonFile(saveJsonFile):
	print("TODO: To be implemented")


def createSkelXpathJson(crawl):
	BASE_COMMAND = ['java', '-cp', JAR_PATH, "runner.SkeletonXpathGenerator"]

	command = BASE_COMMAND.copy()
	command.append(crawl)

	logFile = os.path.join(crawl, "skeletonXpathLog_" +
						   str(datetime.now().strftime("%Y%m%d-%H%M%S")) + ".log")
	proc = startProcess(command, logFile)
	if proc is None:
		print("Ignoring error command.")
		return
	done = False
	timeDone = 0
	timeStep = 10
	while not done:
		poll = proc.poll()
		if poll is None:
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


def generateAppChangeAnalysisHTML(crawl, testRun, oracle, app_version, testAnalysisJson=None):
	jsonData = None
	if testAnalysisJson is not None:
		jsonData = importJson(testAnalysisJson)
		for failedEvent in jsonData:
			tags = failedEvent["tags"]
			if failedEvent["response"] == 0:
				stateCat = 0
			elif failedEvent["response"] == 1:
				if 'dditional' in ''.join(tags):
					stateCat = 3
				else:
					stateCat = 1
			elif failedEvent["response"] == 2:
				stateCat = 2
			else:
				stateCat = -1

			eventResponse = -1
			if failedEvent['eventResponse'] == 1:
				eventResponse = 0
			elif failedEvent['eventResponse'] == 0:
				eventResponse = 1
			failedEvent.update({"appChangeResponse": -1})
			failedEvent["eventResponse"] = eventResponse
			failedEvent["response"] = stateCat
	else:
		jsonData = generateTestAnalysisJson(crawl, testRun, oracle)

	if len(jsonData) == 0:
		# No classification necessary
		analysisJson = os.path.join(testRun, TEST_ANALYSIS_FOLDER, APP_CHANGE_ANALYSIS_JSON)
		exportJson(jsonData, analysisJson)

	TITLE = "Manual Test Failure Analysis"
	OUTPUT_HTML_NAME = "testAnalysis.html"
	HTML_OUTPUT_PATH = os.path.join(testRun, "html_classification")
	saveJsonName = getSaveJsonFile_AppChange(crawl, app_version, oracle)
	testFailureAnalysis(HTML_OUTPUT_PATH, OUTPUT_HTML_NAME, TITLE, outputJson=jsonData,
						 saveJsonName=saveJsonName, crawlPath=crawl, overwrite='y')


def generateTestAnalysisJson(crawl, testRun, oracle):
	testRunJson = getTestRunJson(testRun, oracle)
	crawlJson = os.path.join(crawl, RESULT_SKEL_JSON)
	if not os.path.exists(crawlJson):
		print("Could not find skeleton xpath json. So creating!!")
		createSkelXpathJson(crawl)
		if not os.path.exists(crawlJson):
			print("Error creating required skeleton json. Continuing with normal")
			crawlJson = os.path.join(crawl, RESULT_JSON)
	crawlJsonData = importJson(crawlJson)
	states = crawlJsonData['states']
	failedEvents = getFailedEvents(testRunJson)
	jsonData = failedEvents
	invalidLocations = []
	for failedEvent in jsonData:
		failedEvent.update({"response": -1, "eventResponse": -1, "appChangeResponse": -1, "tags": ""})
		stateName = failedEvent['oracle']['name']
		identification = 'dummy'

		if 'eventable' not in failedEvent:
			failedEvent['eventable'] = {'element': {'dummy': 'dummy'}}

		try:
			identification = failedEvent['eventable']['identification']['value']
		except:
			print(failedEvent)
		# identification = failedEvent['eventable']['identification']['value']
		state = states[stateName]
		foundLocation = False
		dummyCandidate = {"left": 0, "top": 0, "height": 0, "width": 0}
		for candidate in state['candidateElements']:
			if candidate['xpath'] == identification:
				failedEvent['eventable']['element'].update({"location": candidate})
				print(failedEvent['eventable']['element'])
				foundLocation = True
				break

		if not foundLocation:
			failedEvent['eventable']['element'].update({"location": dummyCandidate})
			invalidLocations.append(failedEvent)

	return jsonData


# print(invalidLocations)
# print(jsonData)
# TITLE = "Manual Test Failure Analysis"
# OUTPUT_HTML_NAME = "testAnalysis.html"
# HTML_OUTPUT_PATH = os.path.join(testRun, "html_classification")
# saveJsonName = getSaveJsonFile(crawl, app_version, oracle)
# oracleClassification(HTML_OUTPUT_PATH, OUTPUT_HTML_NAME, TITLE, outputJson=jsonData,
# 					 saveJsonName=saveJsonName, crawlPath=crawl, overwrite='y')


def distOracleStats(distResultsJson, threshold):
	jsonData = importJson(distResultsJson)
	methods = list(jsonData.values())
	success = 0
	failed = 0
	fallBack = 0

	for method in methods:
		methodResult = method['methodResult']
		for state in methodResult['crawlStates']:
			if not "distance" in state:
				continue
			distance = state['distance']
			if distance == -1:
				fallBack += 1
				if state['identical']:
					success += 1
				else:
					failed += 1
			else:
				if distance <= threshold:
					success += 1
				else:
					failed += 1
	distStats = {"distOracleSuccess": success, "distOracleFailure": failed, "distanceOracleFallBack": fallBack}
	print(distStats)

	return distStats


################################## TESTS #########################

def testSourceAnalysis():
	crawlStats = analyzeTestSource(
		"/home/fraggen/fraggen/test-results_rhel/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0")
	print(crawlStats)


def testGetFailedEvents():
	crawlJson = "/home/fraggen/fraggen/test-results_rhel/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0/result.json"
	crawlJsonData = importJson(crawlJson)
	states = crawlJsonData['states']
	failedEvents = getFailedEvents(
		"/home/fraggen/fraggen/test-results_rhel/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0/test-results/0/analysis/rtedResults.json")


def testAnalyzeManualAnalysis():
	testAnalysis = analyzeManualTestAnalysis(
		"/home/fraggen/fraggen/test-results_rhel/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0/test-results/0/analysis/" + TEST_ANALYSIS_JSON)


def testAnalyzeTestRun():
	# testRunToAnalyze = "/home/fraggen/fraggen/test-results_rhel/pagekit/pagekit_DOM_RTED_0.0_60mins/192.168.99.101/crawl0/test-results/1/"
	# fullCrawl = "/home/fraggen/fraggen/paper-crawls/out/pagekit/pagekit_DOM_RTED_0.0_60mins/192.168.99.101/crawl0/"
	testRunToAnalyze = "/home/fraggen/fraggen/test-results_rhel/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0/test-results/0/"
	fullCrawl = "/home/fraggen/fraggen/paper-crawls/out/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0/"

	app = 'pagekit'
	crawlStats = analyzeTestSource(fullCrawl)
	verifClassificationJson = os.path.join(fullCrawl, 'comp_output', VERIFIED_CLASSIFICATION_JSON_NAME)
	crawlStatesJson = importJson(verifClassificationJson)['states']
	analyzeTestRunFolder(testRunToAnalyze, app, crawlStats, crawlStatesJson=crawlStatesJson,
						 runOfflineOracles=RUN_OFFLINE_ORACLES,
						 crawlPath=fullCrawl, toBeAnalyzed=[])


def testOracleDistComp():
	thresholds, thresholdPerSAF = getBestThresholds("addressbook")

	print(thresholds)
	print(thresholdPerSAF)
	threshold = thresholdPerSAF['VISUAL_HYST'][0]
	print(threshold)
	testAnalysis = distOracleStats(
		"/home/fraggen/fraggen/test-results_mac/addressbook/addressbook_VISUAL_HYST_433.0669_60mins/localhost/crawl0/test-results/0/analysis/histResults_dist.json",
		threshold)

def getCoverageStats(appName, crawlPath, methods, threshold):
	verifClassificationJson = os.path.join(crawlPath, 'comp_output', VERIFIED_CLASSIFICATION_JSON_NAME)
	crawlStatesJson = importJson(verifClassificationJson)['states']

	if crawlStatesJson is not None:
		coverageStats = getBinCoverage(statesJson=crawlStatesJson, methods=methods, threshold=threshold)
	else:
		coverageStats = {"coveredBins": -1, "failedBins": -1, "skippedBins": -1}


	gsCrawl = os.path.join(os.path.abspath(GS_CRAWLS), appName, 'crawl-' + appName + '-60min')
	gsJson = os.path.join(gsCrawl, 'gs', GS_JSON_NAME)
	if not os.path.exists(gsJson):
		print("GS JSON not found at : {0}".format(gsJson))
		crawlCoverageStats = {"crawlCoverage": -1, "testCoverage":-1}
	elif coverageStats['skippedBins'] != -1:
		gsJsonData = importJson(gsJson)
		gsStatesJson = gsJsonData['states']
		crawlCoverage = getCrawlCoverage(gsStatesJson, crawlStatesJson)
		if crawlCoverage > 0:
			testCoverage = (100 - coverageStats['skippedBins'])*crawlCoverage
		else:
			testCoverage = -1
		crawlCoverageStats = {"crawlCoverage": 100*crawlCoverage, "testCoverage":testCoverage}

	return coverageStats, crawlCoverageStats

def getCrawlCoverage(gsStatesJson, statesJson):
	totalBins = getNumBins(gsStatesJson)
	foundBins = getNumBins(statesJson)
	coverage = foundBins/totalBins
	return coverage

def getBinCoverage(statesJson, methods, threshold=0):
	allBins = getAllBins(statesJson)
	coveredBins = []
	seenBins = []

	for method in methods:
		stateIndex = 0
		methodResult = method['methodResult']
		for state in methodResult['crawlStates']:
			eventSuccess = True
			try:
				eventSuccess = methodResult['crawlPath'][stateIndex]['success']
			except:
				eventSuccess = False

			stateIndex += 1

			stateName = state['name']
			if stateName not in statesJson:
				continue

			bin = statesJson[stateName]['bin']

			if bin not in seenBins:
				seenBins.append(bin)

			if bin in coveredBins:
				continue

			distance = -1
			if "distance" in state and state['distance'] != -1:
				distance = state['distance']
				if distance <= threshold:
					coveredBins.append(bin)

			elif state['identical']:
				coveredBins.append(bin)

			elif eventSuccess:
				coveredBins.append(bin)

	failedBins = [x for x in seenBins if x not in coveredBins]
	skippedBins = [x for x in allBins if x not in seenBins]

	print("Failed Bins : {0}", failedBins)
	print("Skipped Bins : {0}", skippedBins)
	coverageStats = {"coveredBins": 100 * len(coveredBins) / len(allBins),
					 "failedBins": 100 * len(failedBins) / len(allBins),
					 "skippedBins": 100 * len(skippedBins) / len(allBins)}
	return coverageStats


def testgetTestCoverage():
	testRunToAnalyze = "/home/fraggen/fraggen/test-results_rhel/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0/test-results/0/"
	crawl = "/home/fraggen/fraggen/paper-crawls/out/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0/"
	app = 'addressbook'
	oracle = "rted"
	verifClassificationJson = os.path.join(crawl, 'comp_output', VERIFIED_CLASSIFICATION_JSON_NAME)
	distResultsJson = os.path.join(testRunToAnalyze, TEST_ANALYSIS_FOLDER, getOracleFile(oracle))
	jsonData = importJson(distResultsJson)
	methods = list(jsonData.values())
	thresholds, thresholdPerSAF = getBestThresholds("addressbook")

	threshold = thresholdPerSAF['DOM_RTED'][0]

	coverage = getBinCoverage(importJson(verifClassificationJson)['states'], methods, threshold)
	print("Coverage is {0}".format(coverage))


def testGetFailedOracles():
	testRunToAnalyze = "/home/fraggen/fraggen/test-results_rhel/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0/test-results/0/"
	crawl = "/home/fraggen/fraggen/paper-crawls/out/addressbook/addressbook_DOM_RTED_0.0_60mins/localhost/crawl0/"
	app = 'addressbook'
	oracle = "rted"
	print(getFailedOracles(crawl, testRunToAnalyze, oracle, app))

def generateOracleAnalysis():
	allFailed = getAllFailedOracles()
	rootFolder = "../oracle_analysis/"
	for oracle in ORACLES:
		outputPath = os.path.join(os.path.abspath(rootFolder), oracle)
		if os.path.exists(outputPath):
			print("{0} analysis html already exists {1}".format(oracle, outputPath))
			continue
		generateRandomFailedOracleHTML(allFailed, rootFolder, oracle, limit=100)


def testAnalyzeManualTestOracles():
	root = "../oracle_analysis"
	#/oracleAnalysis1/rtedAnalysisResults.json"
	for oracle in ORACLES:
		jsonFile = os.path.join(os.path.abspath(root), oracle, oracle+"analysisResults.json")
		jsonData = importJson(jsonFile)
		falsePositives = 0
		appChanges = 0
		unknown = 0
		fragile = 0
		invalid = 0

		for item in jsonData:



			if item['appChangeResponse'] == 0:
				falsePositives += 1
				if item['response'] == 0 or item['response'] == 1:
					fragile += 1
				elif item['response'] == 2 or item['response'] == 3:
					invalid += 1
			elif item['appChangeResponse'] == 1:
				appChanges += 1
			else:
				unknown += 1

		# print(jsonData)
		print(oracle + "," + (str(falsePositives) + "," + str(appChanges)+ "," + str(fragile)+ "," + str(invalid)))


FULL_CRAWL = "/home/fraggen/fraggen/paper-crawls/"
GS_CRAWLS = '/home/fraggen/fraggen/GroundTruth'
RUN_OFFLINE_ORACLES = True
OPEN_MANUAL_ANALYSIS = False
GENERATE_CLASSIFICATION_HTML = True
USE_DISTANCE_ORACLES = True

def analyzePaperTestRuns():

	totalTestRows = []
	totalStateRows = []
	# APPS=['ppma']
	toBeAnalyzed = []
	for app in APPS:
		testRows = analyzeTestRuns("/home/fraggen/fraggen/test-results_rhel", app=app, toBeAnalyzed=toBeAnalyzed)
		totalTestRows.extend(testRows)
		testRows2 = analyzeTestRuns("/home/fraggen/fraggen/test-results_mac", app=app,
									toBeAnalyzed=toBeAnalyzed)
		totalTestRows.extend(testRows2)

	# totalStateRows.extend(stateMap)

	print(totalTestRows)
	# print(totalStateRows)
	print("Result Json not found for : ")
	print(failedAnalyses)

	print("Manual Analysis to be done for :")
	print(toBeAnalyzed)
	REGRESSION_TESTRUN_CSV_FIELDS = totalTestRows[0].keys()
	# TESTORACLE_CSV_FIELDS = totalStateRows[0].keys()

	writeCSV(csvFields=REGRESSION_TESTRUN_CSV_FIELDS, csvRows=totalTestRows,
			 dst=os.path.join("..", RESULTS_FOLDER, "testRunStats.csv"))

def analyzeNewTestRuns():
	global FULL_CRAWL
	FULL_CRAWL = None
	totalTestRows = []
	totalStateRows = []
	# APPS = ['addressbook']
	toBeAnalyzed = []
	runtime = 60
	for app in APPS:
		testRows = analyzeTestRuns("/home/fraggen/fraggen/out", runtime = runtime, app=app, toBeAnalyzed=toBeAnalyzed)
		totalTestRows.extend(testRows)

	# totalStateRows.extend(stateMap)

	print(totalTestRows)
	# print(totalStateRows)
	print("Result Json not found for : ")
	print(failedAnalyses)

	print("Manual Analysis to be done for :")
	print(toBeAnalyzed)
	REGRESSION_TESTRUN_CSV_FIELDS = totalTestRows[0].keys()
	# TESTORACLE_CSV_FIELDS = totalStateRows[0].keys()

	writeCSV(csvFields=REGRESSION_TESTRUN_CSV_FIELDS, csvRows=totalTestRows,
			 dst=os.path.join("..", RESULTS_FOLDER, "testRunStats.csv"))


if __name__ == "__main__":
	
	analyzePaperTestRuns()
	analyzeNewTestRuns()
	totalTestRows = []
	toBeAnalyzed = []
	app = 'addressbook'
	runtime = 60
	
	testRows = analyzeTestRuns("/home/fraggen/fraggen/test-results_rhel", 
	                           runtime=runtime, 
	                           app=app, 
	                           toBeAnalyzed=toBeAnalyzed)
	totalTestRows.extend(testRows)
	
	print(totalTestRows)
	print("Failed Analyses: ", failedAnalyses)
	print("To Be Analyzed: ", toBeAnalyzed)
	
	if len(totalTestRows) > 0:
		REGRESSION_TESTRUN_CSV_FIELDS = totalTestRows[0].keys()
		writeCSV(csvFields=REGRESSION_TESTRUN_CSV_FIELDS, 
		         csvRows=totalTestRows,
		         dst=os.path.join("..", RESULTS_FOLDER, "testRunStats_addressbook.csv"))

