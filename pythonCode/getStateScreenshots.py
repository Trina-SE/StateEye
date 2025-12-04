import os
import shutil
import sys
import fnmatch
from pythonDBCreator import findDir

statenames = []
crawlFolderPattern = 'crawl[0123456789]*'



def createStateScreenshotsinPath(path):
	try:
		if not os.path.exists(path+"/stateScreenshots"):
			os.makedirs(path+"/stateScreenshots")

		states= os.listdir(path + "/states")

		for state in states:
			statenames.append(os.path.splitext(state)[0])

		screenshots= os.listdir(path + "/screenshots")

		for screenshot in screenshots:
			screenshotname = os.path.splitext(screenshot)[0]
			if(screenshotname in statenames):
				shutil.copy(path+ "/screenshots/" + screenshot, path+ "/stateScreenshots/")
	except Exception as ex:
		print("Error creating screesnhtos for {0}".format(path))
		print(ex)

def main():
	if(len(sys.argv) !=2):
		print("usage : script path_to_crawl")
		quit()

	path = sys.argv[1]
	dirs = findDir('crawlFolderPattern', path)

###########################################################################
## Tests ############
###########################################################################
def testFindDir():
	testPath = "/"
	dirs = findDir(crawlFolderPattern, testPath)
	print(dirs)

if __name__ == '__main__':
	# main()
	# testFindDir()