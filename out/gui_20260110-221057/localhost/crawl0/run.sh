#!/bin/bash
BASEDIR=$(dirname "$0")
echo "Compiling generated tests source files..."
javac -cp "$BASEDIR/../../../libs/*" "$BASEDIR/src/test/java/\generated\GeneratedTests.java"
echo "Running generated tests..."
java -cp "$BASEDIR/../../../libs/*":"$BASEDIR/src/test/java/" org.testng.TestNG testng.xml