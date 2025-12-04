#!/bin/bash
BASEDIR=$1
sed -i -e "s+BrowserType.CHROME,+BrowserType.CHROME_HEADLESS,+g" $BASEDIR/src/test/java/generated/GeneratedTests.java
sed -i -e "s+private final boolean mutate = true;+private final boolean mutate = false;+g" $BASEDIR/src/test/java/generated/GeneratedTests.java

if [ $# -ge 2 ]
then
  URL=$2
  echo $URL
    sed -i -e "s+.*private final String URL.*+private final String URL = \"$URL\";+g" $BASEDIR/src/test/java/generated/GeneratedTests.java
fi

echo "Compiling generated tests source files..."
javac -cp "/home/fraggen/fraggen/jars/crawljax-examples-4.0-beta-jar-with-dependencies.jar" "$BASEDIR/src/test/java//generated/GeneratedTests.java"
echo "Running generated tests..."
java -cp "/home/fraggen/fraggen/jars/crawljax-examples-4.0-beta-jar-with-dependencies.jar":"$BASEDIR/src/test/java/" org.testng.TestNG $BASEDIR/testng.xml
