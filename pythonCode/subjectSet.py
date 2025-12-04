from pythonDBCreator import getCrawlRecord, connectToDB, closeDBConnection, fetchAllNearDuplicates, fetchAllStates
from globalNames import APPS,GS_JSON_NAME, UNALTERED_GS_TAG, RESULTS_FOLDER
from analyzeCrawl import writeCSV, getNumBins
from utils import importJson
import os
from datetime import datetime


# def countBins(states):
# 	numStates=0
# 	print(states[0])
# 	for state in states:
# 		numStates +=1

# 	return numStates

def countCategories(pairs):
	print(str(len(pairs)))
	clones = 0
	nd = 0
	nd1 = 0
	nd2 = 0
	nd3 = 0
	distinct = 0
	# print(pairs[0][14])
	for pair in pairs:
		# print(pair)
		classification = pair[14]
		tags = pair[15]
		if(tags == None):
			tags = ""
		else:
			print(tags)

		if(classification == 0):
			clones+=1
		elif classification == 1:
			nd+=1
			if('adv') in tags.lower():
				# print(tags)
				nd1 +=1
			elif('add' in tags.lower()):
				# print(tags)
				nd3 +=1
			else:
				nd2 +=1
		elif classification ==2:
			distinct +=1

	return {'clones':clones, 'nd1':nd1, 'nd':nd, 'nd2':nd2, 'nd3':nd3, 'distinct':distinct} 


def getSubjectSet(db = "../src/main/resources/GoldStandards/gs.db"):
	fieldNames = ['name', 'states', 'bins', 'pairs', 'clones', 'nd2', 'nd3', 'distinct']
	subjects = []
	try:
		connectToDB(db)
		for app in APPS:
			print(app)
			name = app
			crawlEntry =getCrawlRecord(app, 'crawl-'+app+'-60min')
			# print(crawlEntry)
			pairs = fetchAllNearDuplicates("WHERE appName='{}'".format(app))
			stats = countCategories(pairs)
			bins = 0
			# print(stats)
			gsCrawl = os.path.join(os.path.abspath('../src/main/resources/GoldStandards'), app, 'crawl-'+app+'-60min')
			if(os.path.exists(gsCrawl  + UNALTERED_GS_TAG)):
				gsCrawl = gsCrawl  + UNALTERED_GS_TAG

			gsJson = os.path.join(gsCrawl, 'gs', GS_JSON_NAME)
			if not (os.path.exists(gsJson)):
				print("Error!! No gsJson found {0}".format(gsJson))
				continue

			states = []
			try:
				states = importJson(gsJson)['states']
				bins = getNumBins(states)
			except Exception as ex:
				print(ex)
				print("error getting states from gsjson {0}".format(gsJson))
				continue

			subject = {'name':name, 'states':len(states), 'bins':bins, 'pairs':len(pairs), 'clones':stats['clones'], 'nd2':stats['nd2'], 'nd3':stats['nd3'], 'distinct':stats['distinct']}
			
			print(subject)
			subjects.append(subject)

		writeCSV(fieldNames, subjects, os.path.join(os.path.abspath(".."), RESULTS_FOLDER, "subjectSet" + "_" + str(datetime.now().strftime("%Y%m%d-%H%M%S")) + ".csv"))

	except Exception as ex:
		print(ex)
		print("Error getting subject set stats")
	finally:
		closeDBConnection()

def getDataSet(db = "gt10.db"):
	fieldNames = ['name', 'states', 'bins', 'pairs', 'clones', 'nd2', 'nd3', 'distinct']
	subjects = []
	try:
		connectToDB(db)
	
		pairs = fetchAllNearDuplicates("WHERE human_classification>=0")
		stats = countCategories(pairs)
		print(stats)
		
	except Exception as ex:
		print(ex)
		print("Error getting subject set stats")
	finally:
		closeDBConnection()






if __name__=="__main__":
	# getSubjectSet()
	getDataSet()
