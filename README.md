# CarDealsML

Data Science project about predicting car deal prices, with the intent to classify good used car deals comparing the predicted price with the actual price.
For this project I made a Web Scraper for exploring the most recent car deals in the OLX website, I collected data about thoudands of car deals throughout many days, so I can use this data to train a regression Machine Learning algorithm.

All the data is stored into a SQLite3 database, containing 2 tables, one for the car deal links, and one of information received from each link. The process to extract the links from the website is done with the `requests` module and it's done really quickly because it extracts 50 links for each page, the process to extract the car information is done more slowly because it needs to visit each link one by one, but this process was accelerated using multiprocessing where all the threads of the processor is used separetely to retrieve data.
