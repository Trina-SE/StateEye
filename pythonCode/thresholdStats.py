from globalNames import THRESHOLD_SETS, DB_SETS, APPS
from runCrawljaxBatch import getAllThresholds, getThreshold, normalize
from pythonDBCreator import ALGOS
from analyzeCrawl import writeCSV
from threshold_data import STATISTICS
from datetime import datetime

fieldNames= ['algorithm' , 'thresholdName', 'threshold']

def getRowsForApp(algoMax, app = None):
	rows = []
	allThresholds, thresholdsPerSAF = getAllThresholds()
	if app!=None:
		allThresholds, thresholdsPerSAF = getAllThresholds(app)

	print(allThresholds)
	for thresholdSetName in allThresholds:
		thresholdSet = allThresholds[thresholdSetName]
		thresholdName = '_'.join(thresholdSetName)
		index = 0
		thresholdName = '_'.join(thresholdSetName)
		# fieldNames.append(thresholdName)
		for algo in ALGOS:
			algoStr = str(algo).split('.')[1].upper()
			op = algo.value[2]
			threshold = thresholdSet[algoStr]
			print(threshold)
			if algoMax[algoStr] > 1:
				threshold = threshold/algoMax[algoStr]
			if op=='gt':
				threshold = 1.0-threshold
			rows.append({"algorithm":algoStr, 'thresholdName': thresholdName, 'threshold':threshold})
	return rows

rows = []
algoMax = {}
maxData = STATISTICS["gt10_db_data"]["all_all"]
maxData = normalize(maxData)
for algo in ALGOS:
	algoStr = str(algo).split('.')[1].upper()
	algoData = maxData[algoStr]
	algoMaximum = algoData[4]
	algoMax[algoStr] = algoMaximum


rows.extend(getRowsForApp(algoMax))

for app in APPS:
	rows.extend(getRowsForApp(algoMax, app))

# allThresholds, thresholdsPerSAF = getAllThresholds()
# for thresholdSetName in allThresholds:
# 	thresholdName = '_'.join(thresholdSetName)
# 	fieldNames.append(thresholdName)

uniqueRows = []
for row in rows:
	if row not in uniqueRows:
		uniqueRows.append(row)

writeCSV(fieldNames, uniqueRows, "thresholds" +str(datetime.now().strftime("%Y%m%d-%H%M%S"))+ ".csv")
	