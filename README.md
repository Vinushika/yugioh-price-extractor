# yugioh-price-extractor
Extracts the name of a Yugioh card from a picture, and fetches the lowest price from online card shops.

Change the global variables at the top of the generateEigenCards.py and getEigenResults.py scripts, then run them in that order to first generate the eigencards and vector data, and then use that on the input card to get an ID result. Our database is in the cardDB directory, while right now we're using the testDB directory as our input set. With these ~830 cards, eigenCard generation takes a little under 5 minutes. Getting the result is still blazingly fast as long as we load the preprocessed koala MAP outline, rather than use the classifier to get the binary bounding box in getEigenResult.py. Right now the Koala isn't being properly identified.
TODO: Reconstruct koala image from linear combination of eigencards and scalars, and see how well that works. 

----
The OCR stuff is also here somewhere but I'm not sure where
---


