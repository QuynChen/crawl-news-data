# Import the necessary libraries
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd

def get_url(url):
  """get the url of pages based on the specific category contained in the <li class='has-child'> tag to prepare for crawling.
   The function returns a list of urls"""
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')

  links = []
  for news in soup.find_all('li', class_='has-child'):
    link = news.a['href']
    links.append(url+link)

  return links

url='https://dantri.com.vn'
links=get_url(url)
# print(links)

def scrape_news(stt, url, news_data):
  """scrape news data. The function takes in the starting article number, a specific url, and a dictionary to store the collected data. 
  The function returns the dictionary and the last article number."""
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  stt = stt

  # Find all urls of specific articles from the response of the given url. Then loop through each sub-url.
  for item in soup.find_all('article', class_='article-item'):
    sub_url = item.a['href']
    response = requests.get('https://dantri.com.vn'+sub_url)
    crawl = BeautifulSoup(response.text, 'html.parser')
    # loops through the content in the tag containing the content to be collected
    for news in crawl.find_all('div', class_='grid-container'):
      article_title = news.find('h1', class_='title-page detail').text.strip()
      article_content = news.find('div', class_='singular-content')
      author = news.find('div', class_='author-name')
      # Some articles do not have authors. Therefore, to ensure that the collected data is not missing, we ignore all articles without authors.
      if author is None:
        continue
      category = news.find('ul', class_='breadcrumbs').find('a').text.strip()
      posting_time = news.find('time', class_='author-time').text.strip()
      stt = stt + 1

      news_data['STT'].append(stt)
      news_data['Tiêu đề bài báo'].append(article_title)
      news_data['Nội dung bài báo'].append(article_content.text.strip())
      news_data['Tác giả'].append(author.text.strip())
      news_data['Thể loại'].append(category)
      news_data['Thời gian đăng bài'].append(posting_time)


  return news_data, stt

def scrape_multiple_pages(start, end, links, news_data, stt):
  """scrape data across multiple pages.
  The function receives a list of urls, starting page number, 
  ending page number and the order number of the first article to be stored in the data. 
  The function returns a dictionary containing the newly collected data"""

  for url in links:
    for page in range(start, end + 1):
      # replace the original url with a new url with the page number to crawl
      pattern = r'\.htm'
      replace = '/trang-'+str(page)+'.htm'
      new_url = re.sub(pattern, replace, url)
      print(f'Scraping page {page} on url: {new_url}')

      # Update dictionary and article numbers
      news_data, stt = scrape_news(stt, new_url, news_data)

      # Sleep for a random time between 1 and 3 seconds to avoid getting blocked
      time.sleep(random.uniform(1, 3))

  return news_data

def convert_to_csv(news_data):
  """convert data from dictionary to dataframe, then save data into csv file."""  
  # Convert data from dictionary to dataframe
  df_news = pd.DataFrame.from_dict(news_data)
  
  # Check data information and visualize
  df_news.info()
  df_news.head()
  
  # Store the first 5000 news data just collected, then save the data into a csv file.
  output = df_news.head(5000)
  output.to_csv('output.csv', index=False)

def main():
  # Create a dictionary to store news data
  news_data = {'STT': [], 'Tiêu đề bài báo': [], 'Nội dung bài báo': [], 'Tác giả': [], 'Thể loại': [], 'Thời gian đăng bài': []}
  news_data = scrape_multiple_pages(1,10, links, news_data, 0)
  convert_to_csv(news_data)

if __name__== '__main__':
  main()
