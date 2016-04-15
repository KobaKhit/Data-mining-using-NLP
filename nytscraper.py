import json
from urllib2 import urlopen
from urllib2 import Request
from pprint import pprint
# import pandas as pd
import json

from bs4 import BeautifulSoup

# To do:
#   - articles have multiple pages, so scrape all to get full text 

def scrape(urllist):
    # Scrape new york time articles given a list of urls
    # - input:
    #   list of urls
    # - output:
    #   list of objects

    dump = []
    count = 1
    for URL in urllist:
        try:
            print str(count) + "/" + str(len(urllist)), URL

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
            dump.append(
                {"title": title, 
                "description": description, 
                "author": author, 
                "keywords": keywords, 
                "datePublished": datePublished, 
                "dateModified": dateModified,
                "dateDisplay": dateDisplay, 
                "body": body})

            count += 1
        except:
            print("this article is private")
            count += 1
            pass

    return(dump)

def main():
    NPAGES = 1 # pages to scrape for article urls

    # get article urls
    weburl = []
    for i in range(0,NPAGES):
        response = urlopen('http://query.nytimes.com/svc/add/v1/sitesearch.json?q=corporate%20espionage&page='+str(i)+'&facet=true')
        data = json.load(response)

        # print(len(data["response"]["docs"]))

        for j in range(0,len(data["response"]["docs"])):
            print(data["response"]["docs"][j]["web_url"])
            weburl.append(data["response"]["docs"][j]["web_url"])
        

    #Cleaning url the list
    weburl  = [s for s in weburl if "http://www.nytimes.com" in s]
    print("Articles to scape: ",len(weburl),"\n")

    # Parse using BeautifulSoup
    # scrape nyt for articles
    dump = scrape(weburl)

     # save as json
    datajson = json.dumps({"data": dump})
    with open("data.json", "w") as jsonfile:
        jsonfile.write(datajson)

    print("\nArticles scraped: ", len(dump))
    print("\nDone")

if __name__ == "__main__":
    main()