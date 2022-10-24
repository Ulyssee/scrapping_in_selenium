from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import pandas as pd
import re
from urllib.parse import urljoin
from pyvirtualdisplay import Display
import gspread
import datetime


def selenium_setup():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)

    return driver


def display_setup():
    display = Display(visible=0, size=(1920,1080))
    display.start()
    return display

def scrap():
    display = display_setup()
    print('display started')
    driver = selenium_setup()
    print('headless driver started')
    try:
        url = 'https://francefintech.org/fft22-programme/'
        driver.get(url)
        # wait until the element you want is displayed
        time.sleep(5)
        driver.find_element(By.CSS_SELECTOR, ".et_pb_tab_6").click()
        time.sleep(5)
        #startup_list = driver.find_elements(By.CSS_SELECTOR, '.et-pb-active-slide .et_pb_tab_content ul')
        startup_list = driver.find_elements(By.XPATH, '//*[@id="post-42731"]/div/div/div/div[4]/div[2]/div/div/div/div[7]/div/ul/li')
        info_list = []
        # for startup_grid_elt in startup_list: # <- selenium.WebElement
        #     try:
        #         company_name = startup_grid_elt.find_element(By.CSS_SELECTOR, ' li').text
        #         print(company_name)
        #     except Exception as e:
        #         continue
        #     # wait until all elements needed are loaded
        #     info_list.append({
        #         'company_name': company_name,
        #     })
        for info in startup_list:
            info_list.append({
                'company_name': info.get_attribute('innerHTML'),
            })
        df = pd.DataFrame(info_list, columns=['company_name'])
        df.to_csv("info_list_francefintech.csv", index=False)
    except Exception as e:
        print(e)
        exit(84)
    finally:
        driver.quit()
        display.stop()



# google search to get linkedin profiles of CEOs.
def google_search():
    display = Display(visible=0, size=(1920,1080))
    display.start()
    driver = selenium_setup()
    try:
        urlgoogle = 'https://www.google.com/search?q=CEO'
        driver.get(urlgoogle)
        driver.save_screenshot('screenshot.png')
        time.sleep(5)
        info_list = pd.read_csv("info_list_francefintech.csv")
        linkedin_CEO_links = []
        linkedin_CEO_header = []

        # for i allant de 0 a 10 de la colonne company_name, on va   5 minutes entre chaque boucle for pour eviter le captcha de google. on va donc avancer de 10 en 10 dans la colonne company_name. 
        for i in range(0, len(info_list), 10):
            time.sleep(300)
            for company_name in info_list['company_name'][i:i+10].tolist():
                #changer de fake utilisateur à chaque fois pour éviter les blocages
                time.sleep(30)
                url = 'https://www.google.com/search?q=CEO+' + re.sub("[^a-zA-Z0-9]", " ", company_name) + '+site%3Alinkedin.com'
                print(company_name)
                driver.get(url)
                time.sleep(5)
                try: #cliquer le le bouton "Tout accepter" si il est présent
                    driver.find_element(By.CSS_SELECTOR, '#introAgreeButton').click()
                    driver.find_elements(By.XPATH,'//*[@id="L2AGLb"]').click()
                except Exception as e:
                    pass
                driver.save_screenshot('screenshot.png')
                first_linkedin_profile = driver.find_element(By.ID,'search').find_element(By.CSS_SELECTOR,"a[href*='linkedin.com']")
                link = first_linkedin_profile.get_attribute('href')
                header = first_linkedin_profile.find_element(By.TAG_NAME,'span').text
                print(i, datetime.datetime.now().time(), link , header)
                linkedin_CEO_links.append(link)
                linkedin_CEO_header.append(header)
                
        info_list["linkedin_CEO_link"] = linkedin_CEO_links
        info_list["linkedin_CEO_header"] = linkedin_CEO_header
        info_list.to_csv("info_list_francefintech.csv", index=False)

    except Exception as e:
        print(e)
        exit(84)
    finally:
        driver.quit()
        display.stop()


def main():
    print("\n\ndate of execution of script:")
    print(datetime.datetime.now())
    #scrap()
    google_search()
    exit(0)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
