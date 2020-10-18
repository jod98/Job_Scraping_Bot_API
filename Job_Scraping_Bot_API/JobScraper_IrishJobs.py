from selenium import webdriver  # automate web browser interaction from Python
from selenium.webdriver.common.keys import Keys  # refer to keyboard key presses i.e. Keys.RETURN = 'Enter' on keyboard
from time import sleep  # allows program to 'sleep' for certain period of time
import json  # format for storing and exchanging data (text written in Javascript object notation - JavaScript Object Notation)
import csv  # format for storing and exchanging data (text separated with ',' - Common Separated Values)
from bs4 import BeautifulSoup  # library for pulling data out of HTML and XML files. With your favourite parser, it provides ways of searching the parse tree
from datetime import datetime  # provides current time and date
from selenium.webdriver.support.ui import Select  # allows us to select options from a dropdown menu
import re  # provides regular express matching operations


class IrishjobsJobScraper:
    options = webdriver.ChromeOptions()  # allows us to specify options in chrome
    options.add_argument('--start-maximized')  # start browser in maximised mode
    options.add_experimental_option("detach", True)  # don't initiate another browser when another object of this class created - use current browser (avoids re-login)
    driver = webdriver.Chrome(executable_path=r'Chromedriver/chromedriver.exe', options=options)  # setting path of chromedriver and importing our options

    def __init__(self, login):
        """Parameter Initialization"""

        # 'self' (keyword) represents instance of a class. Allows us to access attributes and methods of the class.
        # '__init__' (function) represents a general constructor in OOP. Method called when object is created from a class and allows class to initialised attributes

        self.irishjobs_email = login['irishjobs_email']  # retrieving indeed email from login_file (json)
        self.irishjobs_password = login['irishjobs_password']  # retrieving indeed password from login_file (json)

        self.driver.get("https://www.irishjobs.ie/Login")  # access login page for indeed
        sleep(5)  # loading time

        login_email = self.driver.find_element_by_id('Email')  # find 'email' textbox
        login_email.clear()  # clear current contents
        login_email.send_keys(self.irishjobs_email)  # input email into textbox
        login_pass = self.driver.find_element_by_id('Password')  # find 'password' textbox
        login_pass.clear()  # clear current contents
        login_pass.send_keys(self.irishjobs_password)  # find 'password' textbox
        login_pass.send_keys(Keys.RETURN)  # simulates pressing "enter" on keyboard i.e. submit
        sleep(5)  # loading time

    def job_search(self, irishjobs_position):
        """Access 'Jobs' Section and Input Position and Location"""

        self.driver.get('https://www.irishjobs.ie/')  # navigate to 'jobs' section via url
        sleep(5)  # loading time

        search_position = self.driver.find_element_by_id('Keywords')  # find 'position' textbox
        search_position.clear()  # clear current contents
        search_position.send_keys(irishjobs_position)  # input 'position' into textbox

        select_location = Select(self.driver.find_element_by_id('Location'))  # find 'location' textbox
        select_location.select_by_visible_text('Leinster')  # select 'Leinster' from dropdown menu

        submit_button = self.driver.find_element_by_id('btnSubmit')  # find 'submit' button
        submit_button.click()  # click 'submit'
        sleep(5)  # loading time

    def filter(self):
        recruiter_type = self.driver.find_element_by_link_text("Company")  # filter by 'company' not 'agency'
        recruiter_type.click()  # click 'company' filter option

    def get_job_info(self):
        """Retrieve Information from Job Card/Listing and Export to '.CSV' File"""
        records = []  # list to store 'record' (tuple) for each job card/listing
        next_page_value = 2  # allows us to iterate through next pages (next page from 1 is 2)
        no_of_jobs = self.driver.find_element_by_xpath("//label[@class='jobsFound']").text.split()[-1]  # retrieving number of jobs value from page

        while True:  # do this forever (until we break out at the end when we hit condition - no more pages left to search through)
            html = self.driver.page_source  # get source code for page
            soup = BeautifulSoup(html, 'html.parser')  # using library to convert source code to html so we can parse the tree and find job info

            job_card = soup.find_all("div", {"itemtype": "https://schema.org/JobPosting"})  # find all job cards/listings

            for job in job_card:  # iterate through all job listings
                title = job.find("h2", {"itemprop": "title"}).find("a", {"href": re.compile('/Jobs')}).text  # retrieve job title
                company = job.find("a", {"itemprop": "hiringOrganization"}).text  # retrieve company
                location = job.find("li", {"class": "location"}).find("a", {"href": re.compile('/Jobs')}).text  # retrieve job location
                job_site = 'Irish Jobs'  # retrieve job site
                post_date = job.find("li", {"itemprop": "datePosted"}).text.replace('Updated ', '')  # retrieve job post date
                extract_date = datetime.today().strftime('%d/%m/%Y')  # retrieve extract date (when script ran to retrieve jobs)

                a = datetime.strptime(extract_date, "%d/%m/%Y").date()  # converting 'extract_date' to datetime object
                b = datetime.strptime(post_date, "%d/%m/%Y").date()   # converting 'post_date' to datetime object
                post_date_days = str(a - b).replace(', 0:00:00', '')  # days since job listing posted
                if post_date_days == '0:00:00':
                    post_date_days = 'Today'

                job_url = 'https://www.irishjobs.ie' + job.find("h2", {"itemprop": "title"}).find("a", {"href": re.compile('/Jobs')}).get('href')  # retrieve job url

                record = (title, company, location, job_site, post_date_days, extract_date, job_url)  # add all variables into record (tuple)

                records.append(record)  # append current job card to records list

            try:
                current_page = self.driver.current_url  # retrieve current url

                if int(no_of_jobs) > 25:  # 25 job posts per page... if there are more than 25 in total then we decrease 'no_of_jobs' by 25 each time so we don't iterate through pages forever
                    if "&Page=" in str(current_page):  # currently on page 2 or more
                        split_url = current_page.split('=Company', 1)[-1]  # get value of current page we on i.e. '&Page=2'
                        next_page = current_page.replace(split_url, '') + '&Page=' + str(next_page_value)  # creating the next page url to redirect to '&Page=2', '&Page=3' etc.
                        self.driver.get(next_page)  # retrieve 'next page'
                        sleep(5)  # loading time

                    if "&Page=" not in str(current_page):  # currently on page 1
                        next_page = current_page + '&Page=' + str(next_page_value)  # creating the next page url to redirect to '&Page=2'
                        self.driver.get(next_page)  # retrieve 'next page'
                        sleep(5)  # loading time

                    next_page_value = next_page_value + 1  # incrementing so we can access next page when we iterate through above statements again
                    no_of_jobs = int(no_of_jobs) - 25  # decreasing number of jobs so we don't iterate through pages forever
                else:
                    break   # this is the last page of results i.e. don't attempt to click 'next page'
            except AttributeError:
                break  # no more pages to iterate through

        with open('Job_Listings_Duplicates.csv', 'a', newline='', encoding='utf-8') as jlf:  # open '.csv' file and append job info
            job_listings_file = csv.writer(jlf)  # initialising csv writer - provides ability to append ('a') rows into spreadsheet
            job_listings_file.writerows(records)  # appending all job records we retrieved

    def retrieve_jobs(self, irishjobs_position):
        """Calls Preceding Functions"""
        self.job_search(irishjobs_position)  # call 'job_search' function and pass in 'position' and 'location' arguments
        sleep(5)  # loading time
        self.filter()  # call 'filter' function
        sleep(5)  # loading time
        self.get_job_info()  # call 'get_job_info' function
        sleep(5)  # loading time


if __name__ == '__main__':  # runs program in its entirety and signifies the program is being run as standalone or is imported. '__name__' = special variable initialised at runtime
    with open('Login_Credentials/login_credentials.json') as login_file:  # open the '.json' file and load all the data
        login_file = json.load(login_file)  # loads all the data (deserialises data to a Python object)

    irishjobs_bot = IrishjobsJobScraper(login_file)  # creating an instance (object) of class and passing in 'login_credentials.csv' - provides login functionality in '__init__' function

    with open('Job_Details/input_irishjobs.txt', 'r') as irishjobs_file:  # open the '.txt' file and read all the data
        irishjobs_input = csv.reader(irishjobs_file)  # initialising csv writer - provides ability to read ('r') rows
        for row in irishjobs_input:  # iterate through each element (row) on each line
            irishjobs_bot.retrieve_jobs(row[0])  # call 'retrieve_function' with 'position' and 'location' of job passed in from file
