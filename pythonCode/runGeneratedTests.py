import os
from datetime import datetime

from analyzeCrawl import getCrawlsToAnalyze
from analyzeTestRun import getTestRun
from globalNames import isDockerized, getVersionURL, getDockerName
from runCrawljaxBatch import startProcess, monitorProcess, cleanup, STATUS_SUCCESSFUL, STATUS_ERRORED, \
	restartDockerVersion
from utils import exportJson

BASE_COMMAND_HYBRID = ['sh', 'runTests_hybrid.sh']
BASE_COMMAND_HYBRID_MUTATE = ['sh', 'runTests_hybrid_mutate.sh']

BASE_COMMAND = ['sh', 'runTests.sh']


def executeTests(appName, algo, crawl, url=None,
				 logFile=os.path.join("logs", "testRunLog_" + str(datetime.now().strftime("%Y%m%d-%H%M%S")) + ".log"),
				 testResultsFolder=None):
	command = BASE_COMMAND.copy()

	


	if algo == 'HYBRID':
		if MUTATION:
			print("Choosing Mutation executable {0}".format(BASE_COMMAND_HYBRID_MUTATE))
			command = BASE_COMMAND_HYBRID_MUTATE.copy()
		else:
			print("Choosing Hybrid executable {0}".format(BASE_COMMAND_HYBRID))
			command = BASE_COMMAND_HYBRID.copy()

	else:
		if MUTATION:
			print("Cannot mutate old crawljax tests. Skipping")
			return STATUS_ERRORED, command
		print("Using Old executable {0}".format(BASE_COMMAND))
		command = BASE_COMMAND.copy()

	command.append(crawl)

	if url is not None:
		command.append(url)

	if DRY_RUN:
		status = STATUS_SUCCESSFUL
		return status, command

	if isDockerized(appName):
		restartDockerVersion(appName, version=APP_VERSION)

	proc = startProcess(command, logFile, changeDir=False, DEBUG=False)
	if proc == None:
		print("Ignoring error command.")
		status = STATUS_ERRORED
		return status, command

	timeout = 200
	if (algo == 'VISUAL_PDIFF'):
		timeout = 300

	status = monitorProcess(proc, 30, timeStep=60)
	print("Done : {0}".format(command))

	try:
		status = saveTestRunInfo(crawl=crawl, url=url,
								 dockerName=getDockerName(appName, APP_VERSION),
								 testResultsFolder=testResultsFolder,
								 version=APP_VERSION)
	except Exception as ex:
		print(ex)
		print("Exception saving test run info")
		status = False

	if isDockerized(appName):
		cleanup(appName, version=APP_VERSION)
	else:
		cleanup()
	return status, command


def saveTestRunInfo(crawl,url, dockerName=None, testResultsFolder=None, version=None):
	if version is None:
		version=APP_VERSION

	testRunInfo = {'version': version, 'url': url, 'docker':dockerName}
	testRunInfoFile = os.path.join(testResultsFolder, 'testRunInfo.json')

	if testResultsFolder == None:
		testResultsFolder = os.path.join(crawl, 'test-results', '0')
		print("Assuming test results folder {0}".format(testResultsFolder))

	if not os.path.exists(testResultsFolder):
		print("Test results folder not found {0}".format(testResultsFolder))
		print("Error: Test Run not successful!!")
		return False

	if os.path.exists(testRunInfoFile):
		print("Error: Test run file already exists at {0}".format(testRunInfo))
		return False
	else:
		print(testRunInfo)
		if not DRY_RUN:
			exportJson(testRunInfo, testRunInfoFile)
		return True


def runTests(crawl, rerun=False):
	split = os.path.split(os.path.split(os.path.split(crawl)[0])[0])
	appName = os.path.split(split[0])[1]
	runInfo = split[1]
	print(appName)
	print(runInfo)
	testRuns = getTestRun(crawl)
	if len(testRuns) > 1:
		if not rerun:
			return False
	else:
		appUrl = getVersionURL(appName, APP_VERSION)
		print("changing URL to {0}".format(appUrl))
		algo = "other"
		if "HYBRID" in runInfo:
			algo = "HYBRID"

		status, command = executeTests(
			appName, algo, crawl,
			url=appUrl,
			logFile=os.path.join(crawl, "testRun_" + str(datetime.now().strftime("%Y%m%d-%H%M%S")) + ".log"),
			testResultsFolder=os.path.join(crawl,'test-results', str(len(testRuns))))
		print(command)
		print(status)
		return True


def runAllTests(crawls, rerun=False):
	success = []
	skipped = []
	for crawl in crawls:
		status = runTests(crawl, rerun)
		if status:
			success.append(crawl)
		else:
			skipped.append(crawl)

	print("succeeded {0}: {1}".format(len(success), success))
	print("skipped {0}: {1}".format(len(skipped), skipped))
	return success, skipped


def addTestRunInfos(crawls, app_version=None):
	for crawl in crawls:
		split = os.path.split(os.path.split(os.path.split(crawl)[0])[0])
		appName = os.path.split(split[0])[1]
		testRuns = getTestRun(crawl)
		for testRun in testRuns:
			print(testRun)
			version = app_version
			if app_version ==None:
				version = int(os.path.split(testRun)[1])
			url = getVersionURL(appName, version)
			saveTestRunInfo(crawl, url,
							dockerName=getDockerName(appName, version),
							testResultsFolder=testRun,
							version=version)




MUTATION = False
DRY_RUN = False
APP_VERSION = 0 #0,1 are possible options
if __name__ == "__main__":
	# testCleanup()
	# testGetThresholds()
	# testRestartDocker()
	# testChangeDir()
	# testGetBestThresholds()
	ALL_CRAWLS = "../out"
	# ALL_CRAWLS = "../paper-crawls"
	runtime = 60

	returnCrawls, crawlMap, missingCrawls = getCrawlsToAnalyze(crawlPath=ALL_CRAWLS, app="addressbook", host="localhost",
															   runtime=runtime, bestCrawls=True)
	print(returnCrawls)

	print(crawlMap)

	print("Missing")
	print(missingCrawls)

	runAllTests(returnCrawls, rerun=False)
