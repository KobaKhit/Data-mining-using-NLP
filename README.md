# Data-mining-using-NLP

In this project we are looking for a possible use of the new york times articles as training data for Natural Language Processing projects.

We wrote New York Times scraper which uses BeautifulSoup to scrape the article pages. `scripts/webscrapers/nytscraper.py` works with python 2.7 and the other one guess.

We also wrote an alternative scraper `nytsnippetgetter.py` that does not parse the actual html pages to get the information. The difference is that instead of full article body we get just the `snippet`, `lead_paragraph` and `asbtract`. The advantage is that we obtain data even about articles that are available for subscribers only. Additionally, it is much quicker. We were able to download 20 thousand files in around 15 minutes.

# Code and Results

To see the code and nitty visualization of the LDA model topics check out [this notebook](http://nbviewer.jupyter.org/github/KobaKhit/Data-mining-using-NLP/blob/0a09bd8ddd7bb415d7275caedb92ff7eb7f8c4fe/draft/simple-intro.ipynb#topic=0&lambda=1&term=)

# To do's
  - [x] - Do a test example.

