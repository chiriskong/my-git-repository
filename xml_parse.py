#!/usr/bin/python
#encoding=utf-8

import os, sys, imp, traceback, argparse

import copy
import time, datetime

import lxml
from lxml import etree
from io import StringIO, BytesIO

from lib import *

from Crawler import ConPool
import SiteInterface.InterfaceParse
import DataSchedule.Task, DataSchedule.Env

imp.reload(sys)
if sys.setdefaultencoding != None:
	sys.setdefaultencoding('utf8')

def usage():
	print "xml_parse"
	print
	print 'Usage: xml_parse.py -op[arg]'
	print '-s --start	DataTaskPath DataSiteCollectionPath		start the data collect task indicated by DataTaskPath file'
	print '-l --list	XmlPath									list all the data element of XmlPath'
	print
	print
	print 'Examples: '
	print 'xml_parse.py -s test.xml'
	sys.exit(0)

def parse_cmdline():
	t23 = None
	try:
		parse = argparse.ArgumentParser("tstsome")
		parse.add_argument("-l", dest="list", help="queued priority level", default=0)
		parse.add_argument("-s", dest="start", help="the path of virues files", required=False)

		parse.add_argument("-p", dest="info", action="store_true", default=False, help="get samples info")
		t23 = vars(parse.parse_args())
	except Exception as err:
		print str(err)

	return t23

class ISAXContentList():

	def __init__(self):
		self.countTab = 0

	def start(self, tag, attrib):
		tmFmt, nTab, self.countTab = "", self.countTab, self.countTab + 1

		while nTab != 0:
			tmFmt += "  "
			nTab -= 1
		tmFmt += "%s %r"

		print(tmFmt % (tag, dict(attrib)))

	def end(self, tag):
		tmFmt, nTab, self.countTab = "", self.countTab - 1, self.countTab - 1

		while nTab != 0:
			tmFmt += "  "
			nTab -= 1
		tmFmt += "%s"

		print(tmFmt % tag)

	def data(self, data):
		tmFmt, nTab = "", self.countTab

		while nTab != 0:
			tmFmt += "  "
			nTab -= 1
		tmFmt += '%s'

		if len(data.replace('\n','').replace('\t','').replace('\r','').replace(' ', '')):
			print(tmFmt % data)

	def comment(self, text):
		tmFmt, nTab = "", self.countTab

		while nTab != 0:
			tmFmt += "  "
			nTab -= 1
		tmFmt += '"%s"'

		print(tmFmt % text)

	def close(self):
		print("close")
		return "closed!"

def ListDataTask(dataTask_path):

	try:
		dataTask_parse = etree.XMLParser(target = ISAXContentList())
		dataTask_ret = etree.parse(dataTask_path, dataTask_parse)
	except Exception as err:
		print str(err)

class ISAXContentHandler():

	def __init__(self, obj):
		self.iObj = obj
		self.tag_stack = []

	def start(self, tag, attrib):
		self.tag_stack.append(tag)
		self.iObj = self.iObj.Parse((tag, attrib))

	def end(self, tag):
		tag_end = self.tag_stack.pop(-1)
		self.iObj = self.iObj.Parse((tag_end, None))

	def data(self, data):
	
		if len(data.replace('\n','').replace('\t','').replace('\r','')):
			tag= self.tag_stack[-1]
			self.iObj = self.iObj.Parse((tag, data))

	def comment(self, text):
		#print("comment %s" % text)
		pass

	def close(self):
		return self.iObj

def StartDataTask(dataTask_path, dataSite_path = 'SiteInterface/DataSiteInterface.xml'):

	try:
		parser = etree.XMLParser(target = ISAXContentHandler(SiteInterface.InterfaceParse.IDataSiteCollection()))
		iDataSiteCollection = etree.parse(dataSite_path, parser)

		taskEnv = DataSchedule.Env.CTaskEnv()
		crawler = ConPool.CNetMana()
		parser = etree.XMLParser(target = ISAXContentHandler(
            DataSchedule.Task.IDataTask(taskEnv, crawler, iDataSiteCollection)))
		iDataTask = etree.parse(dataTask_path, parser)

		iDataTask.Init()
		iDataTask.Run()

	except Exception as err:
		log.warn(traceback.format_exc())

def main():
	op_Task = ""
	dataTask_path = ""
	
	if not len(sys.argv[1:]):
		usage()
		
	try:
		#read the ommandline options
		opts, args = getopt.getopt(sys.argv[1:], 
			"hl:s:",
			["help", "list", "start"])
			
		for op,arg in opts:
			op = op.lower()
			if op in ("-h", "--help"):
				usage()
			elif op in ("-s", "--start"):
				op_Task, dataTask_path = "start", arg
			elif op in ("-l", "--list"):
				op_Task, dataTask_path = "list", arg
			else:
				assert False,"uphandled option"
				
		if op_Task == "start":
			startDataTask(dataTask_path)
		elif op_Task == "list":
			listDataTask(dataTask_path)
		else:
			assert False,"unknown info kind"
		
	except Exception as err:
		print str(err)
		usage()


if __name__ == "__main__":
	main()

