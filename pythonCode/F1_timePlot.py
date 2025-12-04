import numpy as np

from globalNames import GS_JSON_NAME, RESULT_JSON, CONFIG_JSON, getResultsFolder, COMP_OUTPUT, STATES, UNALTERED_GS_TAG, VERIFIED_CLASSIFICATION_JSON_NAME, GENERATED_CLASSIFICATION_JSON_NAME, getPreDefinedSaveJsonLocation, buildCrawlFolderName, APPS, ALGOS, isDockerized, isNd3App, getHostName
import matplotlib.pyplot as plt
from matplotlib import colors, lines, markers
from analyzeCrawl import getMaxState, getBinRepresentatives, STATUS_JSON_NOT_FOUND, STATUS_CREATED_CLASSIFICATION_HTML, analyze, getNumBins, getCrawlsToAnalyze
import os
from utils import importJson, exportJson
from runCrawljaxBatch import getBestThresholds

STATUS_DONE = "DONE"


def getF1( jsonData, gsJsonData):
	states = jsonData['states']
	gsStates = gsJsonData['states']
	binRepresentatives = getBinRepresentatives(states)

	idArray = []
	for stateName in states:
		state = states[stateName]
		Id = state['id']
		idArray.append(Id)
	
	print(idArray)
	idArray.sort()
	print(idArray)

	binArray = []
	for binRep in binRepresentatives:
		Id = binRepresentatives[binRep]	
		binArray.append(Id)

	print(binArray)

	gsBins = getNumBins(gsStates)
	covered = 0
	numSeen = 0
	recall = -1
	precision = -1
	

	prArray = []
	reArray = []
	f1Array = []

	f1 = -1
	for Id in idArray:
		numSeen +=1

		if Id in binArray:
			covered += 1

		recall = covered/gsBins
		precision = covered/numSeen
		f1 = 2* (recall*precision)/(recall + precision)
		reArray.append(recall)
		prArray.append(precision)
		f1Array.append(f1)

	
	return {"pr":prArray, "re": reArray, "f1": f1Array}
	
	


def getF1Series(crawl, gsCrawl):
	status = None
	verifClassificationJson = os.path.join(crawl, 'comp_output', VERIFIED_CLASSIFICATION_JSON_NAME)
	
	
	if (not os.path.exists(verifClassificationJson)):
		print("Classification JSON not found at : {0}".format(verifClassificationJson))
		print("Calling analysis on the crawl to create classification json")
		status, analysisData = analyze(gsCrawl, crawl, appName, thresholdEntry=None, preDefinedSaveJsonLocation = getPreDefinedSaveJsonLocation())
		if status== STATUS_CREATED_CLASSIFICATION_HTML:
			print("Please verify the classification html and run again")
			print(os.path.abspath(crawl, "html_classification", "classification.html"))
		return status, analysisData

	jsonData = importJson(verifClassificationJson)

	gsJson = os.path.join(gsCrawl, 'gs', GS_JSON_NAME)
	if not os.path.exists(gsJson):
		print("GS JSON not found at : {0}".format(gsJson))
		status = STATUS_JSON_NOT_FOUND
		return status, None

	gsJsonData = importJson(gsJson)
	# resultJson = os.path.join(crawl, RESULT_JSON)
	# if not os.path.exists(resultJson):
	# 	print("Result JSON not found at : {0}".format(resultJson))
	# 	status = STATUS_JSON_NOT_FOUND
	# 	return status,None

	# configJson = os.path.join(crawl, CONFIG_JSON)
	# if not os.path.exists(configJson):
	# 	print("Config JSON not found at : {0}".format(configJson))
	# 	status = STATUS_JSON_NOT_FOUND
	# 	return status,None

	# resultJsonData = importJson(resultJson)
	# configJsonData = importJson(configJson)

	f1Series = getF1(jsonData, gsJsonData)
	

	status = STATUS_DONE
	return status, f1Series


