from __future__ import division #by default older versions force integer division, so importing the correct division
import re 
import time
import praw
import random
import pymysql



#Main Fuction 
#Connects to reddit to get posts, calls functions to determine HL3, and posts comment
def main():

	#connect to the database
	db = pymysql.connect(host='hostaddress', port=3306, user='username', passwd='password', db='databasename')
	cursor = db.cursor()

	#Login to reddit
	r = praw.Reddit('HL3 confimred bot'
	                'Url: http:/www.bentheo.com')
	r.login('redditusername','password')

	#List of posts already commented on
	already_done = []

	#Main loop
	if True:
		#Set subreddit to browse
	    subreddit = r.get_subreddit('gaming')

	    #loop through each post in top posts
	    for submission in subreddit.get_hot(limit=30):
	    	#Get post title
	        op_text = submission.title.lower()
	        #Extract all numbers from post title
	        numonly = re.sub("[^0-9]", "", op_text)

	        #If the post hasn't been commented on already and contains numbers then  process
	        #Ignore the case when there is only 1 number, since the only time that matters is when it is 3, which is a boring post
	        #limited the input to 7 characters, since it slows down exponentially
	        if  len(numonly) > 1 and len(numonly) < 8:

	        	#check if this post has already been commented on
	        	query = "SELECT * FROM hl3bot WHERE PostID = \'" +  submission.id + "\'"
	        	found = cursor.execute(query)
	        	
	        	if not found:
		        	#get a formula that equals 3 out of numbers in title
		           	hl3f = HL3Forumula(numonly)
		           	#if a formula exist then process
		           	if len(hl3f) > 0:
		      			comment = []
		      			#Format post title to highlight number
		           		comment.append('**Post Title:** "' + GetRedditTitle(op_text) + '"')

		           		#List out all numbers with some explanation
		           		if re.sub("[^0-9]", "", hl3f) == numonly:
		           			comment.append("\n\nExtract the numbers from this post title and you get: " + numonly + '\n\n')
		           		else:
		           			comment.append("\n\nExtract and rearrange the numbers from the post title and you get: " + re.sub("[^0-9]", "", hl3f) + '\n\n')
		           		
		           		#Convert the formula to text for the comment
		           		comment.extend(FormulaToText(hl3f))

		           		#post comment
		           		submission.add_comment(''.join(comment))

		     			#add to database
		           		cursor.execute("""INSERT INTO hl3bot VALUES(%s)""", (submission.id))


#This is the implementation from itertools
#http://docs.python.org/2/library/itertools.html
#my server host doens't have this module installed so I had to implement
def combinations_with_replacement(iterable, r):
    # combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)

#Generates all permationts of input string
def all_perms(str):
    if len(str) <=1:
        yield str
    else:
        for perm in all_perms(str[1:]):
            for i in range(len(perm)+1):
                yield perm[:i] + str[0:1] + perm[i:]

#Finds a formula from a list of numbers that equals 3
#Generates multiple solutions (if they exist) and returns a random one
#if no solution exists returns an empty set
def HL3Forumula(numlist):
	digits = list(numlist)

	#get all permutations of numbers
	numbercombos = all_perms(numlist)

	#list of operators being processed
	operators = ['+','-','/','*']
	results = []

	if len(digits) > 0:
		#get all combinatinos of operators
		#the operators basically alternate with the numbers, so each string of operators needs to be one less than the number string
		operatorcombos =  list(combinations_with_replacement(operators,len(digits)-1))
		
		#Combine the number strings with the operator strings and evaluate
		for n in numbercombos:
			for o in operatorcombos:
				word = ""
				for i in range(len(n)):
					if i == len(n)-1:
						word += n[i]
					else:
						word += n[i] +  o[i] 
				#if the result of the formula found is 3, then store the 
				rword = 0
				#don't process cases where division by 0
				#previously was just letting this case error out and ignoring the error
				if word.find("/0") == -1:
					try:
						rword = float(eval(word))
					except ZeroDivisionError:
						pass
					if rword  == 3: results.append(word)
	
	#return a random result
	if len(results) > 0:
			#prioritize the results based on feedback on reddit
			#cases where their is 0 times a number of 0 divided by a number are low
			#cases where the numbers are in the original order of the post title are high
			#everything else is medium 
	        low = [x for x in results if  x.find('*0') > -1 or x.find('0*') > -1 or x.find('0/') > -1]
	        high = [x for x in results if re.sub("[^0-9]", "", x) == numlist and x not in low]
	        med = [x for x in results if  x not in high and x not in low]
	        if len(high) > 0:
	            return random.choice(high)
	        elif len(med) > 0:
	            return random.choice(med)
	        elif len(low) > 0:
	            return random.choice(low)
	        else:
	            return []
	else:
		return []

