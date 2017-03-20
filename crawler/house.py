import requests
#import json
import bs4
#from bs4 import NavigableString
#from bs4 import UnicodeDammit
from bs4.element import Tag
import time
import re
import json
import random
from datetime import datetime, timedelta

def extractNumber(text):
    return re.sub('[^0-9\.]', '', text)

HistoryPattern = "{0}{1}\t{2}\n"

class house(object):
    """
    fetch information from trademe house
    """
    #

    def houseFigure(self, block, className):
        result = ''
        area = block.find(attrs={"class":className})
        if area == None:
            return result
        
        area = area.find(attrs={"class": 'icon-attribute-number'})
        if area == None:
            return result
        result = area.string
        return result
        
    def exist(self, id):
        response = requests.get(self.api + "/api/houses/" + id)
        if not response.ok:
            return response.ok
        
        json = response.json()
        json["LastVisit"] = datetime.now().isoformat()
        response = requests.put(self.api + "/api/houses/" + id, data = json)
        return True

    def updatePrice(self, id, price):
        response = requests.get(self.api + "/api/houses/" + id)
        if not response.ok:
            return response.ok
        
        json = response.json()
        json["LastVisit"] = datetime.now().isoformat()

        if json["Price"].lower() == price.lower():
            response = requests.put(self.api + "/api/houses/" + id, data = json)
            return True
        
        #if json["History"] == None:
        #    json["History"] = ""
        #json["History"] = HistoryPattern.format(json["History"], datetime.now().isoformat(), json["Price"])
        json.pop('HouseHistories', None)
        json["Price"] = price
        response = requests.put(self.api + "/api/houses/" + id, data = json)
        if not response.ok:
            print("update House failed " + id)

        #add history instead
        history = {}
        history['houseid']= id
        history['ChangedAt'] = json["LastVisit"] 
        history['Price'] = price

        response = requests.post(self.api + "/api/househistories", json = history)

        return True

    def parseDate(self, txt):
        result = datetime.now()
        if txt.lower() == 'today':
            return result 
        if txt.lower() == 'yesterday':
            result +=  timedelta(days=-1)
            return result
        comma = txt.find(',')
        if comma != -1:
            txt = txt[comma + 1:]
        comma = txt.find(' on')
        if comma != -1:
            txt = txt[comma + 3:]
        txt = txt + " " + str(result.year)
        result = result.strptime(txt.strip(), "%d %b %Y") 
        return result

    def fetch(self, pagenumber):
        url0 = self.url + str(pagenumber)
        fresp = requests.get(url0)
        fsoup = bs4.BeautifulSoup(fresp.text, "lxml")
        t = fsoup.find("ul", {"id":"ListViewList"})

        idre = re.compile('pid')
        for li in t.children:
            if not isinstance(li, Tag):
                continue
            try:
                #data to post
                house = {}
                #list['Highlight'] = ' '.join(li.attrs['class'])
                feature = ''
                if 'feature' in li.attrs['class']:
                    feature += ' feature'
                if 'highlight' in li.attrs['class']:
                    feature += ' highlight'
                house['Feature'] = feature

                preview = li.find(attrs={"class": 'list-view-photo-container'})
                listurl = preview.find('a').attrs['href']
                listingImage = preview.find('img').attrs['src']
                house['Url'] = listurl
                house['ImageUrl'] = listingImage
                house['HouseId'] = re.findall('-(\d*)\.htm',listurl)[0]
 
                titleCol = li.find(attrs={"class": 'list-view-details-container'})
                house['Price'] = titleCol.find(attrs={"class": 'list-view-card-price'}).contents[0].string

                #if exists, update price and continue
                if self.updatePrice(house['HouseId'], house['Price']):
                    #print('\t-' + house['HouseId'])
                    continue

                print('\t' + house['HouseId'])

                listingTitle = titleCol.find(attrs={"class": 'list-view-card-title'})
                house['Title'] = listingTitle.find("a").string
                house['Address'] = titleCol.find(attrs={"class": 'property-card-subtitle'}).string

                others = titleCol.find(attrs={"class": 'list-view-attribute-details'})

                house['Land'] = self.houseFigure(others, 'property-card-land-area')
                house['Room'] = self.houseFigure(others, 'property-card-bedrooms')
                house['BathRoom'] = self.houseFigure(others, 'property-card-bathrooms')
                
                #listedAt = titleCol.find(attrs={"class":
                #'list-view-listed-date'}).string.replace('Listed ','')
                #house['ListedAt'] = self.parseDate(listedAt).isoformat()
                self.detail(house)

                #print(json.dumps(house))
                response = requests.post(self.api + "/api/houses", json = house)
                if not response.ok:
                    print(response.status_code)

                #add history
                history = {}
                history['houseid']= house['HouseId']
                history['ChangedAt'] =  datetime.now().isoformat()
                history['Price'] = house['Price']

                response = requests.post(self.api + "/api/househistories", json = history)

            except BaseException as ex:
                print(ex)

        return

    def detail(self, house):
        url = "http://www.trademe.co.nz" + house['Url']
        sp = bs4.BeautifulSoup(requests.get(url).text, "lxml")
        content = sp.find("div", {"id":"mainContent"})

        titleTime = content.find("li", {"id":"ListingTitle_titleTime"}).string
        now = datetime.now()
        ListedAt = now.strptime(titleTime.replace("Listed: ",""), "%a %d %b, %I:%M %p")
        house['ListedAt'] = datetime(now.year, ListedAt.month, ListedAt.day, ListedAt.hour, ListedAt.minute).isoformat()

        attrs = content.find("table", {"id":"ListingAttributes"})
        for th in attrs.find_all("th"):
            #Auction date
            if "Price" in th.string and "auction" in house['Price']:
                txt = th.next_sibling.next_sibling.string.strip()
                Auction = self.parseDate(txt)
                if Auction < ListedAt:
                    Auction = Auction + timedelta(days=365)
                house['Auction'] = Auction.isoformat()
            if "Property type" in th.string:
                txt = th.next_sibling.next_sibling.string.strip()
                house['PropertyType'] = txt
        
        house["Wording"] = "\r\n".join(content.find("div", {"class":"ListingDescription"}).strings)

        agent = content.find("div", {"id":"ClassifiedActions_AgentDetails"})
        if agent == None:
            return

        house["Agent"] = agent.text.strip()
        return

    def getSession(self):
        sp = bs4.BeautifulSoup(requests.get("http://www.trademe.co.nz/browse/property/regionlistings.aspx?sort_order=expiry_desc&cid=3399&134=1&216=0&216=0&217=0&217=0&v=list").text, "lxml")
        content = sp.find("table", {"id":"PagingFooter"})
        keyurl = content.find("a").attrs['href']
        start = keyurl.find("key=")
        if start == -1:
            return None

        keyurl = keyurl[start + 4:]
        end = keyurl.find("&")
        if end == -1:
            return keyurl

        return keyurl[:end]

    def __init__(self, **kwargs):
        self.api = 'http://localhost/bo'
        self.url = 'http://www.trademe.co.nz/browse/categoryattributesearchresults.aspx?cid=5748&search=1&v=list&134=1&nofilters=1&originalsidebar=1&key={0}&sort_order=prop_default&rptpath=350-5748-3399-&page='
        self.url = self.url.format(self.getSession())
        return

def initmaster():


    return

def load():
    tm = house()
    for page in range(1,150):
        print(page)
        tm.fetch(page)

def test():
    tm = house()
    print(tm.updatePrice("366007847", "1"))

#test()
load()
