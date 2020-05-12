#!/bin/bash

export PATH=$PATH:/home/cgustave/github/python/packages/taskwatcher/taskwatcher/tests

echo "***" > debug.log
echo "" >> debug.log

# Run testing for all objects

for NAME in parse database control launch; do

	echo
	echo "==========================================="
	echo "= PYTHON code analysis : $NAME"
	echo "==========================================="
	pyflakes3 "$NAME".py
	echo

	#echo "=========================================="
	#echo "= PEP 8 codestyle check : $NAME" 
	#echo "=========================================="
	#pycodestyle "$NAME".py --statistics
	#echo

	echo "==========================================="
	echo "= UNIT TESTS : $NAME"
	echo "==========================================="
	python3 -m coverage run --rcfile tests/coveragerc  tests/test_"$NAME".py

	echo
	echo "==========================================="
	echo "= COVERAGE : $NAME"
	echo "==========================================="
	python3 -m coverage report --show-missing
	echo

	echo "==========================================="
	echo "= DOCUMENTATION : $NAME"
	echo "==========================================="
	python3 -m pydoc "$NAME"  > README.md

	echo "" >> debug.log
done

