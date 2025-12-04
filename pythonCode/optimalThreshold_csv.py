import os
from sklearn import metrics

from analyzeCrawl import writeCSV
from globalNames import ALGOS
from importResponses import importJson
from optimalThreshold import getMax
from pythonDBCreator import getAllPairsFromCSV
from hyperopt import hp, tpe, fmin, Trials, STATUS_OK

allEntries = None
algoStr = None
distances = None
y_actual = []


# def objective(x):
#     return {
#         'loss': x ** 2,
#         'status': STATUS_OK,
#         # -- store other results like this
#         'eval_time': time.time(),
#         'other_stuff': {'type': None, 'value': [0, 1, 2]},
#         # -- attachments are handled differently
#         'attachments':
#             {'time_module': pickle.dumps(time.time)}
#         }

def getLoss_SAF(space):
	t = space['t']
	return getF1_SAF_new(t)

def getF1_SAF_new(t):
	global algoStr
	global distances
	global y_actual
	algo = None
	for Algo in ALGOS:
		if algoStr == str(Algo).split('.')[1].upper():
			algo = Algo

	if Algo == None:
		print("No Algo found for the string specified. Quitting!!")
		exit(-1)
	y_pred = []

	for value in distances:
		pred = 0
		if algo.value[2] == "lt":
			if value <= t:
				pred = 0
			else:
				pred = 1
		else:
			if value >= t:
				pred = 0
			else:
				pred = 1

		y_pred.append(pred)

	cm = metrics.confusion_matrix(y_actual, y_pred)
	# print(cm)
	precision, recall, f1, support = metrics.precision_recall_fscore_support(y_actual, y_pred, average=None)

	# print("{0} : {1} : {2} : {3}".format(precision, recall, f1, support))
	return {'loss': 1-f1[1], 'status': STATUS_OK, 'data_pr': precision[1], 'data_re': recall[1]}

def get_y_actual_SAF(allEntries, jsonData, nd3=False):
	global distances
	global y_actual
	y_actual = []
	distances = []
	maxVal = 0
	nd3Change = 0
	if allEntries == None:
		print("No entries initialized yet. Quitting!")
		exit(0)

	pairMap = {}
	for pair in jsonData['pairs']:
		key = pair['state1']+'_'+pair['state2']
		response = pair['response']
		tags = "_".join(pair['tags'])
		# print(tags)
		if response == 1 and nd3 and 'dditional' in tags :
			nd3Change += 1
			response = 2
		pairMap[key] = response
		key =  pair['state2']+'_'+pair['state1']
		pairMap[key] = response

	print("Changed {0} ND3 pairs".format(nd3Change))
	for entry in allEntries:
		distance = float(entry['distance'])
		if(distance>maxVal):
			maxVal = distance
		distances.append(float(entry['distance']))
		key = entry['state1']+"_" + entry['state2']
		classif = None
		try:
			classif = pairMap[key]
		except:
			classif = 2

		if classif == 0 or classif ==1:
			y_actual.append(0)
		else:
			y_actual.append(1)
	return y_actual, distances, maxVal

def getOptimalThresholds_SAF(csv, jsonData, algoStr2, appName, optimalThresholds, nd3):
	global allEntries
	global algoStr
	algoStr = algoStr2
	print(appName)
	allEntries = getAllPairsFromCSV(csv)
	print(len(allEntries))
	pairs = jsonData['pairs']
	print(len(pairs))
	print(allEntries[0])
	print(algoStr)
	y_actual, distances, maxVal = get_y_actual_SAF(allEntries, jsonData, nd3=nd3)
	space = {
		't': hp.uniform('t', 0, maxVal),
	}
	trials = Trials()

	try:
		best = fmin(fn = getLoss_SAF,
				space = space, algo=tpe.suggest,
				max_evals = 5000, trials=trials)


		row = {'thresholdSet' : "optimal", 'appName':appName, 'algoName':algoStr,'thre':best['t']}
		optimalThresholds.append(row)
		print(best)
		# print(trials.trials)

	except Exception as ex:
		print(ex)
		print("Error getting optimal threshold for {0}".format(algoStr))

	fieldNames = ['thresholdSet', 'appName', 'algoName', 'thre']
	# writeCSV(fieldNames, optimalThresholds, "optimalThresholds_SAF.csv")
	return optimalThresholds

if __name__ == "__main__":
	appName = 'ppma'
	algo = ALGOS.DOM_RTED
	algoStr = str(algo).split('.')[1].upper()
	algoVal = algo.value[0]
	optimalThresholds = []
	crawl = '../GroundTruth/{0}/crawl-{0}-60min/'.format(appName)

	csv = os.path.join(crawl, 'comp_output', appName + '-' + algoVal + '-raw.csv')
	jsonFile = os.path.join(crawl, 'gs', 'gsResults.json')
	if not os.path.exists(jsonFile):
		print("json doesn't exist at {0}".format(jsonFile))
		exit(-1)
	if not os.path.exists(csv):
		print("csv doesn't exist at {0}".format(csv))
		exit(-1)
	jsonData = importJson(jsonFile)
	optimalThresholds = getOptimalThresholds_SAF(
		csv,
		jsonData,
		algoStr,
		appName,
		optimalThresholds,
		nd3=True
	)