# Local Imports
import config

def console_log(text):
	if config.output_log:
		print("Log     | " + text)

def console_warning(text):
	if config.output_warning:
		print("Warning | " + text)

def console_error(text):
	if config.output_error:
		print("Error   | " + text)

def datafile_init(fields):
	line = ""
	for field in fields:
		line += field + ", "
	line = line[:-2]
	line += "\n"
	data_file = open(config.datafile_path, 'w')
	data_file.truncate()
	data_file.write(line)
	data_file.close()

def datafile_log(fields):
	line = ""
	for field in fields:
		line += str(field) + ", "
	line = line[:-2]
	line += "\n"
	data_file = open(config.datafile_path, 'a')
	data_file.write(line)
	data_file.close()



