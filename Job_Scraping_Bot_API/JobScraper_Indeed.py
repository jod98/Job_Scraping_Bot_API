from selenium import webdriver  # automate web browser interaction from Python
from selenium.webdriver.common.keys import Keys  # refer to keyboard key presses i.e. Keys.RETURN = 'Enter' on keyboard
from time import sleep  # allows program to 'sleep' for certain period of time
import json  # format for storing and exchanging data (text written in Javascript object notation - JavaScript Object Notation)
import csv  # format for storing and exchanging data (text separated with ',' - Common Separated Values)
from bs4 import BeautifulSoup  # library for pulling data out of HTML and XML files. With your favourite parser, it provides ways of searching the parse tree
from datetime import datetime  # provides current time and date
from selenium.common.exceptions import NoSuchElementException  # no such element exists


class IndeedJobScraper:
    """Initialising selenium webdriver options outside '__init__' function (web browser closes if not defined outside)"""
    options = webdriver.ChromeOptions()  # allows us to specify options in chrome
    options.add_argument('--start-maximized')  # start browser in maximised mode
    options.add_experimental_option("detach", True)  # don't initiate another browser when another object of this class created - use current browser (avoids re-login)
    driver = webdriver.Chrome(executable_path=r'Chromedriver/chromedriver.exe', options=options)  # setting path of chromedriver and importing our options

    def __init__(self, login):
        """Parameter Initialisation"""

        # 'self' (keyword) represents instance of a class. Allows us to access attributes and methods of the class.
        # '__init__' (function) represents a general constructor in OOP. Method called when object is created from a class and allows class to initialised attributes

        self.indeed_email = login['indeed_email']  # retrieving indeed email from login_file (json)
        self.indeed_password = login['indeed_password']  # retrieving indeed password from login_file (json)

        self.driver.get("https://secure.indeed.com/account/login")  # access login page for indeed
        sleep(5)  # loading time

        login_email = self.driver.find_element_by_id('login-email-input')  # find 'email' textbox
        login_email.clear()  # clear current contents
        login_email.send_keys(self.indeed_email)  # input email into textbox
        login_pass = self.driver.find_element_by_id('login-password-input')  # find 'password' textbox
        login_pass.clear()  # clear current contents
        login_pass.send_keys(self.indeed_password)  # find 'password' textbox
        login_pass.send_keys(Keys.RETURN)  # simulates pressing "enter" on keyboard i.e. submit
        sleep(5)  # loading time

    def job_search(self, indeed_position, indeed_location):
        """Access 'Jobs' Section and Input Position and Location"""

        jobs_link = self.driver.find_element_by_link_text('Find jobs')  # find 'jobs' button
        jobs_link.click()  # click 'jobs' button
        sleep(5)  # loading time

        search_position = self.driver.find_element_by_id('text-input-what')  # find 'position' textbox
        search_position.clear()  # clear current contents
        search_position.send_keys(indeed_position)  # input 'position' into textbox

        search_location = self.driver.find_element_by_id('text-input-where')  # find 'location' textbox
        search_location_current_text = search_location.get_attribute('value')  # retrieve the 'value' attribute - autofill on therefore current text not erased using .clear()

        try:
            for i in search_location_current_text:  # iterate all chars in the 'location' textbox (autofilled word)
                search_location.send_keys(Keys.BACKSPACE)  # and delete all the chars
        except AttributeError:
            pass  # if autofill turned of (possible future update to site) then pass i.e. move on

        search_location.send_keys(indeed_location)  # now... input 'location' into textbox
        search_location.send_keys(Keys.RETURN)  # simulates pressing "enter" on keyboard i.e. submit
        sleep(5)  # loading time

    def filter(self):
        """Filters Job Results"""
        distance_radius = "&radius=50"  # adding filter 'within 50 radius' to url
        recruiter_type = "&sr=directhire"  # adding filter 'employer' to url

        current_url = self.driver.current_url  # retrieve current url (not filtered)
        self.driver.get(current_url + distance_radius + recruiter_type)  # retrieve the url with added filters
        sleep(5)  # loading time

        try:
            close_popup = self.driver.find_element_by_xpath("//button[@aria-label='Close']")  # locating 'X' button for close popup
            close_popup.click()  # click 'X' button to close popup
        except NoSuchElementException:
            pass

    def get_job_info(self):
        """Retrieve Information from Job Card/Listing and Export to '.CSV' File"""
        records = []  # list to store 'record' (tuple) for each job card/listing

        while True:  # do this forever (until we break out at the end when we hit condition - no more pages left to search through)
            html = self.driver.page_source  # get source code for page
            soup = BeautifulSoup(html, 'html.parser')  # using library to convert source code to html so we can parse the tree and find job info
            job_card = soup.find_all('div', 'jobsearch-SerpJobCard unifiedRow row result clickcard')  # find all job cards/listings

            for job in job_card:  # iterate through all job listings
                try:
                    title = job.h2.a.get('title')  # retrieve job title
                except AttributeError:
                    title = ""
                try:
                    company = job.find(name="span", class_="company").text.strip()  # retrieve company name
                except AttributeError:
                    company = ""
                try:
                    location = job.find(name="div", class_="recJobLoc").get('data-rc-loc')  # retrieve job location
                except AttributeError:
                    location = ""
                try:
                    job_site = 'Indeed'  # retrieve job site
                except AttributeError:
                    job_site = ""
                try:
                    post_date = job.find(name="span", class_="date").text.replace(' ago', '')  # retrieve job post date without 'ago' at end
                except AttributeError:
                    post_date = ""
                try:
                    extract_date = datetime.today().strftime('%Y-%m-%d')  # retrieve extract date (when script ran to retrieve jobs)
                except AttributeError:
                    extract_date = ""
                try:
                    job_url = 'https://ie.indeed.com' + job.h2.a.get('href')  # retrieve job url
                except AttributeError:
                    job_url = ""

                record = (title, company, location, job_site, post_date, extract_date, job_url)  # add all variables into record (tuple)
                records.append(record)  # append current job card to records list

            try:
                next_page = 'https://ie.indeed.com' + soup.find('a', {'aria-label': 'Next'}).get('href')  # try click 'next page' once we've iterated through all job cards - retrieve next page url
                self.driver.get(next_page)  # access 'next page' via url
                sleep(5)  # loading time
            except AttributeError:
                break  # if no 'next page' then pass

        with open('Job_Listings_Duplicates.csv', 'a', newline='', encoding='utf-8') as jlf:  # open '.csv' file and append job info
            job_listings_file = csv.writer(jlf)  # initialising csv writer - provides ability to append ('a') rows into spreadsheet
            job_listings_file.writerows(records)  # appending all job records we retrieved

    def retrieve_jobs(self, indeed_position, indeed_location):
        """Calls Preceding Functions"""
        self.job_search(indeed_position, indeed_location)  # call 'job_search' function and pass in 'position' and 'location' arguments
        sleep(5)  # loading time
        self.filter()  # call 'filter' function
        sleep(5)  # loading time
        self.get_job_info()  # call 'get_job_info' function
        sleep(5)  # loading time


if __name__ == '__main__':  # runs program in its entirety and signifies the program is being run as standalone or is imported. '__name__' = special variable initialised at runtime
    with open('Login_Credentials/login_credentials.json') as login_file:  # open the '.json' file and load all the data
        login_file = json.load(login_file)  # loads all the data (deserialises data to a Python object)

    indeed_bot = IndeedJobScraper(login_file)  # creating an instance (object) of class and passing in 'login_credentials.csv' - provides login functionality in '__init__' function

    with open('Job_Details/input_indeed.txt', 'r') as indeed_file:  # open the '.txt' file and read all the data
        indeed_input = csv.reader(indeed_file)  # initialising csv writer - provides ability to read ('r') rows
        for row in indeed_input:  # iterate through each element (row) on each line
            indeed_bot.retrieve_jobs(row[0], row[1])  # call 'retrieve_function' with 'position' and 'location' of job passed in from file
