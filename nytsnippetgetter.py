
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

def init(TOPICS=None, NDOCS = None, BEGINDATE=None, ENDDATE=None):
    
    url = 'http://query.nytimes.com/svc/add/v1/sitesearch.json?&sort=desc' # starting url 
    urls = [] # list of links to query
        
    # add query parameter
    if TOPICS is not None: urls = [[url + "&q=" + x] for x in TOPICS]
    else: urls, TOPICS = [[url]], [""]
    
    # add dates to links
    urlh = urls
    if BEGINDATE is not None:
        # DATERANGE = "fromYYYYMMDDtoYYYYMMDD" or "fromYYYYMMDD"
        urlh = [[x + "&begin_date=" + str(BEGINDATE) for x in l] for l in urls]
        BEGINDATE = datetime.strptime(str(BEGINDATE), "%Y%m%d").date()
    else:
        BEGINDATE = date.today()  - timedelta(days=30)

    if ENDDATE is not None:
        # DATERANGE = "fromYYYYMMDDtoYYYYMMDD" or "fromYYYYMMDD"
        urlh = [[x + "&end_date=" + str(ENDDATE) for x in l] for l in urls]
        ENDDATE = datetime.strptime(str(ENDDATE), "%Y%m%d").date()
    else:
        ENDDATE = date.today()   
    
    if ENDDATE <= BEGINDATE: BEGINDATE = ENDDATE-timedelta(days=30)
    
    # get number of articles from nyt server
    reader = codecs.getreader("utf-8")
    if NDOCS is not None and len(NDOCS)>1:
        pass
    elif NDOCS is not None and len(NDOCS)==1:
        NDOCS = [NDOCS[0] for x in range(0,len(TOPICS))]
    else:
        NDOCS = list(map(lambda x: json.load(reader(urlopen(x)))["response"]["meta"]['hits'],
                          [x for l in urlh for x in l]))
        
    # add dates
    date_range = [x.strftime('%Y%m%d') for x in  perdelta(BEGINDATE,ENDDATE, timedelta(days=1))]
    date_range = date_range[::-1] # reverse list
    
    BEGINDATE = str(BEGINDATE)
    ENDDATE = str(ENDDATE)
    
    # generate links 
    urlss=[]
    for l in urls:
        for u in l:
            ls = list(map(lambda k: u + "&begin_date=" + date_range[k] + "&end_date=" + date_range[k-1],
                range(1,len(date_range))))
            urlss.append(ls)
    
    return(urlss,NDOCS, TOPICS, BEGINDATE, ENDDATE)
    
    
def get_data(TOPICS=None, NDOCS=None, BEGINDATE=None, ENDDATE=None, VERBOSE=0, LIMITS=False,
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
    urls, NDOCS, TOPICS, BEGINDATE, ENDDATE = init(TOPICS, NDOCS, BEGINDATE, ENDDATE)
    
    print("Topics: ", TOPICS)
    print("Documents: ", NDOCS)
    print("Date range: ", BEGINDATE,"->", ENDDATE,"\n")
    print("Total documents: ", sum(NDOCS))
    
    if LIMITS is not True: print("Started download...")
    else: return
    
    reader = codecs.getreader("utf-8")
    
    df = []
    for i,l in enumerate(urls):
        docs = 0   
        for url in l:
            # if we get enough documents stop loop
            if docs == NDOCS[i]:
                break
                
            page = 0
            page_limit = 0
            progress = 0
            
            urli = url + "&page=" + str(page) # add page to url
            response = urlopen(urli)
            data = scrape(json.load(reader(response)), TOPICS[i])
             
            while len(data) > 0 and docs < NDOCS[i] and page_limit < 101:
            # repeat until next page contains 0 results or we get enough docs 

                
                for b in data: 
                    if docs < NDOCS[i]:
                        df.append(b); 
                        docs += 1 # number of articles in page
                    else: continue
                            

                
                if VERBOSE > 0: print(urli,
                                      " | " + str(docs) + "/",NDOCS[i],
                                      "|", 
                                      progress, '/', 
                                      sum(NDOCS))
                
                page += 1
                page_limit += 1
                progress += 1
                
                urli = url + "&page=" + str(page) # add page to url
                response = urlopen(urli)
                data = scrape(json.load(reader(response)), TOPICS[i])
            
        print(TOPICS[i], "is done | " + str(NDOCS[i]) + "/" + str(sum(NDOCS)))

    # save data as json
    if FILENAME is not None: save_json(df, FILENAME)

    print('\nTotal documents returned: ', len(df))
    print('\nTotal unique documents: ', len(set([x['snippet'] for x in df])))
    print("\nDone in ", time.time()-start_time, "seconds")
    return(df)


def main():
                                                
    topics=['donald+trump', 'hillary'] # list of topics for articles
    ndocs = [20]
    df = articles = get_data(None, BEGINDATE=20140101, 
                             VERBOSE=1, FILENAME='erwf.json', LIMITS = True)
    
    
    return
                
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
