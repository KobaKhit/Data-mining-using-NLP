import json
from urllib.request import urlopen
from pprint import pprint
import json
import codecs
import time
from datetime import datetime

# to do 
#   - define nytclass field in the article object (use ["keywords"]["subject"],["nytddes"])

def save_json(df,filename="nytarticles.json"):
    # save df as {"data": df} json object
    filename = str(datetime.now().strftime("%Y-%m-%d")) + "-" + filename
    datajson = json.dumps({"data": df})
    with open(filename, "w") as jsonfile:
        jsonfile.write(datajson)

def get_data(TOPICS, NPAGES=None, BEGINDATE=None, ENDDATE=None, VERBOSE=0, LIMITS=False,
    FILENAME=None):
    # Downloads data about articles from nytimes.com
    #   - TOPICS = list of topics, ex.g. ["economics", "globale warming"]
    #   - NPAGES = list of integers which set the number of pages to download 
    #              for the topics, ex.g. [10, 15]. One page is equal to 10 articles.
    #   - BEGINDATE, ENDDATE - integer which limit the published date range, YYYYMMDD
    #   - VERBOSE = display all output
    #   - LIMITS = display number of pages available for each topic. If True then data
    #              is not downloaded.

    # start timer
    start_time = time.time()

    url = 'http://query.nytimes.com/svc/add/v1/sitesearch.json?' # starting url 

    if BEGINDATE is not None:
        # DATERANGE = "fromYYYYMMDDtoYYYYMMDD" or "fromYYYYMMDD"
        url = url + "&begin_date=" + str(BEGINDATE)

    if ENDDATE is not None:
        # DATERANGE = "fromYYYYMMDDtoYYYYMMDD" or "fromYYYYMMDD"
        url = url + "&end_date=" + str(ENDDATE)

    url = url+"&sort=desc&q="

    reader = codecs.getreader("utf-8")
    
    if NPAGES is not None:
        npages = NPAGES
    else:
        npages = list(map(lambda x: json.load(reader(urlopen(url + x)))["response"]["meta"]['hits'], TOPICS))

    if LIMITS ==  True:
        npages = list(map(lambda x: json.load(reader(urlopen(url + x)))["response"]["meta"]['hits'], TOPICS))
        print("Total number of pages available (each page is 10 articles): ")
        for i,k in zip(TOPICS,npages):
            print(i,": " ,k)
        return

    print("Topics: ", TOPICS)
    print("NPages: ", npages, '\n')
    print("Total documents: ", sum(npages)*10)
    print("Started download...")

    # get article data
    df = []
    progress = 0
    for i,k in zip(TOPICS,npages):

        URL = 'http://query.nytimes.com/svc/add/v1/sitesearch.json?q={}&pages={}' # starting url

        k = round(k,-1)
        for m in range(0,k):
            URL = URL.format(i,str(m+1))
            if VERBOSE > 0:
                print(URL," | " + str(m) + "/",k)

            response = urlopen(URL)
            data = json.load(reader(response))

            for j in range(0,len(data["response"]["docs"])):
                row = data["response"]["docs"][j]
                if row["pub_date"] is not None:
                    df.append(
                        {
                        "title": row["headline"]["main"],
                        "author": row["byline"].replace("By ", '') if row["byline"] is not None else "",
                        "snippet": row["snippet"],
                        "weburl": row["web_url"],
                        "abstract": row["abstract"],
                        "lead_paragraph": row["lead_paragraph"],                  
                        "section_name": row["section_name"],
                        "date_published": row["pub_date"],
                        "date_modified": row["updated"],
                        "nytclass": row["nytddes"],
                        "keywords": row['keywords'],
                        "user_topic": i
                        })

        progress += k
        print(i, "is done | " + str(progress) + "/" + str(sum(npages)))

    # save data as json
    if FILENAME is not None:
        save_json(df, FILENAME)

    print("\nDone in ", time.time()-start_time, "seconds")
    return(df)


def main():
    
    # topics = ['clinton','sex'] # list of topics for articles
    # npages = [10,10]
    # df = get_data(topics, npages, VERBOSE=1, FILENAME='test.json')
                
    # dump urls into a txt
    # weburl = [x['weburl'] for x in df]
    # with open('URList.txt', mode='wt') as myfile:
    #    myfile.write('\n'.join(weburl))
   
    # get available number of pages for each topic. Each page is equivalent to 10 articles
    # topics=['economics','politics','espionage','global+warming', 'clinton', 'sanders', 'guns', 
    #     'cancer', 'sex']
    # npages = [1500,1000,500,100,100,100,100,100,100]
    # # topics=['economics','politics']
    # get_data(topics, BEGINDATE = 20131213, LIMITS=True) # articles written since 2013-December-13
    # articles = get_data(TOPICS = topics, NPAGES = npages, BEGINDATE = 20131213)

    # topics = ["bernie+sanders","hillary+clinton","donald+trump"]
    # get_data(topics, LIMITS=True)

    # npages = [100,100,100]
    # articles = get_data(topics,npages, BEGINDATE = 20150101, FILENAME='politics.json')
    # print(articles[1])
    
    # save as json
    # datajson = json.dumps({"data": articles})
    # with open("snippetdata.json", "w") as jsonfile:
    #     jsonfile.write(datajson)
    return


if __name__ == "__main__":
    main()
