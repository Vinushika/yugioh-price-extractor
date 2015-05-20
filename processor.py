import text_extractor
import argparse
import pricecrawler

##first a fancy CLI engine
parser = argparse.ArgumentParser(description="Gets price of the card in your image!")
parser.add_argument("input_file", metavar="input", type=str, help="The path to your image file.")
values = vars(parser.parse_args())
input_file = values['input_file']
##now load the DB (important! maybe add as an argument?) and parse the image
text_extractor.get_list_from_db("cards.cdb")
card_name = text_extractor.extract_text(input_file)
##If we don't have a card name, make sure we check for that
##and fetch price
if card_name != None:
	price = pricecrawler.get_price(card_name)
	print "Your card is %s and can be bought for %s at Trollandtoad.com" % (card_name, price)
else:
	print "We couldn't get your card. Maybe try taking another picture?"
