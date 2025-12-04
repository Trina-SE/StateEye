from enum import Enum
import os

class ALGOS(Enum):
	DOM_RTED= ['DOM-RTED', 0.0, 'lt']
	# DOM_Levenshtein = ['DOM-Levenshtein', 0.1, 'lt']
	# DOM_contentHash = ['DOM-contentHash', 100, 'lt']
	# DOM_SIMHASH = ['DOM-SIMHASH', 10, 'lt']
	# VISUAL_BLOCKHASH = ['VISUAL-BlockHash', 23.4, 'lt'] # 234 max
	# VISUAL_PHASH = ["VISUAL-PHash", 5.7, 'lt'] #57 max
	VISUAL_HYST = ["VISUAL-Hyst", 100, 'lt'] # max 1.085430529912071E13
	# VISUAL_PDIFF = ["VISUAL-PDiff", 0.1, 'lt']
	# VISUAL_SIFT = ["VISUAL-SIFT", 90.0, 'gt']
	# VISUAL_SSIM = ["VISUAL-SSIM", 1.0, 'gt']
	HYBRID = ["HYBRID", -1, "na"]

############### APPS #################
APPS = ['addressbook', 'petclinic', 'claroline', 'dimeshift', 'pagekit', 'phoenix', 'ppma', 'mantisbt']
DOCKERIZED_APPS = ['petclinic', 'dimeshift', 'pagekit', 'phoenix', 'retroboard', 'splittypie', 'ppma', 'mrbs', 'mantisbt', 'collabtive', 'addressbook', 'claroline']
ND3_APPS = ['addressbook', 'pagekit', 'phoenix']
DOCKER_LOCATION = os.path.abspath(os.path.join("..","dockerApps"))


def getDockerName(appName, version=0):
	try:
		if version==0:
			return VERSION0_DOCKER_NAME[appName]
		elif version==1:
			return VERSION1_DOCKER_NAME[appName]
		elif version==-1:
			return VERSION0_DOCKER_NAME_ALT[appName]
	except Exception as ex:
		print(ex)
		print("Unable to get docker name for app {0} version {1}".format(appName, version))
		return None
	# return appName

def getHostNames():
	return ['192.168.99.101', 'localhost', 'amesbah-macpro.ece.ubc.ca']

def isDockerized(appName):
	if(appName.strip() in DOCKERIZED_APPS):
		return True
	return False

def isNd3App(appName):
	if(appName.strip() in ND3_APPS):
		return True
	return False

############### DB NAMES #################
DB_NAME = 'gt10.db'
GS_DB_NAME = 'gs.db'

############## FOLDER AND FILE NAMES ################
SCREENSHOTS = 'screenshots'
DOMS = 'doms'
STATES = 'states'
COMP_OUTPUT='comp_output'
RESULTS_FOLDER = "results"
VERIFIED_CLASSIFICATION_JSON_NAME = 'classification_verified.json'
TEST_ANALYSIS_JSON = 'testAnalysis.json'
APP_CHANGE_ANALYSIS_JSON='testAnalysis_change.json'
TEST_ANALYSIS_FOLDER = 'analysis'
GENERATED_CLASSIFICATION_JSON_NAME = 'classification.json'
GS_JSON_NAME = 'gsResults.json'
RESULT_JSON = "result.json"
RESULT_SKEL_JSON = "result_skel.json"
CONFIG_JSON = "config.json"
DISTANCES_RESPONSES_JSON = 'classification_with_distances.json'

NODESIZES_JSON = 'nodeSizes.json'
PIXELSIZES_JSON = 'pixelSizes.json'
DOMSIZES_JSON = 'domSizes.json'

def getResultsFolder():
	return os.path.join(os.path.abspath(".."), RESULTS_FOLDER)

def getPreDefinedSaveJsonLocation():
	return os.path.abspath("../saveJsons")

def buildCrawlFolderName(appName, algo, threshold, runtime=5):
	crawlFolderName = appName + "_" + algo + "_" + str(float(threshold))+ "_" + str(runtime) + "mins"
	return crawlFolderName

def getHostName(crawlpath):
	for host in getHostNames():
		if os.path.exists(os.path.join(crawlpath, host)):
			return host

	return None

