#!/usr/bin/env python
import glob
import re
import os
import urllib
import urllib2
import json
from hashlib import sha256
import time
import base64
import argparse


parser = argparse.ArgumentParser (description='Batch process images with DarbeeOnDemand.')
parser.add_argument ('--server', dest='server', default='https://darbeeondemand.com/farm/api/')
parser.add_argument ('--token', dest='token', required=True)
parser.add_argument ('--mode', dest='mode', required=True)
parser.add_argument ('--presence', dest='presence', type=int, required=True)


args = parser.parse_args ()
SERVER_URL = args.server
TOKEN = args.token
DARBEE_MODE = args.mode
DARBEE_LEVEL = str (args.presence)



class Task (object):
	def __init__ (self, source, batch_name):
		self.source = source
		self.batch_name = batch_name
		self.done = False
		self.pending = False
		self.source_hash = None
	
	def getBaseName (self):
		return self.source[:-4]
	
	def getResultName (self):
		return self.getBaseName () + '.' + self.batch_name + '.png'
	
	def calculateSourceHash (self):
		with open (self.source, 'rb') as f:
			self.source_hash = sha256 (f.read ()).hexdigest ()


# Finds all incomplete tasks
def find_tasks (batch_name):
	sources = glob.glob ('*.png')
	tasks = []

	for source in sources:
		task = Task (source, batch_name)

		# Skip non-sources
		if re.match ('.*\.(hd|gaming|full)[0-9]+\.png$', source):
			continue

		# Skip completed
		if os.path.isfile (task.getResultName ()):
			continue

		task.calculateSourceHash ()
		tasks.append (task)
	
	return tasks


def do_farm (method, data):
	url = SERVER_URL + method
	data = urllib.urlencode (data)
	request = urllib2.Request (url, data)
	response = urllib2.urlopen (request)
	result = response.read ()
	result = json.loads (result)

	if 'error' in result:
		print "API Error in '%s': %s" % (method, result['error'])
	
	print "Farm Response (%s): " % method, result

	return result


def download_result (task, result):
	response = urllib2.urlopen (SERVER_URL + 'download/' + result)
	data = response.read ()

	# TODO
	with open (task.getResultName (), 'wb') as f:
		f.write (data)
	
	print "Task Completed"


def farm_upload (task, token):
	result = do_farm ('file_exists', {'hash': task.source_hash})

	if result['exists'] == True:
		print "%s already on server." % task.source
		return

	with open (task.source, 'rb') as f:
		result = do_farm ('upload', {'token': token, 'data': base64.b64encode (f.read ())})

		if 'error' in result:
			print "%s caused an error." % task.source


def update_tasks (token, tasks):
	pending_count = 0

	# Get list of 20 most recent jobs
	recent_jobs = do_farm ('recent_work', {'token': token, 'offset': 0})['work_orders']
	recent_jobs += do_farm ('recent_work', {'token': token, 'offset': 10})['work_orders']

	# Analyze recent jobs
	completed_hashes = {}
	pending_hashes = {}

	for job in recent_jobs:
		if job['darbee_mode'] == 'hidef':
			job_batch_name = 'hd'
		elif job['darbee_mode'] == 'gaming':
			job_batch_name = 'gaming'
		else:
			job_batch_name = 'full'

		job_batch_name += str (job['darbee_level'])

		if job['status'] != 'done':
			pending_count += 1
			pending_hashes[job['source'] + job_batch_name] = 1
			continue

		completed_hashes[job['source'] + job_batch_name] = job['result']
	
	for task in tasks:
		key = task.source_hash + task.batch_name

		task.pending = key in pending_hashes

		if not key in completed_hashes:
			continue

		download_result (task, completed_hashes[key])
		task.done = True
	
	return pending_count


if DARBEE_MODE == 'hidef':
	batch_name = 'hd' + DARBEE_LEVEL
elif DARBEE_MODE == 'gaming':
	batch_name = 'gaming' + DARBEE_LEVEL
elif DARBEEMODE == 'fullpop':
	batch_name = 'full' + DARBEE_LEVEL
else:
	print "ERROR: Bad Darbee Mode"
	exit (-1)


print "Building list of tasks..."
tasks = find_tasks (batch_name)
print "List complete. %d tasks remaining." % len (tasks)
token = TOKEN

while True:
	pending_count = update_tasks (token, tasks)

	# Clear completed tasks
	tasks = [t for t in tasks if not t.done]
	available = [t for t in tasks if not t.pending]

	print "%d pending..." % pending_count
	print "%d remaining..." % len (tasks)
	
	while pending_count < 8 and len (available) > 0:
		pending_count += 1
		task = available[0]
		available = available[1:]

		print "Uploading..."
		farm_upload (task, token)
		print "Submitting job..."
		do_farm ('submit_work', {'token': token, 'source': task.source_hash, 'darbee_level': str (DARBEE_LEVEL), 'darbee_mode': DARBEE_MODE, 'watermark': 0})
		print "New job created."

	if len (tasks) == 0:
		break

	print "Sleeping..."
	time.sleep (20.0)

print "No more tasks."
