#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 16:30:13 2022

@author: peremoles
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 15:45:51 2022

@author: peremoles
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 10:24:01 2022

@author: peremoles
"""

import requests
import time
import string
import pandas as pd
from bs4 import BeautifulSoup

import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options




class fcbscraper():
    
    def __init__(self,url,sport):
            self.url = url
            self.sport = sport
       
    def __text_cleaner(self, text: str) -> str:
        '''Una funció que corregeix alguns detalls del text que scrapegem de la web del Barça. Retirem salts de línea,
            espais innecessaris, el símbol d'euro pels preus...'''
        text = text.replace('\n','')
        text = text.replace('€','')
        text = text.strip()
        return text
        
    def __date_cleaner(self,data: str) -> str:
        '''Una funció que converteix el text que llegim de la web del Barça en format estàndard de datetime de Python'''

        datasplitted = data.split()
        months_dict = {'ene.': 1,
               'feb.': 2,
               'mar.': 3,
               'abr.': 4,
               'may.': 5,
               'jun.': 6,
               'jul.': 7,
               'ago.': 8,
               'sep.': 9,
               'oct.': 10,
               'nov.': 11,
               'dic.': 12}
        if(months_dict[datasplitted[2]]>=11): year = 2022
        else: year = 2023
        return(datetime.datetime(year, months_dict[datasplitted[2]], int(datasplitted[1])))
        
    
    
    def scrap_matches_url(self) -> pd.DataFrame:
        '''Una funció que donada la pàgina de navegació d'una secció, per exemple futbol, retorna la llista de partits, horaris
        i accedeix a les pàgines d'entrades de cada partit
        '''
        
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content,'lxml')
        
        
        
        #DIFERENTS PARTITS 
        if self.sport == 'Futbol_masculi' or self.sport == 'Futbol_femeni':
            list_match_tag = soup.find_all("div", {"class":"fixture-result-list__fixture"})
        else:
            list_match_tag = soup.find_all("div", {"class":"fixture-result-list__fixture fixture-result-list__fixture--generic"})
        df = pd.DataFrame(columns = ['Esport','Rival','Dia','Sector', 'Preu'])
        i = 0
        for tag in list_match_tag:
            
            rival=tag.find("div",{"class":"fixture-info__name fixture-info__name--away"})
            dia=tag.find("div",{"class":"fixture-result-list__fixture-date"})
            ticket_url = self.__selenium_enter_ticket_page(i)
            prices_df = self.__scrap_prices(ticket_url)
            prices_df['Rival'] = self.__text_cleaner(rival.string)
            prices_df['Dia'] = self.__date_cleaner(self.__text_cleaner(dia.string))
            prices_df['Esport'] = self.sport
            df = pd.concat([df, prices_df])
            i = i+2
       
        return df
    
            
            
    
    def __selenium_enter_ticket_page(self, match_number: int) -> str:
        '''
        Aquesta funció utilitza Selenium per tal d'obtenir la url de la pàgina amb les entrades d'un cert partit en concret.
        Utilitzant només BeautifulSoup no evitava el control de robots de la web. Per tant, simulem clicks amb Selenium,
        i tornem la url final que ens interessa scrapejar
        
        Com a paràmetres tenim:
            url de la pàgina que accedim amb selenium (que té tots els partits)
            match_number indica el partit que volem obtenir les entrades
        '''
        DRIVER_PATH = '/home/peremoles/chromedriver'
        
        chrome_options = Options()
        driver = webdriver.Chrome(executable_path=DRIVER_PATH, options = chrome_options)
        driver.set_window_size(1440, 900)
        page = driver.get(self.url)
        time.sleep(3)
        try: 
            cookie = driver.find_element(By.ID, "fcbarcelona-button-accept")
            cookie.click()
        except: 
            print("No s'han pogut acceptar les cookies")
        if self.sport == 'Basket':
            try: 
                publi = driver.find_element(By.ID, "close_DFP_btn")
                publi.click()
            except: 
                print("O bé ja no existeix, o bé no s'ha pogut tancar el primer element publicitari")
            try:
                publi2 = driver.find_element(By.CLASS_NAME, "toast-box__close")
                publi2.click()
            except: print("O bé ja no existeix, o bé no s'ha pogut tancar el segon element publicitari")
        time.sleep(2)
        entrades = driver.find_elements(By.CLASS_NAME, "fixture-tickets__container")
        el = entrades[match_number].find_element_by_xpath(".//*")
        try:    
            el.click()
        except: 
            print("No hem pogut clickar el botó de les entrades del partit")
        if(self.sport == 'Futbol_femeni'):
            p = driver.current_window_handle
            time.sleep(2)    
            chwd = driver.window_handles
    
            for w in chwd:
                if(w!=p):
                    driver.switch_to.window(w)
        time.sleep(3)
        ticket_url = driver.current_url
        if self.sport == 'Basket' or self.sport == 'Futbol_masculi' or self.sport == 'Futbol_femeni': 
            time.sleep(3)
            try:
                publi = driver.find_elements(By.CLASS_NAME, "toast-box__header-actions")
                close = publi[0].find_elements_by_xpath(".//*")
                close[1].click()
            except: print('No hi havia publicitat per tancar')
            time.sleep(2)
            try: 
                entrades2 = driver.find_elements(By.CLASS_NAME, "ticket-promo__ctas")
                entrades2child = entrades2[0].find_elements_by_xpath(".//*")
                entrades2child[0].click()
                time.sleep(2)
                if self.sport == 'Basket' or self.sport == 'Futbol_femeni':
                    p = driver.current_window_handle
                    time.sleep(2)
                    chwd = driver.window_handles
            
                    for w in chwd:
                    #switch focus to child window
                        if(w!=p):
                            driver.switch_to.window(w)
            except: print("No s'ha clickat el segon botó d'entrades")
            
            ticket_url = driver.current_url
       

        driver.close()
        time.sleep(1)
        return ticket_url
        
    
    def __scrap_prices(self,ticket_url: str) -> pd.DataFrame:
        '''Una funció que donada  la url d'una pàgina de la web del Barça amb els preus de les entrades als diferents sectors
        de l'estadi, retorna un dataframe de Pandas amb els diferents preus i sectors'''
        DRIVER_PATH = '/home/peremoles/chromedriver'
        chrome_options = Options()
    
        chrome_options.add_argument("headless")    
        driver = webdriver.Chrome(executable_path=DRIVER_PATH, options = chrome_options)
        driver.set_window_size(1440, 900)
        driver.get(ticket_url)
        time.sleep(3)
        
        try: 
                cookie = driver.find_element(By.ID, "fcbarcelona-button-accept")
                cookie.click()
        except: 
                print("No s'han pogut acceptar les cookies")
                
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        seats = soup.find_all("div", {"class":"asiento"})
        if(len(seats) == 0): 
            seats = soup.find_all("span", {"class":"zone-name ng-binding"})
        prices = soup.find_all("span", {"class": "final_price"})
        if(len(prices)==0):
            prices = soup.find_all("span", {"class": "zoneInfo price ng-binding"})
        if(len(prices)==0):
              prices = soup.find_all("span", {"class": "zoneInfo price pl-1 ng-binding"})
  
        price_list = []
        seat_list = []
                
            #DINS DE LA PÀGINA D'ENTRADES TREIEM SEIENTS I PREUS
                
        for seat in seats:
            for child in seat.children:
                if(child.string!=None):
                    seat_list.append(self.__text_cleaner(child.string))
        seat_list = [x for x in seat_list if x.strip()]
        for price in prices:
            price_list.append(self.__text_cleaner(price.string))
        driver.close()
        time.sleep(1)
        return pd.DataFrame(list(zip(seat_list,price_list)), columns = ['Sector','Preu'])



