from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import sys
import time 

class UsageError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

def open_browser(url):
    #
    edge_options = Options()
    edge_options.use_chromium = True 
    edge_options.add_argument("start-maximized")
    edge_options.add_argument("inprivate")
    edge_options.add_argument('--mute-audio')
    edge_options.add_argument("--disable-notifications")
    edge_options.add_argument('--log-level=3')
    edge_options.add_experimental_option("detach", True)
    driver = webdriver.Edge(options=edge_options)
    
    driver.get(url)
    return driver 

def click_videos(driver):
    video_tab = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@class = "tab-title style-scope ytd-c4-tabbed-header-renderer"][contains(text(), "Videos")]')#'/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/tp-yt-app-header-layout/div/tp-yt-app-header/div[2]/tp-yt-app-toolbar/div/div/tp-yt-paper-tabs/div/div/tp-yt-paper-tab[2]/div')
        )
    )
    video_tab.click()
    
def filter_by_popular(driver):
    popular = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.XPATH,'/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-rich-grid-renderer/div[1]/ytd-feed-filter-chip-bar-renderer/div/div[3]/iron-selector/yt-chip-cloud-chip-renderer[2]/yt-formatted-string') 
            )
            )
    popular.click()

def parse_data(driver):
    """
    Parses data from the web page and returns lists of titles, views_s, and dates.

    Parameters:
        driver (webdriver): The web driver instance.

    Returns:
        tuple: A tuple containing three lists - titles, views_s, and dates.
    """
    
    titles = []
    views_s = []
    dates = []
    time.sleep(2)
    videos = driver.find_elements(By.XPATH, '//*[@id="contents"]/ytd-rich-item-renderer' )
    for video in videos:
        #print(video)
        
        title = video.find_element(By.XPATH, './/*[@id="video-title"]' ).text
        views = video.find_element(By.XPATH, './/*[@id="metadata-line"]/span[1]' ).text
        date = video.find_element(By.XPATH, './/*[@id="metadata-line"]/span[2]' ).text
        if title not in titles:
            titles.append(title)
            views_s.append(views)
            dates.append(date)

    #print( f'got {len(videos)} videos' )
    return titles, views_s, dates


def save_data(titles, views_s, dates, output_file_name):
    df = pd.DataFrame( {'titles':titles, 'views':views_s, 'dates':dates} )
    print('############')
    print(f'we have {len(df.index)} elements.')
    print('############')
    print('Here is the first 5 elements please check if that\'s correct.')
    print('############')

    print(df.head())

    print('############')
    print('Here is the last 5 elements please check if that\'s correct.')
    print('############')

    print(df.tail())


    df.to_csv(f'{output_file_name}', index=False)


def main(url, output_file_name= "output.csv"):
    print("#######################")
    print("Processing URL:", url)
    print("#######################")
    print(f"Scraping YouTube Channel:{url.split('@')[-1]}") 
    print("#######################")
    

    driver = open_browser(url)
    time.sleep(4)
    click_videos(driver)
    time.sleep(4)
    filter_by_popular(driver)
    last_height = driver.execute_script('return document.documentElement.scrollHeight;')
    
    titles = []
    views_s = []
    dates = []    
    while True:        
        driver.execute_script('window.scrollTo(0, document.documentElement.scrollHeight);')
        time.sleep(4)

        new_height = driver.execute_script('return document.documentElement.scrollHeight;')
        if new_height == last_height:
            title, views, date = parse_data(driver)
            titles.extend(title) 
            views_s.extend(views)
            dates.extend(date)
            break
        last_height = new_height 
        
    driver.quit()
    
    save_data(titles, views_s, dates, output_file_name)    
    

if __name__ == "__main__":    
    #url = "https://www.youtube.com/@johnnyharris"
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        raise UsageError(
                    "\n"
                    f"Usage should not be: python {sys.argv}"
                    "\n"
                    "Usage should be: python youtube_script.py \"https://www.youtube.com/@something\" \"your_file_name.csv\"\n"
                    "Note: if you didn't specify a file name, output.csv will be used as the new file name instead."
                    )

    print(f"sys.argv: {sys.argv}")
    url = sys.argv[1]
    if len(sys.argv) == 3:
        output_file_name = sys.argv[2]
        main(url, output_file_name)
    else:
        main(url)