#Simple function to bold all the numbers in a the reddit post title
def GetRedditTitle(title):
	reddittitle = ""
	boldOn = False
	for c in title:
	    if c.isdigit() and not boldOn:
	        reddittitle = reddittitle + "**" + c
	        boldOn = True
	    elif not c.isdigit() and boldOn:
	        reddittitle = reddittitle + "**" + c
	        boldOn = False
	    else:
	        reddittitle = reddittitle  + c
	if title[-1].isdigit(): reddittitle = reddittitle + "**"  
	return reddittitle

#Given the position of the oprator and the formula, finds the two numbers that the operator applies to
#this really made me regret using strings for everything and nore a datatype that made more sense for a formula
#this is only needed when the formula is translated to text, not for the actual evaluation
def GetStartEnd(position, formula):
    loffset = position -1
    roffset = position + 1
    left = formula[:position]
    right = formula[position+1:]
    while loffset > 0 and (formula[loffset].isdigit() or formula[loffset] =='.'):
        loffset -= 1
    if loffset != 0: loffset += 1
    while roffset < len(formula) and  (formula[roffset].isdigit() or formula[roffset] =='.'):
        roffset += 1

    return list([loffset,roffset])

#Converts the formula to text to be posted in comment
def FormulaToText(formula):
	steps = []
	answers = []
	n = formula

	#Apply all division and multiplication to formula first. Division is processed first in eval()
	#Results are pushed in the order they are processed to the steps & answers array
	#If the formula is less than 3 characters long it means their is just one operation, or it is just 3
	if len(formula) > 3:
		#Same for both. Finals all cases of operator and does operation on those two numbers. the numbers/operator are stored in the steps and results in the answers
		#the operator/number combo is then replaces with the result in the formula
		#this is repeated until only addition and subtraction are left

		#Division
		while n.find('/') >= 0:
		    x = n.find('/')
		    offset = GetStartEnd(x,n)
		    sub = n[offset[0]:offset[1]]
		    subr = eval(sub)
		    if subr - int(subr) == 0: subr = str(int(subr))
		    steps.append(sub)
		    answers.append(subr)
		    n = n.replace(sub,str(subr))

		#Multiplication
		while n.find('*') >= 0:
		    x = n.find('*')
		    offset = GetStartEnd(x,n)
		    sub = n[offset[0]:offset[1]]
		    subr = eval(sub)
		    if subr - int(subr) == 0: subr = str(int(subr))
		    steps.append(sub)
		    answers.append(subr)
		    n = n.replace(sub,str(subr))


	#add whatever is left to the steps
	steps.append(n)
	ans = eval(n)

	#format integers, otherwise calculated numbers will be like "1.0"
	if ans - int(ans) == 0: ans = str(int(ans))
	answers.append(ans)

	output = []
	#turn operates into text and add to output
	#newlines added for reddit commment formatting
	#if the title only had 3 in it then there is no formula to post
	if formula != '3':
		while len(steps) > 0:
		    s = steps.pop(0)
		    a = answers.pop(0)
		    s = s.replace('+',' plus ')
		    s = s.replace('-', ' minus ')
		    s = s.replace('*', ' times ')
		    s = s.replace('/', ' divided by ')
		    output.append(str(s) + ' equals ' + str(a))
		    output.append('\n\n')

	output.append('\n\n\n\n**HALF-LIFE 3 CONFIRMED**')
	return output


#run main function
main()
