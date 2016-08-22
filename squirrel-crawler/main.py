# Package Imports
import Queue
import threading
import ujson
import time

# Local Imports
import config
import database
import web
import words
import output
import error


# Constants
start_url = "http://www.mit.edu"

# Variables
validating_queue = Queue.Queue()
validated = []
validating_queue.put(start_url)
processed = []

processing_queue = Queue.Queue()

# main()
def main():
	output.console_log("Spawning threads...")
	threads = []
	for i in range(config.validating_threads):
		thread = ValidateUrls(validating_queue, processing_queue)
		thread.setDaemon(True)
		threads.append(thread)
		thread.start()

	for i in range(config.processing_threads):
		thread = ProcessUrls(validating_queue, processing_queue)
		thread.setDaemon(True)
		threads.append(thread)
		thread.start()

	output.datafile_init(["Urls Total", "Urls New"])
	for i in range(config.outputing_threads):
		thread = Output()
		thread.setDaemon(True)
		threads.append(thread)
		thread.start()
	output.console_log("Spawned " + str(len(threads)) + " threads.")
	validating_queue.join()
	processing_queue.join()

# Functions

# Classes
class Output(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		lastProcessed = 0
		while True:
			time.sleep(config.output_interval)
			output.datafile_log([len(processed), len(processed) - lastProcessed])
			lastProcessed = len(processed)

class ValidateUrls(threading.Thread):
    def __init__(self, validating_queue, processing_queue):
        threading.Thread.__init__(self)
        self.validating_queue = validating_queue
        self.processing_queue = processing_queue

    def run(self):
        while True:
			# Get queued url
			url = self.validating_queue.get()

			# Validate url
			if web.validate(url):
				# Place into processing queue
				self.processing_queue.put(url)

			# Signal job completion
			validated.append(url)
			self.validating_queue.task_done()
			
class ProcessUrls(threading.Thread):
    def __init__(self, validating_queue, processing_queue):
        threading.Thread.__init__(self)
        self.validating_queue = validating_queue
        self.processing_queue = processing_queue

    def run(self):
        while True:
			# Get queued url
			url = self.processing_queue.get()

			# GET page
			page = web.get(url)

			if page != False:
				# Get tree
				tree = web.tree(page)
				if tree != False:
					# Get urls
					urls = web.urls(tree)
	
					# Process url
					output.console_log(url)	
				
					# Add urls to validation queue
					for newUrl in urls:
						if (newUrl in validated):
							error.urlValidatedError()
						else:
							self.validating_queue.put(newUrl)
			
			# Signal job completion
			processed.append(url)
			self.processing_queue.task_done()

# Program
main()