def getF1SeriesForApp(appName, allCrawls = "../out/", gsCrawls = "../GroundTruth", runtime = 5):
	# bestAlgos = ['DOM_RTED', 'VISUAL_HYST', 'VISUAL_BLOCKHASH', 'VISUAL_PDIFF', 'DOM_LEVENSHTEIN', 'VISUAL_SSIM', 'HYBRID']
	bestAlgos = ['DOM_RTED', 'HYBRID', 'VISUAL_HYST']

	gsCrawl = os.path.join(os.path.abspath(gsCrawls), appName, 'crawl-'+appName+'-60min')
	hostName = "localhost"
	if isDockerized(appName):
		hostName = "192.168.99.101"


	crawlsToAnalyze, crawlMap, missingCrawls = getCrawlsToAnalyze(allCrawls, appName, host=hostName, runtime= 60)
	
	returnSeries = []
	failed = []
	succeeded = []

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
				failed.append(os.path.join(os.path.abspath(allCrawls), appName, folderName))
				continue

			crawl = os.path.join(os.path.abspath(allCrawls), appName, folderName, hostName, 'crawl0')
			if crawl not in crawlsToAnalyze:
				print(crawl)
				print("not found in tobe analyzed crawls")
			# print(crawl)
			if crawl in missingCrawls:
				failed.append(crawl)
				continue

			# crawl = os.path.join(crawl, 'crawl0')
			print(crawl)
			status, series = getF1Series(crawl, gsCrawl)
			if status == STATUS_DONE:
				succeeded.append(crawl)
				seriesObject = {"appName": appName, "algo": algoStr, "threshold": crawlMap[crawl], "pr": series['pr'], "re": series['re'], "f1": series['f1']}
				returnSeries. append(seriesObject)
			else:
				failed.append(crawl)

	return {"failed": failed, "succeeded": succeeded, "series": returnSeries}

def getF1SeriesForAllApps():
	returnSeries = []
	failed = []
	succeeded = []
	for app in APPS:
		returnObject = getF1SeriesForApp(app, runtime = 60)
		print("failed to get f1 for {0}".format(returnObject["failed"]))
		print("succeeded for {0}".format(returnObject["succeeded"]))
		returnSeries.extend(returnObject["series"])
		failed.extend(returnObject["failed"])
		succeeded.extend(returnObject["succeeded"])


	print(returnSeries)
	print("succeeded {0}".format(succeeded))
	print("failed {0}".format(failed))

	print("succeeded {0} and failed {1}".format(str(len(succeeded)), str(len(failed))))
	exportJson(returnSeries, os.path.join(getResultsFolder(), "f1_series.json"))
	return {"failed": failed, "succeeded": succeeded, "series": returnSeries}


def testGetF1Series():
	GS_CRAWL = '~/git/abstract-state-function-project/src/main/resources/GoldStandards/ppma/crawl-ppma-60min/'


	crawl = "~/VisCrawler/testBatch/ppma/crawl0/"
	status, data = getF1Series(crawl, GS_CRAWL)

	print(status)
	print(data)



if __name__=="__main__":

	# testGetF1Series()
	returnObject = getF1SeriesForAllApps()

	seriesList = returnObject['series']

	colors_array = list(colors.cnames.keys())
	lines_array = list(lines.lineStyles.keys())
	# markers_array = list(markers.MarkerStyle.markers.keys())
	# print(markers_array)
	# ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_', 'P', 'X', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 'None', None, ' ', '']

	markers_array = [ 'o', 'v', 's', '*', 'H', 'd', 'P', '.', "|"]
	legend = []
	fig, axes = plt.subplots(1, 3)

	i= 0
	for algo in ALGOS:
		algoStr = str(algo).split('.')[1].upper()

		bestAlgos = ['HYBRID', 'DOM_RTED', 'VISUAL_HYST']

		if algoStr not in bestAlgos:
			continue


		axes[i].set_ylabel('F\u2081')
		axes[i].set_xlabel('States')
		# axes[1].set_title('Nd3-Apps')
		# axes[1].set_ylabel('norm F\u2081')
		# axes[1].set_xlabel('% States')

		legend1 = []
		legend2 = []
		# plt.suptitle('F1 vs States ' );
		index = 0
		for series in seriesList:

			algostr = series['algo'] 
			if(algostr != algoStr):
				continue

			ax = None
			appName = series['appName']
			
			print(appName + " " + markers_array[index])

			# if isNd3App(appName):
			# 	ax = axes[1]
			# 	legend1.append(appName)
			# else:
			ax = axes[i]
			legend2.append(appName)

			
			f1_raw = series['f1']
			f1_array = []
			xArray = []
			count = 0
			for f1 in f1_raw:
				# xArray.append(100*count/len(f1_raw))
				# f1_array.append(f1/max(f1_raw))
				xArray.append(count)
				f1_array.append(f1)
				count +=1
			ax.plot(xArray, f1_array, marker= markers_array[index])
			# legend.append(appName +"_"+algoStr)
			index += 1
		axes[i].set_yticks(np.arange(0, 1, 0.1))
		axes[i].set_ylim(0,1)
		i+=1
		# plt.legend(legend, loc='upper left')
		# axes[1].legend(legend1, loc= 'lower right')

	axes[0].set_title('Structural')
	axes[1].set_title('Visual')
	axes[2].set_title('FragGen')

	axes[1].legend(legend2, loc= 'upper right')
	axes[0].legend(legend2, loc='upper right')
	axes[2].legend(legend2, loc='lower right')

	plt.show()