############## Test ORACLES ################
class ORACLES(Enum):
	Rted = "rted"
	# Rted_Text = "rted_text"
	Histogram = "hist"

	# HTML = "string"
	# Content = "string_content"
	# Structure = "string_structure"
	FragGen = "hybrid_oracle"

class MUTATORS(Enum):
	SUBTREE = "SubtreeMutator"
	TEXT = "TextNodeMutator"
	TAG = "TagMutator"
	ATTR = "AttributeMutator"

############## THRESHOLD SETS ################
class DB_SETS(Enum):
	GT10_DB_DATA = {'name':'gt10_db_data'}
	GS_DB_DATA = {'name':'gs_db_data'}

class FILTER(Enum):
	CLONES = {'name':'clones'}
	NEAR_DUPLICATES = {'name':'near_duplicates'}
	DIFFERENT = {'name':'different'}
	NOZEROES = {'name':'noZeroes'}
	NEAR_DUPLICATES_DYN = {'name':'near_duplicates_dyn'}
	NEAR_DUPLICATES_ADD = {'name':'near_duplicates_add'}
	ALL = {'name':'all'}
	OPTIMAL = {'name':'optimal'}
	OPTIMAL_ND3 = {'name': 'optimal_nd3'}
	OPTIMAL_CLASSIFICATION = {'name':'optimal_classification'}

class THRESHOLD_SETS(Enum):
	# FULLDB_QUART1 = 	{'name':'fullDB_quart1', 	 'percentile':25, 	'filter':FILTER.ALL, 				 'dataSet':[DB_SETS.GT10_DB_DATA, DB_SETS.GS_DB_DATA] , 'appSpecific': True}
	# FULLDB_MEDIAN = 	{'name':'fullDB_median', 	 'percentile':50, 	'filter':FILTER.ALL, 				 'dataSet':[DB_SETS.GT10_DB_DATA, DB_SETS.GS_DB_DATA] , 'appSpecific': True}
	# #EXCLUDE0_QUART1 = 	{'name':'exclude0_quart1', 	 'percentile':25, 	'filter':FILTER.NOZEROES,			 'dataSet':[DB_SETS.GT10_DB_DATA] , 'appSpecific': False}
	# HUMANCLONE_QUART3 = {'name':'humanClone_quart3', 'percentile':75, 	'filter':FILTER.CLONES, 			 'dataSet':[DB_SETS.GT10_DB_DATA, DB_SETS.GS_DB_DATA] ,	'appSpecific': True}#, DB_SETS.GS_DB_DATA
	# HUMANNDDYN_QUART1 = {'name':'humanNDDyn_quart1', 'percentile':25, 	'filter':FILTER.NEAR_DUPLICATES_DYN, 'dataSet':[DB_SETS.GS_DB_DATA] ,	'appSpecific': True}
	HUMANNDDYN_MEDIAN = {'name':'humanNDDyn_median', 'percentile':50, 	'filter':FILTER.NEAR_DUPLICATES_DYN, 'dataSet':[DB_SETS.GS_DB_DATA] ,	'appSpecific': True}
	# HUMANDIFF_MIN =		{'name':'humanDiff_min',	 'percentile':0, 	'filter':FILTER.DIFFERENT, 		  	 'dataSet':[DB_SETS.GT10_DB_DATA, DB_SETS.GS_DB_DATA] , 'appSpecific': True}
	# HUMANND_MEDIAN = 	{'name':'humanND_median',	 'percentile':50, 	'filter':FILTER.NEAR_DUPLICATES, 	 'dataSet':[DB_SETS.GT10_DB_DATA, DB_SETS.GS_DB_DATA] , 'appSpecific': True}#, DB_SETS.GS_DB_DATA
	OPTIMAL = {'name':'optimal', 'percentile':0, 'filter':FILTER.OPTIMAL, 'dataSet':[DB_SETS.GT10_DB_DATA, DB_SETS.GS_DB_DATA], 'appSpecific':True}
	# OPTIMAL_CLASSIFICATION_CLONE = {'name':'optimal_classification_clone',	 'percentile':25, 	'filter':FILTER.OPTIMAL_CLASSIFICATION, 	 'dataSet':[DB_SETS.GT10_DB_DATA] , 'appSpecific': False}
	# OPTIMAL_CLASSIFICATION_ND = {'name':'optimal_classification_nd',	 'percentile':75, 	'filter':FILTER.OPTIMAL_CLASSIFICATION, 	 'dataSet':[DB_SETS.GT10_DB_DATA] , 'appSpecific': False}
	# OPTIMAL_ND3 = {'name':'optimal', 'percentile':0, 'filter':FILTER.OPTIMAL_ND3, 'dataSet':[DB_SETS.GS_DB_DATA], 'appSpecific':True}

