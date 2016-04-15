import json
from urllib2 import urlopen
from urllib2 import Request
from pprint import pprint
# import pandas as pd

from bs4 import BeautifulSoup

# To do:
#   - articles have multiple pages, so scrape all to get full text 
#   - save data as csv
#   - remove duplicate urls from the list

def main():
    NPAGES = 2 # pages to scrape for article urls
    NARTICLE = 10 # number of articles to download

    # get article urls
    weburl = []
    for i in range(0,NPAGES):
        response = urlopen('http://query.nytimes.com/svc/add/v1/sitesearch.json?q=corporate%20espionage&page='+str(i)+'&facet=true', 'JSONOne.json')
        with open('JSONOne.json') as data_file:    
            data = json.load(data_file)
        
        for j in range(0,NARTICLE):
            weburl.append(data["response"]["docs"][j]["web_url"])
            
    # pprint(weburl)

    # dump urls into a txt
    with open('URList.txt', mode='wt') as myfile:
        myfile.write('\n'.join(weburl))

    #Cleaning url the list
    weburl1= []
    weburl1 = [s for s in weburl if "http://www.nytimes.com" in s]
    print("Articles to scape: ",len(weburl1))

    # Parse using BeautifulSoup
    # scrape nyt for articles
    dump = []
    for URL in weburl1:
        print str(weburl1.index(URL)+1) + "/" + str(len(weburl1)), URL

        r=urlopen(URL).read()
        soup = BeautifulSoup(r,"html.parser")

        # print (soup.prettify())

        title = soup.find("meta", { "name" : "hdl" })['content']
        description = soup.find("meta", { "name" : "description" })['content']
        author = soup.find("meta", { "name" : "byl" })['content'].replace("By ","")
        keywords = soup.find("meta", { "name" : "keywords" })['content']

        datePublished = soup.find("meta", { "itemprop" : "datePublished" })['content']
        dateModified = soup.find("meta", { "itemprop" : "dateModified" })['content']
        dateDisplay = soup.find("meta", { "name" : "DISPLAYDATE" })['content']
        
        nextPage = soup.find('a',{'title': 'Next Page'})

        body = soup.find("div", { "class" : "articleBody" }).find_all('p',{'itemprop': 'articleBody'})
        body = '\n'.join([w.get_text() for w in body])

        # if(nextPage):

        # append to dump list
        dump.append([title, description, author, keywords, datePublished, dateModified, dateDisplay, body])

    # join text elemets with lines as separators
    dump = [("\n"+"-"*10+"\n").join(w).encode('utf-8').strip() for w in dump]

    # save as a txt
    with open('Dump.txt', mode='wt') as myfile:
        myfile.write(("\n\n"+"*"*20+"\n\n").join(dump))

    print "\nDone"

if __name__ == "__main__":
    main()
