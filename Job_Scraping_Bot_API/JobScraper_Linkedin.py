from selenium import webdriver  # automate web browser interaction from Python
from selenium.webdriver.common.keys import Keys  # refer to keyboard key presses i.e. Keys.RETURN = 'Enter' on keyboard
from time import sleep  # allows program to 'sleep' for certain period of time
import json  # format for storing and exchanging data (text written in Javascript object notation - JavaScript Object Notation)
import csv  # format for storing and exchanging data (text separated with ',' - Common Separated Values)
from bs4 import BeautifulSoup  # library for pulling data out of HTML and XML files. With your favourite parser, it provides ways of searching the parse tree
from datetime import datetime  # provides current time and date
import re  # provides regular express matching operations


class LinkedinJobScraper:
    options = webdriver.ChromeOptions()  # allows us to specify options in chrome
    options.add_argument('--start-maximized')  # start browser in maximised mode
    options.add_experimental_option("detach", True)  # don't initiate another browser when another object of this class created - use current browser (avoids re-login)
    driver = webdriver.Chrome(executable_path=r'Chromedriver/chromedriver.exe', options=options)  # setting path of chromedriver and importing our options

    def __init__(self, login):
        """Parameter Initialization"""

        # 'self' (keyword) represents instance of a class. Allows us to access attributes and methods of the class.
        # '__init__' (function) represents a general constructor in OOP. Method called when object is created from a class and allows class to initialised attributes

        self.linkedin_email = login['linkedin_email']  # retrieving indeed email from login_file (json)
        self.linkedin_password = login['linkedin_password']  # retrieving indeed password from login_file (json)

        self.driver.get("https://www.linkedin.com/login")  # access login page for indeed
        sleep(5)  # loading time

        login_email = self.driver.find_element_by_name('session_key')  # find 'email' textbox
        login_email.clear()  # clear current contents
        login_email.send_keys(self.linkedin_email)  # input email into textbox
        login_pass = self.driver.find_element_by_name('session_password')  # find 'password' textbox
        login_pass.clear()  # clear current contents
        login_pass.send_keys(self.linkedin_password)  # find 'password' textbox
        login_pass.send_keys(Keys.RETURN)  # simulates pressing "enter" on keyboard i.e. submit
        #sleep(5)  # loading time
        sleep(120)  # security verification

    def job_search(self, linkedin_position, linkedin_location):
        """Access 'Jobs' Section and Input Position and Location"""

        jobs_link = self.driver.find_element_by_link_text('Jobs')  # navigate to 'jobs' section via button
        jobs_link.click()  # click 'jobs' button
        sleep(5)  # loading time

        search_position = self.driver.find_element_by_xpath("//input[contains(@id, 'jobs-search-box-keyword')]")  # find 'position' textbox
        search_position.clear()  # clear current contents
        search_position.send_keys(linkedin_position)  # input 'position' into textbox

        search_location = self.driver.find_element_by_xpath("//input[contains(@id, 'jobs-search-box-location-id')]")  # find 'location' textbox
        search_location.clear()  # clear current contents
        search_location.send_keys(linkedin_location)  # input 'location' into textbox
        search_location.send_keys(Keys.RETURN)  # simulates pressing "enter" on keyboard i.e. submit
        sleep(5)  # loading time

    def filter(self):
        """Retrieve Information from Job Card/Listing and Export to '.CSV' File"""

        all_filters_button = self.driver.find_element_by_xpath("//button[@data-control-name='all_filters']")  # locate 'all filters' button
        all_filters_button.click()  # click 'all filters' button
        sleep(3)  # loading time

        entry_level_button = self.driver.find_element_by_xpath("//label[@for='experience-2']")  # locate 'entry-level' button
        entry_level_button.click()  # click 'entry-level' button
        sleep(2)  # loading time

        associate_level_button = self.driver.find_element_by_xpath("//label[@for='experience-3']")  # locate 'associate' button
        associate_level_button.click()  # click 'associate' button
        sleep(2)  # loading time

        apply_filter_button = self.driver.find_element_by_xpath("//button[contains(@class, 'button--apply')]")  # locate 'apply filters' button
        apply_filter_button.click()  # click 'apply filters'' button
        sleep(5)  # loading time

    def get_job_info(self):
        """Retrieve Information from Job Card/Listing and Export to '.CSV' File"""
        records = []  # list to store 'record' (tuple) for each job card/listing
        next_page_value = 25  # allows us to iterate through next pages (next page from 1 is 2)
        no_of_jobs = self.driver.find_element_by_xpath("//small[@class='display-flex t-12 t-black--light t-normal']").text.split()[0].replace(',', '')  # retrieving number of jobs value from page

        while True:  # do this forever (until we break out at the end when we hit condition - no more pages left to search through)
            # Scroll to bottom of page to load all the listings - Linkedin integrates lazy loading
            scroll_box = self.driver.find_element_by_xpath("/html/body/div[8]/div[3]/div[3]/div/div/div/div/section/div")  # locating 'scroll box'
            last_ht = 0  # old height of scrollbox
            ht = 1  # new height of scrollbox
            while last_ht != ht:  # if last height != new height then...
                last_ht = ht  # set last height = new height
                ht = self.driver.execute_script("""arguments[0].scrollTo(0, arguments[0].scrollHeight); return arguments[0].scrollHeight;""", scroll_box)  # find height of scrollbox
                sleep(3)  # loading time

            html = self.driver.page_source  # get source code for page
            soup = BeautifulSoup(html, 'html.parser')  # using library to convert source code to html so we can parse the tree and find job info

            job_card = soup.find_all("div", {"class": re.compile('job-card-container relative job-card')})  # find all job cards/listings

            for job in job_card:  # iterate through all job listings
                try:
                    title = job.find("a", {"class": re.compile('job-card-list__title')}).text.strip()  # retrieve job title
                except AttributeError:
                    title = ""

                try:
                    company = job.find("a", {"class": re.compile('company-name ember-view')}).text.strip()  # retrieve company
                except AttributeError:
                    company = ""

                try:
                    location = job.find("li", {"class": 'job-card-container__metadata-item'}).text.strip()  # retrieve job location
                except AttributeError:
                    location = ""

                try:
                    job_site = 'Linkedin'  # retrieve job site
                except AttributeError:
                    job_site = ""

                try:
                    post_date = job.find("time", {"datetime": re.compile('2')}).text.strip().replace(' ago', '')  # retrieve job post date
                except AttributeError:
                    post_date = ""

                try:
                    extract_date = datetime.today().strftime('%d/%m/%Y')  # retrieve extract date (when script ran to retrieve jobs)
                except AttributeError:
                    extract_date = ""

                try:
                    job_url = 'https://www.linkedin.com' + job.find("div", {"class": re.compile('mr1 artdeco')}).find("a", {"href": re.compile('/jobs')}).get('href')  # retrieve job url
                except AttributeError:
                    job_url = ""

                record = (title, company, location, job_site, post_date, extract_date, job_url)  # add all variables into record (tuple)
                records.append(record)  # append current job card to records list

            try:
                current_page = self.driver.current_url  # retrieve current url

                if int(no_of_jobs) > 25:  # 25 job posts per page... if there are more than 25 in total then we decrease 'no_of_jobs' by 25 each time so we don't iterate through pages forever
                    if "&start=" in str(current_page):  # currently on page 2 or more
                        split_url = current_page.split('Ireland', 1)[-1]  # get value of current page we on i.e. '&start=25'
                        next_page = current_page.replace(split_url, '') + '&start=' + str(next_page_value)  # creating the next page url to redirect to '&start=25', '&start=50' etc.
                        self.driver.get(next_page)  # retrieve 'next page'
                        sleep(5)  # loading time

                    if "&start=" not in str(current_page):  # currently on page 1
                        next_page = current_page + '&start=' + str(next_page_value)  # creating the next page url to redirect to '&Page=2'
                        self.driver.get(next_page)  # retrieve 'next page'
                        sleep(5)  # loading time

                    next_page_value = next_page_value + 25  # incrementing so we can access next page when we iterate through above statements again
                    no_of_jobs = int(no_of_jobs) - 25  # decreasing number of jobs so we don't iterate through pages forever
                else:
                    break  # this is the last page of results i.e. don't attempt to click 'next page'
            except AttributeError:
                break  # no more pages to iterate through

        with open('Job_Listings_Duplicates.csv', 'a', newline='', encoding='utf-8') as jlf:  # open '.csv' file and append job info
            job_listings_file = csv.writer(jlf)  # initialising csv writer - provides ability to append ('a') rows into spreadsheet
            job_listings_file.writerows(records)  # appending all job records we retrieved

    def retrieve_jobs(self, linkedin_position, linkedin_location):
        """Calls Preceding Functions"""
        self.job_search(linkedin_position, linkedin_location)  # call 'job_search' function and pass in 'position' and 'location' arguments
        sleep(5)  # loading time
        self.filter()  # call 'filter' function
        sleep(5)  # loading time
        self.get_job_info()    # call 'get_job_info' function
        sleep(5)  # loading time


if __name__ == '__main__':  # runs program in its entirety and signifies the program is being run as standalone or is imported. '__name__' = special variable initialised at runtime
    with open('Login_Credentials/login_credentials.json') as login_file:  # open the '.json' file and load all the data
        login_file = json.load(login_file)  # loads all the data (deserialises data to a Python object)

    linkedin_bot = LinkedinJobScraper(login_file)  # creating an instance (object) of class and passing in 'login_credentials.csv' - provides login functionality in '__init__' function

    with open('Job_Details/input_linkedin.txt', 'r') as linkedin_file:  # open the '.txt' file and read all the data
        linkedin_input = csv.reader(linkedin_file)  # initialising csv writer - provides ability to read ('r') rows
        for row in linkedin_input:  # iterate through each element (row) on each line
            linkedin_bot.retrieve_jobs(row[0], row[1])  # call 'retrieve_function' with 'position' and 'location' of job passed in from file