############# MISCELLANEOUS ########################
UNALTERED_GS_TAG = "_unaltered"

def getDockerList(version):
	if version == 1:
		return VERSION1_DOCKER_NAME
	if version == 0:
		return VERSION0_DOCKER_NAME
	if version == -1:
		return VERSION0_DOCKER_NAME_ALT

def getURLList(version):
	if version ==0:
		return VERSION0_URL_MAP
	if version ==1 :
		return VERSION1_URL_MAP
	if version ==-1: #mac-pro
		return VERSION0_URL_MAP_ALT

def getVersionURL(appName, version=0):
	url = getURLList(version)[appName]
	return url


VERSION1_URL_MAP = {'addressbook':'http://localhost:3000/addressbook8251/addressbook/index.php',
		   'petclinic':'http://localhost:9966/petclinic/',
		   'dimeshift':'http://localhost:30000/',
		   'ppma':'http://localhost:3000/ppma_052/index.php',
		   'mantisbt':'http://localhost:3000/mantisbt_v121/',
		   'pagekit':'http://localhost:3000/pagekit_1014/index.php/admin/dashboard',
		   'claroline': 'http://localhost:3000/claroline1119/'
		   }

VERSION0_URL_MAP = {'addressbook':'http://localhost:3000/addressbook825/index.php',
		   'petclinic':'http://localhost:9966/petclinic/',
		   'dimeshift':'http://localhost:30000/',
		   'ppma':'http://localhost:3000/ppma/index.php',
		   'mantisbt':'http://localhost:3000/mantisbt',
		   'pagekit':'http://localhost:3000/pagekit/index.php/admin/dashboard',
		   'phoenix': 'httP://localhost:4000',
			'claroline': 'http://localhost:3000/claroline11110/'
		   }

VERSION0_URL_MAP_ALT = {'addressbook':'http://localhost:8888/addressbook/addressbook-mod/addressbook/index.php',
		   'petclinic':'http://localhost:9966/petclinic/',
		   'dimeshift':'http://192.168.99.101:30000/',
		   'ppma':'http://192.168.99.101:3000/ppma/index.php',
		   'mantisbt':'http://192.168.99.101:3000/mantisbt',
		   'pagekit':'http://192.168.99.101:3000/pagekit/index.php/admin/dashboard',
		   'phoenix': 'http://192.168.99.101:4000',
			'claroline': 'http://localhost:8888/claroline/claroline-1.11.10/'
		   }

VERSION1_DOCKER_NAME = {
	'addressbook': 'addressbook',
	'claroline': 'claroline',
	'petclinic': 'petclinic1',
	'dimeshift': 'dimeshift2',
	'pagekit': 'pagekit',
	'ppma': 'ppma',
	'mantisbt':'mantisbt',
	'phoenix':'phoenix'
}

VERSION0_DOCKER_NAME = {
	'addressbook': 'addressbook',
	'claroline': 'claroline',
	'petclinic': 'petclinic0',
	'dimeshift': 'dimeshift',
	'pagekit': 'pagekit',
	'ppma': 'ppma',
	'mantisbt':'mantisbt',
	'phoenix':'phoenix'
}
VERSION0_DOCKER_NAME_ALT = {
	'dimeshift': 'dimeshift',
	'pagekit': 'pagekit',
	'ppma': 'ppma',
	'mantisbt':'mantisbt',
	'phoenix':'phoenix'
}

def testEnum():
	for thresholdSet in THRESHOLD_SETS:
		print(thresholdSet.value['name'])

if __name__=="__main__":
	testEnum()
