import requests
from bs4 import BeautifulSoup

#hardcode in the site we want to search, with a %s for the "searching slot"
get_url = "http://www.trollandtoad.com/products/search.php?search_words=%s&search_category=4736&search_order=price_asc"

def get_price(card_name):
	#first, trim the string just in case
	fixed_name = card_name.strip()
	#the site doesn't actually mind multiple spaces anywhere, so just
	#replace all spaces with +
	fixed_name = fixed_name.replace(" ","+")
	formatted_url = get_url % fixed_name
	#now actually get the page
	r = requests.get(formatted_url)
	if r.status_code == 200:
		#ok, we got the page, so let's open this in beautifulsoup
		soup = BeautifulSoup(r.text) #r.text is the raw HTML
		#get the first "price_text" one.
		all_prices = soup.find_all("td",class_="price_text")
		return all_prices[0].get_text()
	else:
		return -1
