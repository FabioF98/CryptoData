# Cryptocurrency Reporting System

<p align = "center">
  <img
       width = "1000"
       height = "300"
       src = "./crypto.jpg"
       
  >
  </p>

## Introduction
This python script was created as a project for the Blockchain section of the Data Science course of Start2Impact, an italian startup (B Corp certified) which has been selected among the best ones in Europe in terms of education and social impact by the European Social Innovation Competition.

The main goal of this project was to create an automated reported that each day at a specific time, defined by the user, would retrieve information about cryptocurrencies. In particular the script must compute the following : 
1. The cryptocurrency with the largest volume (in $) of the last 24 hours.
2. The top and worst 10 cryptocurrencies (based on percentage increase in the last 24 hours).
3. The amount needed (in $) to buy one unit of the best 20 cryptocurrencies[^1]
4. The amount needed (in $) to but one unit of every cryptocurrency whose volume in the last 24 hours exceeded $76.000.000.
5. The net percentage gain or loss the user would have made having bought one of the best 20 cryptocurrencies of the previous day

## Project Structure
The first thing needed for the program to run was data from CoinMarketCap, and I obtained it using its API. Following the official documentation from the website I implemented a try/except clause inside the script to catch any error that might occur during the execution. The next step was the creation of a set of parameters in the form of dictionaries, that were needed as function arguments once I requested the data through the API. After that, I created another dictionary and I filled it with empty fields, which would be later filled with information from each of the cryptocurrency I was interested in. 
Once I had the data and a structured dictionary that could contain the values, I used a for loop to compute all that was required. The final step was to create a JSON file needed to store the information, I named the file with the name of the day it was run, since the script is automated, new JSON files need to be added everyday in order not to overwrite previously gathered data. The last function of the program uses the schedule module to run the program every day at a predefined time.



[^1]: Best 20 according to the ranking of CoinMarketCap, therefore sorted by capitalization
