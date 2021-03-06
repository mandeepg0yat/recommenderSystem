import pandas as pd
from bs4 import BeautifulSoup
import requests
import csv

moviesoriginal= pd.read_csv("./movies.csv",names=["num","name","genre"])
moviesScraped  = moviesoriginal
links= pd.read_csv("./links.csv",skiprows=1,names=["num","imdbId","tmdbId"])
imageLinks=[]
article=[]
linkslist = list(links["imdbId"])
error_movieId = []
with open("movies_info.csv", 'w') as movies_info:
    writer = csv.writer(movies_info)
    writer.writerows([["movieId", "imgLink", "summary"]])
    for i in range(resume,len(linkslist)):         # Will save the data after 10 scrap
        try:
            rl= str(linkslist[i]).zfill(7)
            page= requests.get("https://www.imdb.com/title/tt"+rl)
            soup = BeautifulSoup(page.content,'html.parser')
            rl= soup.find(class_="poster").find("a")
            image= rl.find("img")
            article= soup.find(class_="summary_text").get_text()
            article = article.strip()
            writer.writerows([[moviesoriginal["num"][i+1], image['src'], article]])
        except:
            error_movieId.append(moviesoriginal["num"][i+1])
movies_info.close()
