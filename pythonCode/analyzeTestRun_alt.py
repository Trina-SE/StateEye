import os

from analyzeCrawl import writeCSV, getCrawlsToAnalyze
from analyzeTestRun import TESTRUN_CSV_FIELDS, createOracleJsons, getTestRun, getMethodNumber
from globalNames import RESULTS_FOLDER, APPS, ORACLES, MUTATORS
from importResponses import importJson

stateMap = {}
eventStats = []
testStats = []
mutationRecords = None

MUTATION_SEED = 10000000


def getMutationNode(xpath):
	if xpath == None:
		return None

	finalNode = xpath.split('/')[len(xpath.split('/'))-1]
	finalNode = finalNode.split('[')[0]
	return finalNode


def initStateMap(state):
	global mutationRecords

	Id = state['id']
	origId = state['name']
	mutation = False
	mutationType = None
	mutationNode = None

	if Id >= MUTATION_SEED:
		mutation = True
		if Id == MUTATION_SEED:
			origId = "index"
		else:
			origId = "state" + str(Id - MUTATION_SEED)

	initMap = {'id': Id, 'mutation': mutation}

	if mutation and origId in mutationRecords :
		mutationRecord = mutationRecords[origId][0]
		if 'operator' in mutationRecord:
			mutationType = mutationRecord['operator']
			mutationNode = getMutationNode(mutationRecord['originalXpath'])
			if mutationType == 'TextNodeMutator' and mutationNode == 'P':
				mutationType = 'SubtreeMutator'

	initMap['mutationType'] = mutationType
	initMap['mutationNode'] = mutationNode

	initMap['comps'] = {}

	return initMap

def initStateResult(state):
	global mutationRecords

	Id = state['id']

	initMap = {'id': Id, 'traceId': state['traceState'], 'hybridwarn':0,'hybridwarn1':0,'hybridwarn2':0,'hybridwarn3':0,
			   'hybrid_oraclewarn':0, 'hybrid_oraclewarn1':0, 'hybrid_oraclewarn2':0, 'hybrid_oraclewarn3':0}


	for oracle in ORACLES:
		initMap[oracle.value] = 0

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

	warnLevel = state['warnLevel']
	compResult = state['compResult']

	traceStateName = "state" + str(traceState)
	stats = {}
	if traceStateName not in stateMap[name]['comps']:
		stats = initStateResult(state)
	else:
		stats = stateMap[name]['comps'][traceStateName]

	if not identical and compResult=="DIFFERENT":
		stats[oracle] += 1

	#TODO: Use warn level here
	if warnLevel == "LEVEL2":
		stats[oracle + 'warn2'] += 1
		stats[oracle + 'warn'] += 1
	elif warnLevel == "LEVEL3":
		stats[oracle + 'warn3'] += 1
		stats[oracle + 'warn'] += 1
	elif warnLevel=="LEVEL1":
		stats[oracle+'warn1'] += 1
		stats[oracle + 'warn'] += 1

	stateMap[name]['comps'][traceStateName] = stats


def analyzeTestRun(testRunFile, appName, oracle, runtype):
	testRunJson = importJson(testRunFile)

	methods = list(testRunJson.values())
	methods.sort(key=getMethodNumber)

	testStats = getTestAndEventStats(methods, appName)
	#
	# eventStats['appName'] = appName
	# eventStats['oracle'] = oracle
	# eventStats['runType'] = runtype

	testStats['appName'] = appName
	testStats['oracle'] = oracle
	testStats['runType'] = runtype

	for method in methods:
		methodResult = method['methodResult']
		for state in methodResult['crawlStates']:
			analyzeState(state, oracle)


def getTestAndEventStats(methods, appName):
	global eventStats
	global testStats

	totalEvents = 0
	eventSuccess = 0
	eventFailures = 0

	totalMethods = len(methods)
	numSuccess = 0
	numFailures = 0
	numSkips = 0
	duration = 0

	for method in methods:
		failed = False
		if method['testStatus'] == "success":
			numSuccess += 1
		elif method['testStatus'] == "skipped":
			numSkips += 1
		elif method['testStatus'] == "failure":
			failed = True

		duration += method['duration']

		methodResult = method['methodResult']
		for event in methodResult['crawlPath']:
			totalEvents += 1
			if event['success']:
				eventSuccess += 1
			else:
				failed = True
				eventFailures += 1

		for state in methodResult['crawlStates']:
			if (not state['identical']) and (state['compResult'] == "DIFFERENT"):
				failed = True

			#TODO: Find the warn level and declare failed if it meets criteria to fail as oracle
			# elif state['compResult'] == "NEARDUPLICATE2":
			# 	nd2 += 1
			# elif state['compResult'] == "NEARDUPLICATE1":
			# 	nd1 += 1
			# else:
			# 	identicalStates += 1

		if failed:
			numFailures += 1


	eventStatsNow = {"totalEvents": totalEvents, "eventFailures": eventFailures, "eventSuccess": eventSuccess}
	testStatsNow = {"totalMethods": totalMethods, "numSuccess": numSuccess, "numFailures": numFailures, "numSkips": numSkips}

	testStatsNow.update(eventStatsNow)
	testStats.append(testStatsNow)

	return testStatsNow


