import sqlite3
from pythonDBCreator import connectToDB, closeDBConnection, conn, cursor, createTables, getCrawlRecord, fetchNearDuplicates, resetDatabase, addCrawl, checkCrawlEntryExists, ALGOS, updateNearDuplicateMulti, mergeDatabase, createTables
import time
import sys
import os
conn = 'noConnYet'
cursor = 'noCursorYet'


def testMerge():
	testDB = '/Users/fraggen/VisCrawler/Test/test.db'
	toMergeDB = '/Users/fraggen/VisCrawler/Test/toMergeTest.db'

	connectToDB(testDB)
	resetDatabase()

	for i in range(1):
		tuples = {}
		if not addCrawl('testapp' + str(i), 'testcrawl'+str(i), 10, 100, 5):
			print("COULD NOT added app entry")
		if not checkCrawlEntryExists('testapp' + str(i), 'testcrawl'+str(i)):
			print("ADDED ENTRY DOESN'T EXIST !! ")
		#tuples[( 'state1'+ str(i), 'state2'+str(i))] = {}
		for algo in ALGOS:
			for j in range(1):
				state1 = 'state' + str(j)
				state2 = 'state' + str(j+2)
			
				if ('testapp' + str(i) , 'testcrawl' + str(i), state1, state2) in tuples:
				#	print("TUPLE already present updating my value to it")
					tuples[( ('testapp' + str(i) , 'testcrawl' + str(i), state1, state2))][str(algo).split('.')[1]] = 0.02*i*j
				else:
				#	print("TUPLE not present creating it ")
					tuples[( ('testapp' + str(i) , 'testcrawl' + str(i), state1, state2))] = {}
					tuples[( ('testapp' + str(i) , 'testcrawl' + str(i), state1, state2))][str(algo).split('.')[1]] = 0.02*i*j
			#print("Updating my tuples for : testapp " + str(i))
			#print(tuples)

			added, failed = updateNearDuplicateMulti(tuples)
			print(str(added)  + " tuples added and " + str(failed) + " tuples failed" )

	closeDBConnection()

	connectToDB(toMergeDB)
	resetDatabase()

	for i in range(10):
		tuples = {}
		if addCrawl('toMergeApp' + str(i), 'toMergeCrawl'+str(i), 10, 100, 5):
			print("SUCCESSFULLY added app entry")
		if checkCrawlEntryExists('testapp' + str(i), 'testcrawl'+str(i)):
			print("ADDED ENTRY EXISTS !! ")
		#tuples[( 'state1'+ str(i), 'state2'+str(i))] = {}
		for algo in ALGOS:
			for j in range(10):
				state1 = 'state' + str(j)
				state2 = 'state' + str(j+2)
				
				if ('toMergeApp' + str(i) , 'toMergeCrawl' + str(i), state1, state2) in tuples:
				#	print("TUPLE already present updating my value to it")
					tuples[( ('toMergeApp' + str(i) , 'toMergeCrawl' + str(i), state1, state2))][str(algo).split('.')[1]] = 0.02*i*j
				else:
				#	print("TUPLE not present creating it ")
					tuples[( ('toMergeApp' + str(i) , 'toMergeCrawl' + str(i), state1, state2))] = {}
					tuples[( ('toMergeApp' + str(i) , 'toMergeCrawl' + str(i), state1, state2))][str(algo).split('.')[1]] = 0.02*i*j
		print("Updating my tuples for : toMergeCrawl " + str(i))
	#print(tuples)

		added, failed = updateNearDuplicateMulti(tuples)
		print(str(added)  + " tuples added and " + str(failed) + " tuples failed" )

	closeDBConnection()
	#time.sleep(5)

	connectToDB(testDB)
	mergeDatabase(toMergeDB)

	print( fetchNearDuplicates('testapp1', 'testcrawl1','teststate1', 'teststate2'))
	print(getCrawlRecord('testapp1', 'testcrawl1'))

	print(fetchNearDuplicates('toMergeApp1', 'toMergeCrawl1','teststate1', 'teststate2'))
	print(getCrawlRecord('toMergeApp1', 'toMergeCrawl1'))
	closeDBConnection()

#testMerge()



###########################################################################
## Main Code ############
###########################################################################

if __name__ == '__main__':
	COMBINED_DB = ""
	overwriteResponse = False
	if len(sys.argv) <=1 :
		print("Argument missing : COMBINED_DB Name ")
		COMBINED_DB = os.path.abspath(input('Please provide the name of COMBINED DB YOU WANT TO CREATE.').strip())

	else :
		COMBINED_DB = os.path.abspath(sys.argv[1].strip())


	print("Your database will be located at  : " + COMBINED_DB)
	
	if os.path.exists(COMBINED_DB):
		response = input("A Database already exists.. You might lose some data if you continue with it. DO you want to use it (Y/N) ?").strip()
		if(response.lower() == 'y'):
			print('Okay. Continuing with the provided database')
			overwriteResponse = True
		else :
			print("ABORTING!! Please run again with database of your choice.")
			sys.exit()

	try:
		connectToDB(COMBINED_DB)
	except Exception as e : 
		print("Exception when trying to connect to provided DB : {0}. ABORTING!! ".format(COMBINED_DB))
		sys.exit()

	if not overwriteResponse :
		print("Creating the database for the first time : " + os.path.abspath(COMBINED_DB))
		createTables()

	doneMerging = False
	mergedDatabases  = []
	finalResult = {'totalAppsDeleted' : 0, 'totalNDsDeleted' : 0, 'totalAppsInserted' : 0, 'totalNDsInserted' : 0}
	try :
		while not doneMerging: 	
			response = input("Do you want to merge a Database (Y/N) ?")
			if(response.lower() == 'y'):
				print('Okay.')
			else :
				print("Done.")
				break

			TOMERGEDB = os.path.abspath(input('Please provide the path of DB YOU WANT TO MERGE.').strip())
			

			if not os.path.exists(TOMERGEDB):
				print("No Database found : " + TOMERGEDB)
				continue
			
			if TOMERGEDB in mergedDatabases:
				print("You already merged this database this time.")
				print("Databases merged so far in this run > {0}".format(str(mergedDatabases)))
				continue

			if TOMERGEDB == COMBINED_DB :
				print("Cannot Merge a database into itself!!")
				continue

			print("Your database {0} will be merged with {1}. ".format(os.path.abspath(TOMERGEDB), os.path.abspath(COMBINED_DB)))
			mergeResult = mergeDatabase(TOMERGEDB)
			if(mergeResult['status']) : 
				finalResult['totalAppsDeleted'] += mergeResult['deletedApps']
				finalResult['totalNDsDeleted'] += mergeResult['deletedNDs']
				finalResult['totalAppsInserted'] += mergeResult['insertedApps']
				finalResult['totalNDsInserted'] += mergeResult['insertedNDs']
			else :
				print("MERGE UNSUCCESSFUL !! " + TOMERGEDB)
				continue

			mergedDatabases.append(os.path.abspath(TOMERGEDB))

	except Exception as e:
		print("Error in merging ")
		print(e)
	finally:
		closeDBConnection()
		if overwriteResponse:
			print("YOU HAVE OVERWRITTEN THE COMBINED DATABASE : " + COMBINED_DB)  
		else :
			print("YOU HAVE CREATED A NEW COMBINED DATABASE : " + COMBINED_DB)
		
		print("DATABASES MERGED IN THIS RUN : " + str(mergedDatabases))
		print(str(finalResult))
	






