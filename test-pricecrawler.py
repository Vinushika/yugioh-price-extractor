import pricecrawler
##"Unit test" of sorts for pricecrawler

test1 = "Blue-Eyes White Dragon"
test2 = "Rescue Rabbit"

print (test1 + " should be $0.25")
print (pricecrawler.get_price(test1))
print (test2 + " should be $0.69")
print (pricecrawler.get_price(test2))