def analyzeTestRunFolder(testRun, appName, runOfflineOracles = False):
	global mutationRecords
	# returnArray = []
	testRunFile = os.path.join(testRun, "testRun.json")
	# analyzeTestRun(testRunFile, appName, 'hybrid', 'normal')

	# if runOfflineOracles:
	# 	createOracleJsons(testRun, appName)
	analysisFolder = os.path.join(testRun, "analysis")

	mutationRecordsFile = os.path.join(analysisFolder, "mutationRecordsExt.json")
	mutationRecords = None
	if not os.path.exists(mutationRecordsFile) and runOfflineOracles:
		print("Creating the new mutation records for visibility analysis")
		createOracleJsons(testRun, appName)

	if os.path.exists(mutationRecordsFile):
		mutationRecords = importJson(mutationRecordsFile)
	else:
		print("No Mutation Record Found at {0}".format(mutationRecordsFile))


	# if mutationRecords !=None:
	# 	testRunFile_mut = os.path.join(analysisFolder, "testRun_mut_fixed.json")
	# 	if not os.path.exists(testRunFile_mut):
	# 		testRunFile_mut = os.path.join(testRun, "testRun_mut.json")
	# 	analyzeTestRun(testRunFile_mut, appName, 'hybrid', 'mutation')

	# returnArray.append(mutationAnalysis)

	mutString = "_mut"
	resultsFile = "Results"
	extension = ".json"


	for oracle in ORACLES:
		testRunFile = os.path.join(analysisFolder, oracle.value + resultsFile + extension)
		#not os.path.exists(testRunFile) and


		analyzeTestRun(testRunFile, appName, oracle.value, 'normal')

		if mutationRecords == None:
			print("No mutation records.. so ignoring mutation stats")
			continue


		testRunFile_mut = os.path.join(analysisFolder, oracle.value + resultsFile + mutString + extension)
		if not os.path.exists(testRunFile) and runOfflineOracles:
			print("testRunFile does not exist {0}".format(testRunFile_mut))

		analyzeTestRun(testRunFile_mut, appName, oracle.value, 'mutation')


	return stateMap


def initStateRow(origState, appName):
	global mutationRecords

	if origState['id'] >= MUTATION_SEED:
		initMap = {'mutationType':origState['mutationType'],
				'mutationNode':origState['mutationNode'],
				   'mut_hybridwarn': 0,
				   'mut_hybridwarn1': 0,
				   'mut_hybridwarn2': 0,
				   'mut_hybridwarn3': 0,
				   'mut_hybrid_oraclewarn':0,
				   'mut_hybrid_oraclewarn1': 0,
				   'mut_hybrid_oraclewarn2': 0,
				   'mut_hybrid_oraclewarn3': 0
				}

		for oracle in ORACLES:
			initMap['mut_'+ oracle.value] = 0

	else:
		initMap = {'app': appName,
				'id': origState['id'],
				'mutationType':None,
				'mutationNode':None,
				'numComps':len(origState['comps']),
				'hybridwarn':0,
				   'hybridwarn1': 0,
				   'hybridwarn2': 0,
				   'hybridwarn3': 0,
				'hybrid_oraclewarn':0,
				   'hybrid_oraclewarn1': 0,
				   'hybrid_oraclewarn2': 0,
				   'hybrid_oraclewarn3': 0,
				'mut_hybridwarn': 0,
				   'mut_hybridwarn1': 0,
				   'mut_hybridwarn2': 0,
				   'mut_hybridwarn3': 0,
				'mut_hybrid_oraclewarn':0,
				   'mut_hybrid_oraclewarn1': 0,
				   'mut_hybrid_oraclewarn2': 0,
				   'mut_hybrid_oraclewarn3': 0
				}

		stateStr= 'index' if origState['id'] == 0 else 'state'+ str(origState['id'])

		if stateStr in mutationRecords:
			initMap['visible'] = mutationRecords[stateStr][0]['visible']
		else:
			initMap['visible'] = None

		for oracle in ORACLES:
			initMap[oracle.value] = 0
			initMap['mut_'+ oracle.value] = 0


	return initMap


