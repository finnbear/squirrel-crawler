# +---------+
# | Imports |
# +---------+

import sys
import lxml
from lxml import html
from lxml import etree
import requests

# +-----------+
# | Variables |
# +-----------+

# Data file base path and schedule
data_file_path = 'data.csv'
data_file_schedule = 10
data_file_index = 0

# The first url to process
start_url = 'http://www.mit.edu'

# Urls will be judged based on whether they contain this string
score_string = 'mit.edu'

# Variables to track all data metrics
page_scores = []
page_lengths = []

# A variable to track how many pages have been processed
page_count = 0

# A list to keep track of all the pages that have been processed
processed_pages = []

# Variables to keep track of how many times certain errors have occured
error_already_processed = 0
error_timeout = 0
error_connection_error = 0
error_too_many_redirects = 0
error_tree_parse = 0
error_missing_http = 0
error_invalid_file = 0
error_keyboard_interrupt = 0

# +--------+
# | main() |
# +--------+

def main():
	# Clear and then write a header to the data file
	data_file = open(data_file_path, 'w')
	data_file.truncate()
	data_file.write('Index, Error Count, Average Score, Average Length\n')
	data_file.close()

	# Start off the program by processing the starting url
	processPage(start_url)
	return

# +-----------+
# | Functions |
# +-----------+

def processPage(url):
	# Globals
	global lxml

	global processed_pages
	global page_count
	global score_string
	global page_scores
	global page_lengths

	global data_file_path
	global data_file_schedule
	global data_file_index

	global error_already_processed
	global error_timeout
	global error_connection_error
	global error_too_many_redirects
	global error_tree_parse
	global error_missing_http
	global error_invalid_file
	global error_keyboard_interrupt

	# Print a header for the new page
	print '--------------------------------------------------------------'

	try:
		# Check if url starts with the http
		if url[0:7] != 'http://':
			error_missing_http += 1
			print error_missing_http, '| Missing http, url: ', url
			return

		# Check if the url is only a link to part of the same page
		#if url[0] == '#':
		#	return

		# Check if the url starts with /
		#if url[0] == '/':
		#	return

		# Check if the url is only a mailto: link
		#if 'mailto' == url[0:6]:
		#	return

		# Check if the url has already been processed
		if url in processed_pages:
			error_already_processed += 1
			print error_already_processed, '| Already processed url: ', url
			return

		# Check if the url represents a invalid file
		file_type = url[-4:]
		if '.pdf' == file_type or '.jpg' == file_type or 'jpeg' == file_type or '.png' == file_type:
			error_invalid_file += 1
			print error_invalid_file, '| Invalid file type: ', file_type, ' in url: ', url
			return

		# Increment page count and store the url in a list of processed urls to avoid it being processed again
		page_count += 1
		processed_pages.append(url)

		# Issue a GET request
		page = []
		try:
			page = requests.get(url, allow_redirects=True, timeout=2)
		except requests.exceptions.ConnectionError:
			error_connection_error += 1
			print error_connection_error, '| Connection error, url: ', url
			return
		except requests.exceptions.TooManyRedirects:
			error_too_many_redirects += 1
			print error_too_many_redirects, '| Too many redirects, url: ', url
			return
		except requests.exceptions.Timeout:
			error_timeout += 1
			print error_timeout, '| Request timed out, url: ', url
			return
		except KeyboardInterrupt:
			error_keyboard_interrupt += 1
			print error_keyboard_interrupt, '| KeyboardInterrupt'
			exit()

		# Use lxml to get a tree representation of the page binary
		tree = []
		try:
			tree = lxml.html.fromstring(page.content)
		except lxml.html.etree.ParserError:
			error_tree_parse += 1
			print error_tree_parse, '| Could not parse tree (HTML Error, url: ', url
			return
		except lxml.etree.XMLSyntaxError:
			error_tree_parse += 1
			print error_tree_parse, '| Could not parse tree (XML Error), url: ', url
			return

		# Parse out all hrefs from <a> tags
		urls = tree.xpath('//a/@href')

		# Initialize variables for logging urls
		num_urls = len(urls)

		# Print original findings
		print 'Page #: ', page_count;
		print 'Url: ', url
		print 'Url Count: ', len(urls)

		# Check if there are any urls to process
		if num_urls > 0:
			# Initialize variables for scoring of each url
			good_urls = []
			bad_urls = []

			# Score each url
			for url in urls:
				if score_string in url:
					good_urls.append(url)
				else:
					bad_urls.append(url)
			num_good_urls = len(good_urls)
			num_bad_urls = len(bad_urls)
			percent_good_urls = (float(num_good_urls * 100) / (num_good_urls + num_bad_urls))

			# Print scoring results
			print 'Good url count: ', num_good_urls
			print 'Bad url count:  ', num_bad_urls
			print 'Percent good urls:', int(percent_good_urls), '%'

			# Add score to list of scores
			page_scores.append(percent_good_urls)

			# Get length of page
			page_length = len(page.content)

			# Print length of page
			print 'Page Length: ', page_length

			# Add page length to list of page lengths
			page_lengths.append(page_length)

			# Compute average of metrics sofar
			score_average = average(page_scores)
			length_average = average(page_lengths)

			# Print average score
			print "Average score: ", int(score_average), '%'
			print "Average length: ", int(length_average)

			#Compute error count
			error_count = sum([error_already_processed, error_timeout, error_connection_error, error_too_many_redirects, error_tree_parse, error_missing_http, error_invalid_file, error_keyboard_interrupt])

			# Print error count
			print "Error Count: ", error_count

			# Increment the data file index
			data_file_index += 1

			# Check if its time to write to data file
			if data_file_index % data_file_schedule == 0:
				# Alert user
				print 'Writing to data file, index: ', data_file_index

				# Open data file
				data_file = open(data_file_path, 'a')
				data_file.write(str(data_file_index) + ',' + str(score_average) + ',' + str(length_average) + ',' + str(error_count))
				data_file.write('\n')
				data_file.close()

			# Repeat process for all good urls on page
			for url in good_urls:
				processPage(url)
			return
		else:
			return
	except KeyboardInterrupt:
		# Store error in err
		err = sys.exc_info()[0]

		# Print error
		print 'Error: ', err

		# Exit if prompted
		if str(err) == "<type 'exceptions.KeyboardInterrupt'>" or str(err) == "<type 'exceptions.SystemExit'>":
			exit()
		return
def average(list):
	return sum(list) / float(len(list))

# +---------+
# | Program |
# +---------+

main()
