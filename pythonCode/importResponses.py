import json
from pythonDBCreator import connectToDB, closeDBConnection,  fetchRandomNearDuplicates, updateNearDuplicate
from globalNames import SCREENSHOTS

def importJson(jsonFile):
	try:
		with open(jsonFile, encoding='utf-8') as data_file:
			data = json.loads(data_file.read())
			return data
	except Exception as ex:
		print("Exception occured while importing json from : " + jsonFile)
		print(ex)
		return None

def mergeData(data1, data2):
	merged = data1
	concur =0
	conflict =0
	clones = 0
	nds = 0
	diffs = 0
	conflict_CND = 0
	conflict_CD = 0
	conflict_NDD = 0
	noResponse = 0
	for i in range(0,len(data1)):
		elem = data1[i]
		toMerge = data2[i]
		# print(elem)
		# print(toMerge)
		a = []
		a.extend(elem['tags'])
		a.extend(toMerge['tags'])
		merged[i]['tags'] = a
		merged[i]['tags'] = list(dict.fromkeys(merged[i]['tags']))

		if elem['response']==-1 or toMerge['response']==-1:
			noResponse+=1
			merged[i]['response']=-1
			continue
		if elem['response'] == toMerge['response']:
			concur+=1
			if elem['response'] == '0':
				clones+=1
			if elem['response'] == '1':
				nds+=1
			if elem['response'] == '2':
				diffs+=1
			merged[i]['response'] = elem['response']
			
		else:
			conflict+=1
			if (elem['response'] == '0' and toMerge['response']=='1') or (elem['response'] == '1' and toMerge['response']=='0'):
				conflict_CND+=1
				merged[i]['response'] = 1
			if  (elem['response'] == '0' and toMerge['response']=='2') or (elem['response'] == '2' and toMerge['response']=='0'):
				conflict_CD+=1
				merged[i]['response'] = 2
			if (elem['response'] == '1' and toMerge['response']=='2') or (elem['response'] == '2' and toMerge['response']=='1'):
				conflict_NDD+=1
				merged[i]['response'] = 2
	print("merged")
	return merged, {'concur': concur,'conflict':conflict, 'clones':clones, 'nds':nds, 'diffs':diffs, 'conflict_CND':conflict_CND, 'conflict_CD':conflict_CD, 'conflict_NDD':conflict_NDD, 'noResponse':noResponse} 

def updateTags(responseData):
	updated = 0
	for i in range(0, len(responseData)):
		try:
			response = responseData[i]
			appName = response['appname']
			crawl = response['crawl']
			state1 = response['state1']
			state2 = response['state2']
			algo = 'TAGS'
			value = response['response']
			value = ''' '{0}' '''.format(' ,'.join(response['tags']))
			if updateNearDuplicate(appName, crawl, state1, state2, algo, value, insertIfNotPresent=False):
				updated+=1
			else:
				print("Error updating Record with Response : {0}".format(response))
		except Exception as e:
			print(e)
			print("Exception while updating Record with Response : ")
	return updated

def updateDB(responseData):
	updated = 0
	#randomNDs = fetchRandomNearDuplicates(NUMBER*2)
	#print(responseData)
	for i in range(0, len(responseData)):
		try:
			response = responseData[i]
			appName = response['appname']
			crawl = response['crawl']
			state1 = response['state1']
			state2 = response['state2']
			algo = 'HUMAN_CLASSIFICATION'
			value = response['response']
			if updateNearDuplicate(appName, crawl, state1, state2, algo, value, insertIfNotPresent=False):
				updated+=1
			else:
				print("Error updating Record with Response : {0}".format(response))
		except Exception as e:
			print(e)
			print("Exception while updating Record with Response : ")
	return updated

def testImportJson():
	jsonFile = '/responseResults_htmloutput1.json'
	data = importJson(jsonFile)
	print(data[0])

def testMergeData():
	jsonFile1 = '/responseResults__htmloutput1.json'
	jsonFile2 = '/_htmloutput1.json'
	data1 = importJson(jsonFile1)
	data2 = importJson(jsonFile2)
	combinedData = mergeData(data1, data2)
	print(combinedData)

def testUpdateDB():
	jsonFile1 = '/responseResults__htmloutput1.json'
	jsonFile2 = 'responseResults__htmloutput1.json'
	data1 = importJson(jsonFile1)
	data2 = importJson(jsonFile2)
	combinedData, stats = mergeData(data1, data2)
	print(stats)
	testdb = 'gt10.db'
	updated = 0
	try:
		connectToDB(testdb)
		updated = updateDB(combinedData)
	except Exception as e:
		print(e)
		print("Encountered exception while updating records")
	finally:
		closeDBConnection()

	print("Updated {0} db records".format(updated))

def testUpdateSingleResponseResults():
	jsonFile = "responseResults_500_20190402-022537.json"
	data = importJson(jsonFile)
	testdb = '/gt10_last500Responses.db'
	updated = 0
	try:
		connectToDB(testdb)
		updated = updateDB(data)
		updated = updateTags(data)
	except Exception as e:
		print(e)
		print("Encountered exception while updating records")
	finally:
		closeDBConnection()

if __name__ == '__main__':
	#testImportJson()
	#testMergeData()
	# testUpdateDB()
	testUpdateSingleResponseResults()