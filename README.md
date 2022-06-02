# CarDealsML 

Data Science project about predicting car deal prices, with the intent to classify good used car deals comparing the predicted price with the actual price. 

For this project I made a Web Scraper for exploring the most recent car deals in the OLX website, I collected data about thoudands of car deals throughout many days, so I can use this data to train a regression Machine Learning algorithm. All the data is stored into a SQLite3 database, containing 3 tables, one for the car deal links, one of information received from each link, and one about fipe values. The process to extract the links from the website is done with the `requests` module and it's done really quickly because it extracts 50 links for each page, the process to extract the car information is done more slowly because it needs to visit each link one by one, but this process was accelerated using multiprocessing where all the threads of the processor is used separetely to retrieve data in parallel.

The database holds the raw information of more than 44000 car deals scraped from OLX, and executing `scrape.sh` is expected to retrieve 1100-1700 rows of information a day, and is really easy to integrate with crontab to schedule periodic data retrieval while unnassisted. Scraping data also stores at `logs/inference_num.log` the number of data collect that certain day, so this number can be used to inference always the last days's worth of data.

The bash script `inference.sh` is used to process and predict short volumes of data, size specified at `logs/inference_num.log`, configurations and parameters are not altered during inference, just transformed by the existing configuration and model.
