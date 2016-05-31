
from urllib.request import urlopen
from pprint import pprint
import json
import codecs
import time, math
from datetime import datetime, date, timedelta


def perdelta(start, end, delta):
    # generate list of dates between BEGINDATE and ENDDATE delta time 
    # apart (hours, days, months, etc.)
    curr = start
    while curr < end:
        yield curr
        curr += delta

def scrape(response,topic):
    df = []
    data = response["response"]["docs"]
    if len(data) == 0:
        return([])
    else:
        for j in range(0,len(response["response"]["docs"])):
                # go through all articles in response
                    row = response["response"]["docs"][j]
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
                            "user_topic": topic
                            })
    return(df)

# to do 
#   - define nytclass field in the article object (use ["keywords"]["subject"],["nytddes"])

def save_json(df,filename="nytarticles.json"):
    # save df as {"data": df} json object
    filename = str(datetime.now().strftime("%Y-%m-%d")) + "-" + filename
    datajson = json.dumps({"data": df})
    with open(filename, "w") as jsonfile:
        jsonfile.write(datajson)


def get_data(TOPICS, NDOCS=None, BEGINDATE=None, ENDDATE=None, VERBOSE=0, LIMITS=False,
    FILENAME=None):
    # Downloads data about articles from nytimes.com
    #   - TOPICS = list of topics, ex.g. ["economics", "globale warming"]
    #   - NDOCS = list of integers which set the number of pages to download 
    #              for the topics, ex.g. [10, 15]. One page is equal to 10 articles.
    #   - BEGINDATE, ENDDATE - integer which limits the published date range, YYYYMMDD
    #   - VERBOSE = display all output
    #   - LIMITS = display number of pages available for each topic. If True then data
    #              is not downloaded.

    # start timer
    start_time = time.time()

    url = 'http://query.nytimes.com/svc/add/v1/sitesearch.json?' # starting url 

    if BEGINDATE is not None:
        # DATERANGE = "fromYYYYMMDDtoYYYYMMDD" or "fromYYYYMMDD"
        url = url + "&begin_date=" + str(BEGINDATE)
        BEGINDATE = datetime.strptime(str(BEGINDATE), "%Y%m%d").date()
    else:
        BEGINDATE = date.today()  - timedelta(days=1000)

    if ENDDATE is not None:
        # DATERANGE = "fromYYYYMMDDtoYYYYMMDD" or "fromYYYYMMDD"
        url = url + "&end_date=" + str(ENDDATE)
        ENDDATE = datetime.strptime(str(ENDDATE), "%Y%m%d").date()
    else:
        ENDDATE = date.today()    

    url = url+"&sort=desc&q="

    reader = codecs.getreader("utf-8")
    
    if NDOCS is not None and len(NDOCS)>1:
        npages = NDOCS
    elif NDOCS is not None and len(NDOCS)==1:
        npages = [NDOCS[0] for x in range(0,len(TOPICS))]
    else:
        npages = list(map(lambda x: json.load(reader(urlopen(url + x)))["response"]["meta"]['hits'], TOPICS))

    date_range = [x.strftime('%Y%m%d') for x in  perdelta(BEGINDATE,ENDDATE, timedelta(days=1))]
    date_range = date_range[::-1] # reverse list

    if LIMITS ==  True:
        npages = list(map(lambda x: json.load(reader(urlopen(url + x)))["response"]["meta"]['hits'], TOPICS))
        print("Total number of articles available: ", sum(npages))
        print("Date range: ", date_range[0],"->", date_range[-1],"\n")
        for i,k in zip(TOPICS,npages):
            print(i,": " ,k)
        return


    print("Topics: ", TOPICS)
    print("NPages: ", npages)
    print("Date range: ", date_range[0],"->", date_range[-1],"\n")
    print("Total documents: ", sum(npages))
    print("Started download...")

    # get article data
    df = []
    progress = 0

    URL = 'http://query.nytimes.com/svc/add/v1/sitesearch.json?sort=desc&begin_date={}&end_date={}&q={}' # starting url
    for i,k in zip(TOPICS,npages):
    # go through all topics
        counter = 0
        docs = 0
        date1 = date_range[0]


        topic_df = [] # articles for given iteration
        while (docs < k and date1 != date_range[-1]):
        # repeat while we get enough docs or cover date range
            # add dates one day away from each other to url
            # and go through all dates
            date1 = date_range[counter+1]
            nextdate = date_range[counter]
            counter += 1

            url = URL.format(date1, nextdate,i)
            
            response = urlopen(url)
            data = json.load(reader(response))

            counter2 = 0
            while len(scrape(data,i)) > 0 and docs < k and counter2 < 101:
            # repeat while next page contains 0 results or we get enough docs 
                urli = url + "&page=" + str(counter2) # add page to url
                counter2 += 1
                response = urlopen(urli)
                data = json.load(reader(response))
                for b in scrape(data,i):
                    # boo =  b['snippet'] in [x['snippet'] for x in topic_df]
                    # boo1 = b['user_topic'] in [x['user_topic'] for x in topic_df]
                    # if (not (boo and boo1)) or docs < k:
                    if docs < k:
                         docs += 1 # number of articles in page
                         topic_df.append(b)
                    else:
                        continue

                if VERBOSE > 0: print(urli," | " + str(docs) + "/",k,"|", progress, '/', sum(npages))      

                urli = url + "&page=" + str(counter2+1)
                response = urlopen(urli)
                data = json.load(reader(response))

                

        df += topic_df
        progress += k
        print(i, "is done | " + str(progress) + "/" + str(sum(npages)))

    # save data as json
    if FILENAME is not None:
        save_json(df, FILENAME)

    print('\nTotal documents returned: ', len(df))
    print("\nDone in ", time.time()-start_time, "seconds")
    return(df)


def main():
    
    topics=['space','sports','tech','politics','stocks'] # list of topics for articles
    get_data(topics, BEGINDATE=20160101, LIMITS=True)
    articles = get_data(topics, BEGINDATE=20160101, FILENAME='diff-topics.json', VERBOSE=1)
    
                
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
    # articles = get_data(topics,npages, BEGINDATE = 20131213, FILENAME='example.json', VERBOSE=1)

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
