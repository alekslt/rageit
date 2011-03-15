# -*- coding: utf-8 -*-
import sys, os
sys.path.append(os.path.dirname(__file__)) 
sys.path.append("/home/joink/public_html/rageit/irclog")
#sys.path.append(os.path.abspath("./irclog"))
sys.stdout = sys.stderr

#from postvarsel import *
from pysqlite2 import dbapi2 as sqlite
from math import *
import irclog.archive
import random
#connection = sqlite.connect('/usr/local/wsgi-scripts/post.db')
#cursor = connection.cursor()


rage = [ "clean.png", "EWBTE2.png", "FemaleHappy.png", "french.png", "Happy.png", "Hehehe.png", "loool.png", "redeyes.png", "Smile.png", "Stoned.png", "whyyyyyy.png",
"dude-come-on.png", "EWBTE.png", "FemaleRetarded.png", "grin.png", "hehehe.png", "herp.png", "pfftch.png", "Smile2.png", "SoMuchWin.png", "suspicious.png"]

pub_path = "~joink/rageit/avatars/rage"

def get_avatar():
	place = random.randint(0, len(rage)-1)
	return pub_path + "/" + rage[place]
##

def application(environ, start_response):
	status = '200 OK'
	output = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" /> 
<title>RageIt</title>
</head>
<body>
"""
#<link rel="stylesheet" type="text/css" media="screen" href=""http://toppe.no/~joink/rageit/style-screen.css">
	print >> environ['wsgi.errors'], "application debug #1"
	#trackIDs=["RB084737486HK"]
	#print "The ID is %s" % trackID


	story_raw = u"""10:01 <@DrSlem> hmmm, internettet mitt er usigelig treigt i dag
10:02 <@DrSlem> kanskje et forsiktig hint fra NGT om at regningen skal betales i morgen...
10:02 <@DrSlem> eller mest sannsynlig; en konspirasjon!
10:03 <@_neon_> DE ER DI RØDGRØNNE SOMM HAR SKYLLA
10:04 <@runehol> NÅ MÅ JENS Å CO GÅ
10:04 < vrakrav_> NISSELUER!
10:05 < Skuggen> JULEKALENDER!
10:11 < daven> POSTKASSE!"""

	story_raw = story_raw.encode("utf8")
	story_irc = irclog.parser.parse(story_raw.splitlines())

	story = []
	nick = ""
	speak = []
	for message in story_irc:
		if isinstance(message, irclog.messages.PublicMessage):
			message.__class__ = irclog.messages.PublicMessage
			if (nick == message.nick):
				speak.append(message.line)
			else:
				#if nick != "":
				#	output += "%s : %s\n" % (nick, speak)
				story.append([nick, speak])
				nick = message.nick
				speak = [message.line]
	grid_max_width = 4
	strip_length = len(story)
	
	if strip_length <= grid_max_width:
		grid_width = strip_length
		grid_length = 1
	else:
		grid_width = int(grid_max_width)
		grid_length = int(ceil(float(strip_length) / grid_max_width))

	output += "<p>strip_length = %d, grid_width = %d, grid_length = %d</p>\n" % (strip_length, grid_width, grid_length)
	output += "<table border=\"1\">\n"

	current_cell = 1
	for row in range(0, grid_length):
		output +="<tr>\n"
		for column in range(0, grid_width):
			speak = ""
			nick = ""
			output += "<td>\n"
			if current_cell < strip_length:
				speak = "<br/>\n".join(story[current_cell][1])
				nick = story[current_cell][0]	
				current_cell += 1

				output += "<p>%s</p>\n" % (speak)
				output += "<img src=\"%s\">\n" % (get_avatar())
				output += "<p>%s</p>\n" % (nick)
			output += "</td>\n"
		output +="</tr>\n"
	output += "</table>\n"


	output += "</body>\n</html>\n"
	output = output.encode("utf-8")
	response_headers = [	('Content-type', 'text/html'),
				('charset','utf-8'),
				('Content-Length', str(len(output)))]
	
	start_response(status, response_headers)

	return [output]

#from paste.evalexception.middleware import EvalException
#application = EvalException(application)

#from wsgiref import simple_server
#httpd = simple_server.WSGIServer(
#	('',8000),
#	simple_server.WSGIRequestHandler,
#	)
#httpd.set_app(application)
#httpd.serve_forever()
