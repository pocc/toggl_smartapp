# Makefile for starting smartapp reflector for toggl
# This script will listen for requests from Samsung's groovy IDE and get/post to toggl's servers
# the reason for this is that the groovy IDE is hard to debug, but sending data over gets is ok
.PHONY: run

run:
	python3 toggl_smartapp.py >> smartapp.log  2>&1 &
