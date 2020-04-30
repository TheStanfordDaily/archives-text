'''
Code ported from `cloudsearch/cloudsearch-process-and-upload.py`
'''

import os
import re
import json
from multiprocessing import Pool
import time

ARCHIVES_TEXT_PATH = './'

# for multiprocessing; set this to a reasonable number.
POOL_SIZE = 123

class Logger:
    def __init__(self, path, basename):
        self.fullpath = path + basename + '.log'
        f = open(self.fullpath, 'w')
        f.write("logger start\n")
        f.close()

    def log(self, message):
        f = open(self.fullpath, 'a') # open and close here for live updates
        f.write(message + "\n")
        f.close()

    def get_fullpath(self):
        return self.fullpath

    def __del__(self):
        f = open(self.fullpath, 'a') # open and close here for live updates
        f.write("logger done\n")
        f.close()
        
class ArchivesTextProcessor:
    def __init__(self, base_path, startYear, endYear):
        self.base_path = base_path
        self.startYear = startYear
        self.endYear = endYear
        self.is_done = False

        # initialize some data
        self.years_left = list(range(startYear, endYear))
        self.currentYear = None
        self.move_to_next_year()
        self.months_left_in_year = None
        self.set_months_left_in_year()
        self.currentMonth = None
        self.move_to_next_month()
        self.days_left_in_month = None
        self.set_days_left_in_month()
        self.currentDay = None
        self.move_to_next_day()
        self.articles_left_in_day = None
        self.set_articles_left_in_day()
        self.currentArticle = None
        self.move_to_next_article()

    '''
    the following are functions to help us iterate through the files in archives-text
    '''

    def get_current_path(self, level):
        if(level == 'year'):
            return self.base_path + str(self.currentYear).zfill(4) + '/'
        elif(level == 'month'):
            return self.base_path + str(self.currentYear).zfill(4) + '/' + str(self.currentMonth).zfill(2) + '/'
        elif(level == 'day'):
            return self.base_path + str(self.currentYear).zfill(4) + '/' + str(self.currentMonth).zfill(2) + '/' + str(self.currentDay).zfill(2) + '/'
        elif(level == 'article'):
            return self.base_path + str(self.currentYear).zfill(4) + '/' + str(self.currentMonth).zfill(2) + '/' + str(self.currentDay).zfill(2) + '/' + self.currentArticle


    def set_months_left_in_year(self):
        months = os.listdir(self.get_current_path('year'))
        filtered_months = []
        for i in range(0, len(months)):
            try:
                filtered_months.append(int(months[i]))
            except:
                continue
        filtered_months.sort()
        self.months_left_in_year = filtered_months

    def set_days_left_in_month(self):
        days = os.listdir(self.get_current_path('month'))
        filtered_days = []
        for i in range(0, len(days)):
            try:
                filtered_days.append(int(days[i]))
            except:
                continue
        filtered_days.sort()
        self.days_left_in_month = filtered_days

    def set_articles_left_in_day(self):
        articles = os.listdir(self.get_current_path('day'))
        filtered_articles = []
        for i in range(0, len(articles)):
            try:
                filtered_articles.append(articles[i])
            except:
                continue
        filtered_articles.sort()
        self.articles_left_in_day = filtered_articles
        
    # returns -1 if we can't move anymore (i.e. we're done), 1 on success
    def move_to_next_year(self):
        if(len(self.years_left) == 0):
            print('DONE!!')
            self.is_done = True
            return -1
        else:
            self.currentYear = self.years_left.pop()
            return 1

    # returns -1 if we can't move anymore (i.e. we're done), 1 on success
    def move_to_next_month(self):
        while(len(self.months_left_in_year) == 0):
            if(self.move_to_next_year() < 0):
                return -1
            self.set_months_left_in_year()
        self.currentMonth = self.months_left_in_year.pop()
        print("moving to monnth %d in year %d" % (self.currentMonth, self.currentYear))
        return 1
        
    # returns -1 if we can't move anymore (i.e. we're done), 1 on success
    def move_to_next_day(self):
        while(len(self.days_left_in_month) == 0):
            if(self.move_to_next_month() < 0):
                return -1
            self.set_days_left_in_month()
        self.currentDay = self.days_left_in_month.pop()
        return 1

    def move_to_next_article(self):
        while(len(self.articles_left_in_day) == 0):
            if(self.move_to_next_day() < 0):
                return -1
            self.set_articles_left_in_day()
        self.currentArticle = self.articles_left_in_day.pop()
        return 1
    
    """
    fns for processing text and removing repeats
    """
    # detects if text has repeated substrings and removes if true
    # this seems like a leetcode problem lol. I'm using this as a ref https://www.geeksforgeeks.org/python-check-if-string-repeats-itself/
    def removeRepeats(self, text):
        if(len(text) < 2):
            return text
        
        res = None
        temp = (text + text).find(text, 1, -1)
        if(temp != -1):
            res = text[:temp]
            return res
        return text

    def get_current_article_data(self):
        with open(self.get_current_path('article'), 'r') as f:
            articleRawText = ''
            try:
                articleRawText = f.read()
            except:
                print("error: %s", self.get_current_path('article'))
                return ""
            articleLines = articleRawText.splitlines()
            if(len(articleLines) == 0):
                print("error: %s", self.get_current_path('article'))
                return ""
            articleStart = ''
            for i in range(0, 3):
                articleLines[i] += '\n'
            articleStart = articleStart.join(articleLines[0:3])

            articleText = ''
            for i in range(3, len(articleLines)):
                articleLines[i] = re.sub('\s+', ' ', articleLines[i]).strip()
                articleLines[i] += '\n'
            articleTextJoined = articleText.join(articleLines[3:])
            articleText = self.removeRepeats(articleTextJoined)

            return articleStart + articleText

    def fix_current_article_data(self):
        newArticleData = self.get_current_article_data()
        f = open(self.get_current_path('article'), 'w')
        f.write(newArticleData)
        f.close()
        self.move_to_next_article()

    def pretty_print_current_article_data(self):
        current_article_data = self.get_current_article_data()
        print('----------------------------------------------------------')
        print(current_article_data)
        print('----------------------------------------------------------')

    def are_we_done(self):
        return self.is_done

def process_year(year):
    yearProcessor = ArchivesTextProcessor(ARCHIVES_TEXT_PATH, year, year + 1)
    print("starting to process year %d" % year)
    while(not yearProcessor.are_we_done()):
        yearProcessor.fix_current_article_data()
    print("done with processing year %d" % year)

def processYears(startYear, endYear):
    with Pool(POOL_SIZE) as p:
        p.map(process_year, list(range(startYear, endYear + 1)))

def print_num(num):
    print(num)
    print(num)

def pool_test(startYear, endYear):
    with Pool(POOL_SIZE) as p:
        p.map(print_num, list(range(startYear, endYear + 1)))

def tests():
    print('tests:')
    testProcessor = ArchivesTextProcessor(ARCHIVES_TEXT_PATH, 1901, 1902)

    # uncomment if you want to see some article data be printed out
    for i in range(10):
        print(testProcessor.get_current_path('article'))
        testProcessor.pretty_print_current_article_data()
        testProcessor.fix_current_article_data()
    print('if you compare with https://github.com/TheStanfordDaily/archives-text/tree/master/1899/12 you should see matching results')
    
# multiprocessed full upload of archives text
def process_archives_text():
    processYears(1892, 2014)

def main():
    # process_archives_text() # uncomment in order to actually process the text.
    tests()

if __name__ == '__main__':
    main()
