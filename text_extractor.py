import numpy as np
import scipy.ndimage as ndimage
import scipy.misc as misc
import cv2
import tesseract
import matplotlib.pyplot as plt
import re
import sortedcontainers
import sqlite3
import levenshtein

CHOMP = 6 #how far we check for garbage in our strings
MAX_LED = 6 #maximum LED to check for against DB
LOW_THRESHOLD = 127
HIGH_THRESHOLD = 200
GARBAGE_PATTERN = "[^a-zA-Z- ]"
DB_WORD_LIST = None
def extract_text(input_filename):
	img= ndimage.imread(input_filename)
	#first, grayscale input
	grayimg = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
	#now take a high and a low threshold
	#above is for white/silver text
	ret,highthresh = cv2.threshold(grayimg,HIGH_THRESHOLD,255,cv2.THRESH_BINARY)
	highthresh = 255 - highthresh
	#low is for black text
	ret,lowthresh = cv2.threshold(grayimg,LOW_THRESHOLD,255,cv2.THRESH_BINARY)
	#tesseract wants cv2's specific Mat format, so make sure we have that
	#by saving and reloading
	misc.imsave("lowthresh.png",lowthresh)
	lowimg = cv2.cv.LoadImage("lowthresh.png",cv2.CV_LOAD_IMAGE_GRAYSCALE)
	misc.imsave("highthresh.png",highthresh)
	highimg = cv2.cv.LoadImage("highthresh.png",cv2.CV_LOAD_IMAGE_GRAYSCALE)
	#now start up tesseract
	api = tesseract.TessBaseAPI()
	#english since most cards are english words
	api.Init(".","eng",tesseract.OEM_DEFAULT)
	#Split by line so we can prune extra stuff before and after card name extracted
	api.SetPageSegMode(tesseract.PSM_SINGLE_WORD)
	api.SetPageSegMode(tesseract.PSM_AUTO)
	#now actually get the text
	tesseract.SetCvImage(lowimg,api)
	lowtext=api.GetUTF8Text()
	tesseract.SetCvImage(highimg,api)
	hightext= api.GetUTF8Text()
	#we have text now. Split it by newline for analysis
	lowlines = lowtext.split("\n")
	highlines = hightext.split("\n")
	#first do the lowlines because there's more black-text cards (monsters)
	#than any other cards, which increases our general accuracy slightly
	#now go through the lines, trim. If you examine too many, give up
	#because we want to avoid searching card text - only card NAME!
	linecounter = 0
	for line in lowlines:
		linecounter += 1
		if linecounter > 10:
			break
		result = clean_line_and_match(line)
		if result != -1:
			return result
	linecounter = 0
	#if we haven't found anything with the low threshold, try the high one
	for line in highlines:
		linecounter += 1
		if linecounter > 10:
			break
		result = clean_line_and_match(line)
		if result != -1:
			return result
	#well, we give up. Return nothing.
	return None #Maybe change this to a random card or do some probabilistic deal?

##Checks if a line of text is reasonable, then matches it against the DB
##and performs LED. If the string is garbage because it either doesn't agree
##with anything in the DB with LED <= 6, or has too many garbage characters,
##toss it and go to the next line.
def clean_line_and_match(line):
	#check if the first few characters are garbage
	first_chars = line[0:CHOMP]
	#if at least half of the first CHOMP characters are symbols, toss it
	goodchars = re.sub(GARBAGE_PATTERN,"",first_chars)
	if (CHOMP - len(goodchars)) / (float(CHOMP)) >= 0.5:
		return -1
	#then trim the line
	trimmed_line = line.strip()
	#if len is 0, skip it, it's a false positive
	if len(trimmed_line) == 0:
		return -1
	#if not, we have something we can work with, so take out garbage from the whole string
	#This doesn't actually change LED, since it would become insertion vs substitution anyway
	#it just makes checking for LED faster, which is good
	good_line = re.sub(GARBAGE_PATTERN,"",trimmed_line) #leave spaces in
	#now match against the DB
	minLEDMatch = levenshtein.get_min_LED_match(DB_WORD_LIST,MAX_LED,good_line)
	return minLEDMatch #-1 if no match, else the match

##fills up a sortedlist (from sortedcontainers)
##with all the names in the DB at db_file_name
def get_list_from_db(db_file_name):
	#first connect to the DB
	conn = sqlite3.connect(db_file_name)
	#now get cursor
	c = conn.cursor()
	#get all card names, add to sortedlist. The iterable means it's prepopulated!
	#sort by length of string, which we use to prune LED since a lot of card names are really long/short.
	all_names = c.execute("SELECT name FROM texts") #fetch from DB
	global DB_WORD_LIST
	DB_WORD_LIST = sortedcontainers.SortedListWithKey(iterable=[re.sub(GARBAGE_PATTERN,"",x[0].lower())\
			for x in all_names.fetchall()],load=100,key=lambda x: len(x))
	
#conf=api.MeanTextConf()
