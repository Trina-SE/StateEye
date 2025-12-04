from globalNames import ALGOS
from importResponses import importJson
from pythonDBCreator import updateNearDuplicate, connectToDB, closeDBConnection


def updateDBWithAlgoPairs(algoData, appName, crawl, algo):
	updatedPairs = 0
	ignoredPairs = 0
	sameValuePairs = 0
	errorPairs =0
	# randomNDs = fetchRandomNearDuplicates(NUMBER*2)
	for i in range(0, len(algoData)):
		try:
			pair = algoData[i]
			state1 = pair['state1']
			state2 = pair['state2']
			value = pair['response']
			print(state1 + ": " + state2 + ":" + str(value))
			Inserted, Updated, Ignored, SameValue, Error = updateNearDuplicate(appName, crawl, state2, state1, algo,
																			   value, False)

			if Error:
				errorPairs += 1

			if Ignored:
				ignoredPairs += 1

			if SameValue:
				sameValuePairs += 1

			if Updated:
				updatedPairs += 1


		except Exception as e:
			print(e)
			print("Exception while updating Record with Response : ")

		print(str(updatedPairs) + " " + str(ignoredPairs) + " " + str(sameValuePairs) + " " + str(errorPairs))
	return updatedPairs, ignoredPairs, sameValuePairs, errorPairs


def updateDBWithHybridJson(json, appName, crawl):
	pairs = importJson(json)
	algo = ALGOS.HYBRID
	print(algo)
	print(algo.value[0])

	updateDBWithAlgoPairs(pairs, appName, crawl, algo.value[0])


if __name__=='__main__':
	db = 'gs_hybrid.db'
	connectToDB(db)
	jsonFile = 'GroundTruth/petclinic/crawl-petclinic-60min/comp_output/HybridClassification.json'
	updateDBWithHybridJson(jsonFile, 'petclinic', 'crawl-petclinic-60min')
	closeDBConnection()