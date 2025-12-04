from _threading_local import local

from analyzeCrawl import getCrawlsToAnalyze, writeCSV
import os
from importResponses import importJson
from globalNames import RESULTS_FOLDER, APPS
from runCrawljaxBatch import startProcess
from time import sleep
from datetime import datetime

JAR_PATH = os.path.join(os.path.abspath("../jars"), "comparator-0.0.1-SNAPSHOT-jar-with-dependencies.jar")


def createOracleJsons(crawl, appName, runner='runner.OfflineOracleRunner', args=[]):
	BASE_COMMAND = ['java', '-cp', JAR_PATH, runner]

	command = BASE_COMMAND.copy()
	command.append(crawl)
	command.append(appName)

	if len(args) >0:
		for arg in args:
			command.append(arg)

	logFile = os.path.join(crawl, "classificationLog_" +
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


def buildTestRunStats(numTests, numFailures, numSkips, numEventFailures, numStateFailures):
	return {"numTests": numTests, "numFailures": numFailures, "numSkips": numSkips,
			"numEventFailures": numEventFailures, "numStateFailures": numStateFailures}


def getTestRun(crawl):
	returnList = []
	testResultsFolder = os.path.join(crawl, "test-results")
	if os.path.exists(testResultsFolder):
		testRunList = os.listdir(testResultsFolder)
		print("Found test runs {0}".format(testRunList))
		for testRun in testRunList:
			if testRun == '.DS_Store':
				continue
			returnList.append(os.path.join(testResultsFolder, testRun))
		return returnList
	return []


def getMethodNumber(method):
	return method['methodNumber']


def collectMutantStats(state, mutationStats):
	pass


def getMethodStats(method, mutationStats):
	methodResult = method['methodResult']
	# print(methodResult)
	totalStates = 0
	differentStates = 0
	identicalStates = 0
	nd1 = 0
	nd2 = 0
	warningLevel1 = 0
	warningLevel2 = 0
	warningLevel3 = 0
	noWarning = 0
	locatorWarning = 0

	totalEvents = 0
	eventFailures = 0
	eventSuccess = 0

	for state in methodResult['crawlStates']:
		try:
			state['compResult']
		except:
			state['compResult'] = "DUMMY"

		totalStates += 1
		if (not state['identical']) and (state['compResult'] == "DIFFERENT"):
			differentStates += 1
		elif state['compResult'] == "NEARDUPLICATE2":
			nd2 += 1
		elif state['compResult'] == "NEARDUPLICATE1":
			nd1 += 1
		else:
			identicalStates += 1

		if state['warnLevel'] == "LEVEL1":
			warningLevel1 += 1
		elif state['warnLevel'] == "LEVEL2":
			warningLevel2 += 1
		elif state['warnLevel'] == "LEVEL3":
			warningLevel3 += 1
		elif state['identical']:
			noWarning += 1

		if state['locatorWarning']:
			locatorWarning += 1

		mutationStats = collectMutantStats(state, mutationStats)

	for event in methodResult['crawlPath']:
		totalEvents += 1
		if event['success']:
			eventSuccess += 1
		else:
			eventFailures += 1

	return {"totalStates": totalStates,
			"differentStates": differentStates,
			"identicalStates": identicalStates,
			"nd1": nd1,
			"nd2": nd2,
			"warningLevel1": warningLevel1,
			"warningLevel2": warningLevel2,
			"warningLevel3": warningLevel3,
			"noWarning": noWarning,
			"locatorWarning": locatorWarning,
			"totalEvents": totalEvents,
			"eventFailures": eventFailures,
			"eventSuccess": eventSuccess,
			"mutationStats": mutationStats}


def analyzeTestRunFolder(testRun, appName, runOfflineOracles=False):
	returnArray = []

	testRunFile = os.path.join(testRun, "testRun.json")
	normalAnalysis = analyzeTestRun(testRunFile)
	normalAnalysis['runType'] = "NORMAL"
	normalAnalysis['oracle'] = "HYBRID"
	returnArray.append(normalAnalysis)

	# if not os.path.exists(os.path.join(testRun, "testRun_mut_fixed.json")):
	#
	if runOfflineOracles:
		createOracleJsons(testRun, appName)

	mutationRecordsFile = os.path.join(testRun, "mutant", "mutationRecords.json")
	mutationRecords = None
	if os.path.exists(mutationRecordsFile):
		mutationRecords = importJson(mutationRecordsFile)
	else:
		print("No Mutation Record Found at {0}".format(mutationRecordsFile))

	testRunFile_mut = os.path.join(testRun, "testRun_mut_fixed.json")
	mutationAnalysis = analyzeTestRun(testRunFile_mut, mutationRecords)
	mutationAnalysis['runType'] = "MUTATION"
	mutationAnalysis['oracle'] = "HYBRID"
	returnArray.append(mutationAnalysis)

	testRunFile = os.path.join(testRun, "stringResults.json")
	normalAnalysis = analyzeTestRun(testRunFile)
	normalAnalysis['runType'] = "NORMAL"
	normalAnalysis['oracle'] = "STRING"
	returnArray.append(normalAnalysis)

	testRunFile_mut = os.path.join(testRun, "stringResults_mut.json")
	mutationAnalysis = analyzeTestRun(testRunFile_mut, mutationRecords)
	mutationAnalysis['runType'] = "MUTATION"
	mutationAnalysis['oracle'] = "STRING"
	returnArray.append(mutationAnalysis)

	testRunFile = os.path.join(testRun, "rtedResults.json")
	normalAnalysis = analyzeTestRun(testRunFile)
	normalAnalysis['runType'] = "NORMAL"
	normalAnalysis['oracle'] = "RTED"
	returnArray.append(normalAnalysis)

	testRunFile_mut = os.path.join(testRun, "rtedResults_mut.json")
	mutationAnalysis = analyzeTestRun(testRunFile_mut, mutationRecords)
	mutationAnalysis['runType'] = "MUTATION"
	mutationAnalysis['oracle'] = "RTED"
	returnArray.append(mutationAnalysis)

	testRunFile = os.path.join(testRun, "histResults.json")
	normalAnalysis = analyzeTestRun(testRunFile)
	normalAnalysis['runType'] = "NORMAL"
	normalAnalysis['oracle'] = "Histogram"
	returnArray.append(normalAnalysis)

	testRunFile_mut = os.path.join(testRun, "histResults_mut.json")
	mutationAnalysis = analyzeTestRun(testRunFile_mut, mutationRecords)
	mutationAnalysis['runType'] = "MUTATION"
	mutationAnalysis['oracle'] = "Histogram"
	returnArray.append(mutationAnalysis)

	return returnArray


def analyzeTestRun(testRunFile, mutationRecords=None):
	if not os.path.exists(testRunFile):
		return {}

	testRunJson = importJson(testRunFile)

	methods = list(testRunJson.values())
	methods.sort(key=getMethodNumber)

	mutatedStates = 0
	failedMutatedStates = 0
	tag = 0
	tagFail = 0
	Attr = 0
	AttrFail = 0
	SubTree = 0
	SubTreeFail = 0
	text = 0
	textFail = 0
	table = 0
	tableFail = 0
	div = 0
	divFail = 0
	mutationStats = {'mutants': mutatedStates,
					 'failedMutants': failedMutatedStates,
					 'tag': tag,
					 'tagFail': tagFail,
					 'attr': Attr,
					 'attrfail': AttrFail,
					 'subtree': SubTree,
					 'subtreeFail': SubTreeFail,
					 'text': text,
					 'textFail': textFail,
					 'table': table,
					 'tableFail': tableFail,
					 'div': div,
					 'divFail': divFail}

	numTests = 0
	numFailures = 0
	numSkips = 0
	numSuccess = 0
	duration = 0
	methodNoWarning = 0
	methodWarnLevel1 = 0
	methodWarnLevel2 = 0
	methodWarnLevel3 = 0

	totalStates = 0
	differentStates = 0
	identicalStates = 0
	nd1 = 0
	nd2 = 0
	warningLevel1 = 0
	warningLevel2 = 0
	warningLevel3 = 0
	noWarning = 0
	locatorWarning = 0

	totalEvents = 0
	eventFailures = 0
	eventSuccess = 0

	for method in methods:
		print(method)
		print("***************************")
		methodStats = getMethodStats(method, mutationStats)

		numTests += 1

		if method['testStatus'] == "success":
			numSuccess += 1
		elif method['testStatus'] == "skipped":
			numSkips += 1
		elif method['testStatus'] == "failure":
			numFailures += 1

		duration += method['duration']

		try:
			method['methodResult']['warnLevel']
		except:
			method['methodResult']['warnLevel'] = "DUMMY"

		if method['methodResult']['warnLevel'] == "LEVEL1":
			methodWarnLevel1 += 1
		elif method['methodResult']['warnLevel'] == "LEVEL2":
			methodWarnLevel2 += 1
		elif method['methodResult']['warnLevel'] == "LEVEL3":
			methodWarnLevel3 += 1
		else:
			methodNoWarning += 1

		totalStates += methodStats["totalStates"]
		differentStates += methodStats["differentStates"]
		identicalStates += methodStats["identicalStates"]
		nd1 += methodStats["nd1"]
		nd2 += methodStats["nd2"]
		warningLevel1 += methodStats["warningLevel1"]
		warningLevel2 += methodStats["warningLevel2"]
		warningLevel3 += methodStats["warningLevel3"]
		noWarning += methodStats["noWarning"]
		locatorWarning += methodStats["locatorWarning"]
		totalEvents += methodStats['totalEvents']
		eventFailures += methodStats["eventFailures"]
		eventSuccess += methodStats["eventSuccess"]

	return {"numTests": numTests,
			"numSuccess": numSuccess,
			"numSkips": numSkips,
			"numFailures": numFailures,
			"duration": duration,
			"methodWarnLevel1": methodWarnLevel1,
			"methodWarnLevel2": methodWarnLevel2,
			"methodWarnLevel3": methodWarnLevel3,
			"methodNoWarning": methodNoWarning,
			"totalStates": totalStates,
			"differentStates": differentStates,
			"identicalStates": identicalStates,
			"nd1": nd1,
			"nd2": nd2,
			"warningLevel1": warningLevel1,
			"warningLevel2": warningLevel2,
			"warningLevel3": warningLevel3,
			"noWarning": noWarning,
			"locatorWarning": locatorWarning,
			"totalEvents": totalEvents,
			"eventFailures": eventFailures,
			"eventSuccess": eventSuccess,
			"mutationStats": mutationStats}


def analyzeTestRuns(crawlPath="out", runtime=60, app=None, bestCrawls=True):
	returnCrawls, crawlMap, missingCrawls = getCrawlsToAnalyze(crawlPath=crawlPath,
															   app=app, host="localhost", runtime=runtime,
															   bestCrawls=bestCrawls)
	returnMap = []
	for crawl in returnCrawls:
		testRunList = getTestRun(crawl)
		if len(testRunList) == 0:
			print("No Test run found for {0}".format(crawl))
			continue

		testRunToAnalyze = None
		for testRun in testRunList:
			testRunJson = os.path.join(testRun, "testRun.json")
			if os.path.isdir(testRun) and os.path.exists(testRunJson):
				testRunToAnalyze = testRun
				break

		if not (testRunToAnalyze is None):
			analyses = analyzeTestRunFolder(testRunToAnalyze, app, runOfflineOracles=True)
			for analysis in analyses:
				analysis['app'] = app
				returnMap.append(analysis)

	return returnMap


def testAnalyzeRun():
	analysis = analyzeTestRunFolder(
		"out/petclinic/petclinic_HYBRID_0.0_60mins/localhost/crawl2/test-results/0")
	print(analysis)


TESTRUN_CSV_FIELDS = [
	"app",
	"runType",
	"oracle",
	"numTests",
	"numSuccess",
	"numSkips",
	"numFailures",
	"duration",
	"methodWarnLevel1",
	"methodWarnLevel2",
	"methodWarnLevel3",
	"methodNoWarning",
	"totalStates",
	"differentStates",
	"identicalStates",
	"nd1",
	"nd2",
	"warningLevel1",
	"warningLevel2",
	"warningLevel3",
	"noWarning",
	"locatorWarning",
	"totalEvents",
	"eventFailures",
	"eventSuccess",
	"mutationStats"]


def testAnalyzeTestRunFolder():
	returnRows = analyzeTestRunFolder(
		'out/petclinic/petclinic_HYBRID_0.0_60mins/localhost/crawl2/test-results/10',
		'petclinic', runOfflineOracles=True)
	print(returnRows)


if __name__ == "__main__":
	totalRows = []
	for app in APPS:
		rows = analyzeTestRuns("/home/fraggen/fraggen/out", app=app)
		totalRows.extend(rows)

	writeCSV(csvFields=TESTRUN_CSV_FIELDS, csvRows=totalRows,
			 dst=os.path.join("..", RESULTS_FOLDER, "testRunStats.csv"))