def analyzeOracles(states, appName):
	perStateRows = {}

	for origStateName in states.keys():
		origState = states[origStateName]
		stateRow = initStateRow(origState, appName)
		print(origStateName)
		comps = origState['comps']
		mutStr = "mut_" if origState['id']>=MUTATION_SEED else ""
		for compState in comps.keys():
			stateRow[mutStr + 'hybridwarn'] += comps[compState]['hybridwarn']
			stateRow[mutStr + 'hybrid_oraclewarn'] += comps[compState]['hybrid_oraclewarn']
			stateRow[mutStr + 'hybridwarn1'] += comps[compState]['hybridwarn1']
			stateRow[mutStr + 'hybrid_oraclewarn1'] += comps[compState]['hybrid_oraclewarn1']
			stateRow[mutStr + 'hybridwarn2'] += comps[compState]['hybridwarn2']
			stateRow[mutStr + 'hybrid_oraclewarn2'] += comps[compState]['hybrid_oraclewarn2']
			stateRow[mutStr + 'hybridwarn3'] += comps[compState]['hybridwarn3']
			stateRow[mutStr + 'hybrid_oraclewarn3'] += comps[compState]['hybrid_oraclewarn3']

			for oracle in ORACLES:
				stateRow[mutStr + oracle.value] += comps[compState][oracle.value]
		if origState['id'] < MUTATION_SEED:
			perStateRows[origState['id']] = stateRow
		else:
			stateRowOrig = perStateRows[origState['id']-MUTATION_SEED]
			stateRowOrig.update(stateRow)

	return perStateRows.values()



def analyzeTestRuns(crawlPath="/home/fraggen/fraggen/paper-crawls", runtime=60, app=None, bestCrawls=True):
	returnCrawls, crawlMap, missingCrawls = getCrawlsToAnalyze(crawlPath=crawlPath,
															   app=app, host="localhost", runtime=runtime,
															   bestCrawls=bestCrawls)
	global stateMap
	global eventStats
	global testStats
	global mutationRecords

	testRows = []
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
			stateMap = {}
			testStats = []
			eventStats = []
			mutationRecords = None
			states = analyzeTestRunFolder(testRunToAnalyze, app, runOfflineOracles=True)

			testRows.extend(testStats)

			oracleAnalysis = analyzeOracles(states, app)
			returnMap.extend(oracleAnalysis)
			# for analysis in analyses:
			# 	analysis['app'] = app
			# 	returnMap.append(analysis)

	return testRows, returnMap


def initOracleRow(param):
	initMap = {'oracle': param}
	for mutator in MUTATORS:
		mutatorKey = mutator.value
		initMap[mutatorKey] = 0
		initMap[mutatorKey+'warn'] = 0
	initMap['warn'] = 0
	return initMap


def getPerOracleRows(perStateRows):
	oracleMap = {}

	oracleMap['total'] = initOracleRow('total')
	for oracle in ORACLES:
		oracleMap[oracle.value] = initOracleRow(oracle.value)

	for row in perStateRows:
		if row['mutationType'] == None:
			continue
		oracleMap['total'][row['mutationType']] += row['numComps']
		for oracle in ORACLES:
			if oracle == ORACLES.FragGen:
				oracleMap[oracle.value][row['mutationType']+'warn'] += row['mut_' + oracle.value + 'warn']
				oracleMap[oracle.value]['warn'] += row['mut_' + oracle.value + 'warn']

			oracleMap[oracle.value][row['mutationType']] += row['mut_' + oracle.value]

	print(oracleMap)
	return list(oracleMap.values())


def initMutationRow(param):
	initMap = {'mutation': param, 'total':0}
	for oracle in ORACLES:
		oracleKey = oracle.value
		initMap[oracleKey] = 0
	return initMap

def getPerMutationRows_tolerance(perStateRows):
	mutationMap = {}

	mutationMap['warn'] = initMutationRow('warn')
	for mutation in MUTATORS:
		mutationMap[mutation.value] = initMutationRow(mutation.value)
		mutationMap[mutation.value + 'warn'] = initMutationRow(mutation.value + 'warn')

	mutationMap['None'] = initMutationRow('None')
	mutationMap['None' + 'warn'] = initMutationRow('None' + 'warn')
	for row in perStateRows:
		mutationType = 'None' if row['mutationType'] == None else row['mutationType']

		mutationMap[mutationType]['total'] += row['numComps']
		for oracle in ORACLES:
			mutationMap['None'][oracle.value] += row[oracle.value]
			if oracle == ORACLES.FragGen:
				mutationMap['None' + 'warn'][oracle.value] += row[oracle.value + 'warn']
				mutationMap['warn'][oracle.value] += row[oracle.value + 'warn']

		if mutationType != 'None' and (not row['visible'] or mutationType == MUTATORS.ATTRIBUTE.value):

			for oracle in ORACLES:
				if oracle == ORACLES.FragGen:
					mutationMap[mutationType + 'warn'][oracle.value] += row['mut_' + oracle.value + 'warn']
					mutationMap['warn'][oracle.value] += row['mut_' + oracle.value + 'warn']

				mutationMap[mutationType][oracle.value] += row['mut_' + oracle.value]

	print(mutationMap)
	return list(mutationMap.values())

