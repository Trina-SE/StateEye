from pythonDBCreator import connectToDB, closeDBConnection, SCREENSHOTS,  fetchRandomNearDuplicates, updateNearDuplicate, find, getAllPairsFromCSV, ALGOS, splitPathIntoFolders, fetchCurrentNDAlgo, addNearDuplicate
import os 

def updateDBWithAlgoPairs(algoData, appName, crawl, algo):
	updatedPairs = 0
	ignoredPairs = 0
	sameValuePairs = 0
	errorPairs =0
	#randomNDs = fetchRandomNearDuplicates(NUMBER*2)
	for i in range(0, len(algoData)):
		try:
			pair = algoData[i]
			state1 = pair['state1']
			state2 = pair['state2']
			value = pair['distance']
			print(state1 + ": " + state2 + ":" + str(value))
			Inserted, Updated, Ignored, SameValue, Error = updateNearDuplicate(appName, crawl, state1, state2, algo, value, False)
			
			if Error:
				errorPairs+=1
			
			if Ignored:
				ignoredPairs +=1

			if SameValue:
				sameValuePairs +=1

			if Updated:
				updatedPairs +=1


		except Exception as e:
			print(e)
			print("Exception while updating Record with Response : ")
	return updatedPairs, ignoredPairs, sameValuePairs, errorPairs

def updateDBWithCSVs(updatedCSVs, algo, db):

	totalupdated = 0
	totalSynced = 0
	
	try:
		connectToDB(db)
		for csv in updatedCSVs:
		#if csv != None:
			print(csv)
			folders = splitPathIntoFolders(csv)
			#print(folders)
			appName = folders[2]
			crawl = folders[1]
			pairs = getAllPairsFromCSV(csv)
			updatedPairs, ignoredPairs, sameValuePairs, errorPairs = updateDBWithAlgoPairs(pairs, appName, crawl, algo)
			totalupdated += updatedPairs
			totalSynced += updatedPairs
			totalSynced += sameValuePairs
			print("Updated : {0}, Ignored not present in db: {1}, Ignored same Value : {2}, Errored : {3}  db records".format(updatedPairs, ignoredPairs, sameValuePairs, errorPairs))
	except Exception as e:
		print(e)
		print("Encountered exception while updating records")
	finally:
		closeDBConnection()

	print("Updated total {0} db records from {1} csvs".format(totalupdated, len(updatedCSVs)))
	print("Synced total {0} db records from {1} csvs".format(totalSynced, len(updatedCSVs)))


def testUpdateDB():
	
	#updatedCSVs = [updatedCSVs[0]]
	
	testdb = '/gt10.db'
	

	normalizedPDiffCSVs = find('*PDiff-normalized.csv', '/gt10/')
	updateDBWithCSVs(normalizedPDiffCSVs,  str(ALGOS.VISUAL_PDIFF).split('.')[1], testdb)

def testFetch():
	testdb = '/gt10.db'
	conn, cursor = connectToDB(testdb)
	appName ='parktherme.at'
	crawl='crawl0'
	state1='index' 
	state2='state2'
	algo = str(ALGOS.DOM_RTED).split('.')[1]
	print(algo)
	existingEntries = fetchCurrentNDAlgo(appName, crawl, state1, state2, algo)
	print(existingEntries)
	#cursor.execute("select state1,state2,DOM_RTED from nearduplicates where appname='parktherme.at' and crawl='crawl0' and state1='index' and state2='state1'")
	cursor.execute("SELECT DOM_RTED FROM nearduplicates WHERE appname = 'parktherme.at' AND crawl = 'crawl0' AND state1 = 'index' AND state2 = 'state1'")
	existingEntries = cursor.fetchall()	
	print(existingEntries)
	#updateNearDuplicate(appName, crawl, state1, state2, algo, "-20.0", False)
	stmt='''UPDATE nearduplicates SET DOM_RTED = -20.0
								WHERE appname = 'parktherme.at'
								AND crawl = 'crawl0'
								AND state1 = 'index'
								AND state2 = 'state1' '''

	cursor.execute(stmt)
	conn.commit()

	cursor.execute("SELECT DOM_RTED FROM nearduplicates WHERE appname = 'parktherme.at' AND crawl = 'crawl0' AND state1 = 'index' AND state2 = 'state1'")
	existingEntries = cursor.fetchall()	
	print(existingEntries)

	appName = 'test'
	crawl = 'testcrawl'
	# state1 = 'abc'
	# state2 = '123'
	addNearDuplicate(appName, crawl, state1, state2)
	existingEntries = fetchCurrentNDAlgo(appName, crawl, state1, state2, algo)
	print(existingEntries)

	updateNearDuplicate(appName, crawl, state1, state2, algo, "-20.0", False)
	existingEntries = fetchCurrentNDAlgo(appName, crawl, state1, state2, algo)
	print(existingEntries)
	closeDBConnection()
	
if __name__=='__main__':
	testUpdateDB()
	#testFetch()
