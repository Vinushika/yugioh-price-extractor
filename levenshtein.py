from numpy import ndarray #easier to handle than 2D python lists

##Computes LED between two words. This is my code from Autocorrect,
##but translated to Python.
def levenshtein(word1,word2):
	ld_array = ndarray(shape=(len(word1)+1,len(word2)+1),dtype=int)
	for i in range(len(word1) + 1):
		ld_array[i][0] = i
	for j in range(len(word2) + 1):
		ld_array[0][j] = j
	##loop over both strings, compute distance
	for i in range(1,len(word1)+1):
		for j in range(1,len(word2)+1):
			if word1[i-1] == word2[j-1]:
				##characters match, don't increase D
				ld_array[i][j] = ld_array[i-1][j-1]
			else:
				#don't match, check deletion, insertion, substitution
				ld_array[i][j] = min(min(ld_array[i-1][j] + 1,ld_array[i][j-1]+1),ld_array[i-1][j-1]+1)
	return ld_array[len(word1)][len(word2)]

##Gets the match with the lowest LED in the list
##Since we don't really have a way of saying which
##suggestion is "better" than another, we get the first min.
##That said, a good approach could assume certain things about our string,
##such as for example the fact that the first two characters are usually correct
##so we can use those to not give spurious matches and increase accuracy a little.
def get_min_LED_match(sortedlist,maxLED,line):
	#First, lowercase our string just in case.
	check_line = line.lower()
	#then, find where we need to stop iterating through our list.
	#bisect finds the first position at which we can insert something
	#in the sorted list. Therefore, we find where we would insert a string
	#of the length of line + maxLED, which is where strings of length len(line)+maxLED start,
	#and completely ignore those. For example, if our string is "CYBER FA%CON", which is len 12,
	#we don't want to check "BLUE-EYES WHITE DRAGON", which is len 22, unless our LED is 10.
	stopping_word = " "*(len(check_line)+1) #neat Python trick. Doesn't work for all strings!
	stopping_point = sortedlist.bisect_left(stopping_word)
	#now iterate until you get to stopping_point
	minLED = maxLED + 1 #this may as well be Infinity
	minWord = -1 #fill this in
	for i in xrange(stopping_point): #xrange for less mem consumption since we're in Python < 3
		current_distance = levenshtein(line,sortedlist[i])
		if current_distance < minLED: #if less than the min, store it
			minLED = current_distance
			minWord = sortedlist[i]
	#will return -1 if we found nothing, or minWord if we did!
	return minWord

