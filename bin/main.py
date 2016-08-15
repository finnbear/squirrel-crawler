# +---------+
# | Imports |
# +---------+

import sys
from lxml import html
import requests

# +-----------+
# | Variables |
# +-----------+

# The first url to process
start_url = 'http://mit.edu'

# Urls will be judged based on whether they contain this string
score_string = 'mit.edu'

# A variable to track all the scores
scores = []

# A variable to track how many pages have been processed
page_count = 0

# A list to keep track of all the pages that have been processed
processed_pages = []

# +--------+
# | main() |
# +--------+

def main():
	# Start off the program by processing the starting url
	processPage(start_url)
	return

# +-----------+
# | Functions |
# +-----------+

def processPage(url):
	# Globals
	global processed_pages
	global page_count
	global score_string
	global scores
	
	try:
		# Check if the url is only a link to part of the same page
		if url[0] == '#':
			return
		# Check if the url starts with /
		if url[0] == '/':
			return
	
		# Chech if the url is only a mailto: link
		if 'mailto' == url[0:6]:
			return
		
		# Check if the url has already been processed
		if url in processed_pages:
			return
		
		# Check if the url represents a .pdf file
		if 'pdf' == url[-3:]:
			return
		
		# Print a header for the new page
		print '--------------------------------------------------------------'
	
		# Increment page count and store the url in a list of processed urls to avoid it being processed again
		page_count += 1
		processed_pages.append(url)

		# Issue a GET request
		try:
			page = requests.get(url, allow_redirects=True, timeout=1)
		except requests.exceptions.ConnectionError:
			print 'Connection error'
			return
		except requests.exceptions.TooManyRedirects:
			print 'Too many redirects'
			return
		except requests.exceptions.Timeout:
			print 'Request timed out'
			return
		except KeyboardInterrupt:
			print 'KeyboardInterrupt'
			exit()

		# Use lxml to get a tree representation of the page binary
		try:
			tree = html.fromstring(page.content)
		except lxml.etree.ParserError:
			print 'Could not parse'
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
			scores.append(percent_good_urls)

			# Compute average of scores sofar
			score_average = sum(scores) / float(len(scores))
			
			# Print average score
			print "Average score: ", int(score_average), '%'

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

# +---------+
# | Program |
# +---------+

main()
