from pythonDBCreator import connectToDB, closeDBConnection, SCREENSHOTS,  fetchRandomNearDuplicates, updateNearDuplicate, find, getAllPairsFromCSV, ALGOS, createTables, updateState, splitPathIntoFolders, getStateCharacteristics
from importResponses import importJson
import os




def testUpdateStateCharacteristics():

	domSizeJsons = find('result.json', 'gt10/')
	#updatedCSVs = [updatedCSVs[0]]
	print(len(domSizeJsons))
	testdb = 'gt10.db'

	totalupdated = 0
	totalSynced = 0
	totalErrored = 0
	totalIgnored = 0
	done = []
	skipped = []
	try:
		connectToDB(testdb)
		createTables()
		for domSizeJson in domSizeJsons:
		# domSizeJson = domSizeJsons[0]
		# if domSizeJson != None:
			path, file = os.path.split(domSizeJson)
			# nodeSizeJson = os.path.join(os.path.abspath(path), '', 'nodeSizes.json')
			# pixelSizeJson = os.path.join(os.path.abspath(path), '', 'pixelSizes.json')
			# domSizes = importJson(domSizeJson)
			# nodeSizes = importJson(nodeSizeJson)
			# pixelSizes = importJson(pixelSizeJson)

			# print(path)
			folders = splitPathIntoFolders(domSizeJson)
			# #print(folders)
			appName = folders[1]
			crawl = folders[0]

			result = getStateCharacteristics(path, appName, crawl, insertIfNotPresent = False)
			# updatedPairs, ignoredPairs, sameValuePairs, errorPairs = updateStateCharacteristics(appName, crawl, domSizes, nodeSizes, pixelSizes)
			if result['done']:
				totalupdated += result['updatedStates']
				totalSynced += result['updatedStates']
				totalSynced += result['sameValueStates']
				totalErrored+= result['erroredStates']
				totalIgnored += result['ignoredStates']
				done.append((appName,crawl))
			else:
				skipped.append((appName,crawl))
			print(result)
	except Exception as e:
		print(e)
		print("Encountered exception while updating records")
	finally:
		closeDBConnection()

	print("Updated total {0} state records from {1} apps".format(totalupdated, len(domSizeJsons)))
	print("Synced total {0} state records from {1} apps".format(totalSynced, len(domSizeJsons)))
	print("Errored {0} states records from {1} apps".format(totalErrored, len(domSizeJsons)))
	print("Ignored {0} states records from {1} apps".format(totalIgnored, len(domSizeJsons)))
	print("done {0}".format(done))
	print("skipped {0}".format(skipped))

if __name__=='__main__':
	testUpdateStateCharacteristics()

