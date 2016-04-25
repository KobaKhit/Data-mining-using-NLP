import json
from urllib.request import urlopen
from pprint import pprint
# import pandas as pd
import json
import codecs
import time

# to do 
#   - define nytclass field in the article object (use ["keywords"]["subject"],["nytddes"])

def get_data(TOPICS, NPAGES=None, BEGINDATE=None, ENDDATE=None, VERBOSE=0, LIMITS=False):
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
    print("\nDone in ", time.time()-start_time, "seconds")
    return(df)


def main():
    
    topics = ['clinton','sex'] # list of topics for articles
    npages = [10,10]
    df = get_data(topics, npages, VERBOSE=1)
                
    # dump urls into a txt
    weburl = [x['weburl'] for x in df]
    with open('URList.txt', mode='wt') as myfile:
        myfile.write('\n'.join(weburl))

    # save as json
    datajson = json.dumps({"data": df})
    with open("snippetdata.json", "w") as jsonfile:
        jsonfile.write(datajson)

    print(("Documents returned: ",len(weburl)))
    print("\nDone in ", time.time()-start_time)

if __name__ == "__main__":
    main()