def getPerMutationRows(perStateRows):
	mutationMap = {}

	mutationMap['warn'] = initMutationRow('warn')
	for mutation in MUTATORS:
		mutationMap[mutation.value] = initMutationRow(mutation.value)
		mutationMap[mutation.value + 'warn'] = initMutationRow(mutation.value + 'warn')

	for row in perStateRows:
		if row['mutationType'] == None or not row['visible'] or row['mutationType'] == MUTATORS.ATTRIBUTE.value:
			continue
		mutationMap[row['mutationType']]['total'] += row['numComps']
		for oracle in ORACLES:
			if oracle == ORACLES.FragGen:
				mutationMap[row['mutationType']+'warn'][oracle.value] += row['mut_' + oracle.value + 'warn']
				mutationMap['warn'][oracle.value] += row['mut_' + oracle.value + 'warn']

			mutationMap[row['mutationType']][oracle.value] += row['mut_' + oracle.value]

	print(mutationMap)
	return list(mutationMap.values())

def testAnalyzeTestRunFolder():
	global stateMap
	global testStats
	testFolder = ''
	returnRows= analyzeTestRunFolder(testFolder,
									 'dimeshift', runOfflineOracles=True)
	print(testStats)
	print(stateMap)
	perStateRows = analyzeOracles(stateMap, 'dimeshift')
	print(perStateRows)

	perOracleRows = getPerOracleRows(perStateRows)
	print(perOracleRows)

def testAnalyzeTestRun():
	global mutationRecords
	global stateMap
	testRun = ''
	mutationRecordsFile = os.path.join(testRun, "mutant", "mutationRecords.json")
	mutationRecords = None
	if os.path.exists(mutationRecordsFile):
		mutationRecords = importJson(mutationRecordsFile)
	else:
		print("No Mutation Record Found at {0}".format(mutationRecordsFile))

	analyzeTestRun(testRun + '/analysis/rtedResults_mut.json', 'petclinic', 'rted', 'mutation')
	print(stateMap)

	analyzeTestRun(testRun + '/analysis/stringResults_mut.json', 'petclinic', 'string', 'mutation')
	print(stateMap)




if __name__ == "__main__":
	# testAnalyzeTestRunFolder()
	# testAnalyzeTestRun()
	# print(returnCrawls)
	#
	# print("Missing")
	# print(missingCrawls)
	#

	ALL_CRAWLS = "/home/fraggen/fraggen/out"

	# CRAWLS = "/home/fraggen/fraggen/paper-crawls"

	runtime  = 60

	totalTestRows = []
	totalStateRows = []
	for app in APPS:
		testRows, stateMap = analyzeTestRuns(ALL_CRAWLS, runtime=runtime, app=app)
		totalTestRows.extend(testRows)
		totalStateRows.extend(stateMap)


	print(totalTestRows)
	print(totalStateRows)

	# totalOracleRows = getPerOracleRows(totalStateRows)
	#
	# testMutationRows = getPerMutationRows(totalStateRows)
	#
	# testToleranceRows = getPerMutationRows_tolerance(totalStateRows)


	TESTRUN_CSV_FIELDS = totalTestRows[0].keys()
	TESTORACLE_CSV_FIELDS = totalStateRows[0].keys()
	# PERORACLE_CSV_FIELDS = totalOracleRows[0].keys()

	writeCSV(csvFields= TESTRUN_CSV_FIELDS, csvRows=totalTestRows, dst = os.path.join("..", RESULTS_FOLDER, "mutationStats.csv"))
	writeCSV(csvFields= TESTORACLE_CSV_FIELDS, csvRows=totalStateRows, dst = os.path.join("..", RESULTS_FOLDER, "mutationOracleStats.csv"))
	# writeCSV(csvFields=PERORACLE_CSV_FIELDS, csvRows=totalOracleRows, dst= os.path.join("..", RESULTS_FOLDER, "AggrOracleRows.csv"))
