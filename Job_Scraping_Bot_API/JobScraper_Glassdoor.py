from selenium import webdriver  # automate web browser interaction from Python
from selenium.webdriver.common.keys import Keys  # refer to keyboard key presses i.e. Keys.RETURN = 'Enter' on keyboard
from time import sleep  # allows program to 'sleep' for certain period of time
import \
    json  # format for storing and exchanging data (text written in Javascript object notation - JavaScript Object Notation)
import csv  # format for storing and exchanging data (text separated with ',' - Common Separated Values)
from bs4 import \
    BeautifulSoup  # library for pulling data out of HTML and XML files. With your favourite parser, it provides ways of searching the parse tree
from datetime import datetime  # provides current time and date
import re  # provides regular express matching operations


class GlassdoorJobScraper:
    """Initialising selenium webdriver options outside '__init__' function (web browser closes if not defined outside)"""
    options = webdriver.ChromeOptions()  # allows us to specify options in chrome
    options.add_argument('--start-maximized')  # start browser in maximised mode
    options.add_experimental_option("detach",
                                    True)  # don't initiate another browser when another object of this class created - use current browser (avoids re-login)
    driver = webdriver.Chrome(executable_path=r'Chromedriver/chromedriver.exe',
                              options=options)  # setting path of chromedriver and importing our options

    def __init__(self, login):
        """Parameter Initialisation"""

        # 'self' (keyword) represents instance of a class. Allows us to access attributes and methods of the class.
        # '__init__' (function) represents a general constructor in OOP. Method called when object is created from a class and allows class to initialised attributes

        self.glassdoor_email = login['glassdoor_email']  # retrieving glassdoor email from login_file (json)
        self.glassdoor_password = login['glassdoor_password']  # retrieving glassdoor password from login_file (json)

        self.driver.get("https://www.glassdoor.ie/profile/login_input.htm")  # access login page for indeed
        sleep(5)  # loading time

        login_email = self.driver.find_element_by_name('username')  # find 'email' textbox
        login_email.clear()  # clear current contents
        login_email.send_keys(self.glassdoor_email)  # input email into textbox
        login_pass = self.driver.find_element_by_name('password')  # find 'password' textbox
        login_pass.clear()  # clear current contents
        login_pass.send_keys(self.glassdoor_password)  # find 'password' textbox
        login_pass.send_keys(Keys.RETURN)  # simulates pressing "enter" on keyboard i.e. submit
        sleep(5)  # loading time

    def job_search(self, glassdoor_position, glassdoor_location):
        """Access 'Jobs' Section and Input Position and Location"""

        search_position = self.driver.find_element_by_xpath(
            "//input[contains(@id, 'sc.keyword')]")  # find 'position' textbox
        search_position.clear()  # clear current contents
        search_position.send_keys(glassdoor_position)  # input 'position' into textbox

        search_location = self.driver.find_element_by_xpath(
            "//input[contains(@id, 'sc.location')]")  # find 'location' textbox
        search_location_current_text = search_location.get_attribute(
            'value')  # retrieve the 'value' attribute - autofill on therefore current text not erased using .clear()

        try:
            for i in search_location_current_text:  # iterate all chars in the 'location' textbox (autofilled word)
                search_location.send_keys(Keys.BACKSPACE)  # and delete all the chars
        except AttributeError:
            pass  # if autofill turned of (possible future update to site) then pass i.e. move on

        search_location.send_keys(glassdoor_location)  # now... input 'location' into textbox
        search_location.send_keys(Keys.RETURN)  # simulates pressing "enter" on keyboard i.e. submit
        sleep(5)  # loading time

    def get_job_info(self, glassdoor_position):
        """Retrieve Information from Job Card/Listing and Export to '.CSV' File"""
        records = []  # list to store 'record' (tuple) for each job card/listing
        post_date_new = ''  # needed -> error ('variable might be referenced before assignment') - in below

        while True:  # do this forever (until we break out at the end when we hit condition - no more pages left to search through)
            html = self.driver.page_source  # get source code for page
            soup = BeautifulSoup(html, 'html.parser')  # using library to convert source code to html so we can parse the tree and find job info
            job_card = soup.find_all("li", re.compile("jl react-job-listing gdGrid"))  # find all job cards/listings i.e. find 'li' tags that contains 'jl react...'

            for job in job_card:  # iterate through all job listings
                title = job.find(name="a",
                                 class_="jobInfoItem jobTitle css-13w0lq6 eigr9kq1 jobLink").text  # retrieve job title
                company = job.find(name="div",
                                   class_="jobHeader d-flex justify-content-between align-items-start").text  # retrieve company name
                location = job.find(name="span", class_="loc css-nq3w9f pr-xxsm").text  # retrieve job location
                job_site = 'Glassdoor'  # retrieve job site
                post_date = job.find(name="div",
                                     class_="d-flex align-items-end pl-std css-mi55ob").text  # retrieve job post date. Either '1d' or '1h' so...
                if 'd' in post_date:
                    post_date_new = post_date.replace('d', ' days')  # if post_date has 'd', replace with 'days'
                if 'h' in post_date:
                    post_date_new = post_date.replace('h', ' hours')  # if post_date has 'h', replace with 'hours'
                extract_date = datetime.today().strftime(
                    '%Y-%m-%d')  # retrieve extract date (when script ran to retrieve jobs)
                job_url = 'https://www.glassdoor.ie' + job.div.a.get('href')  # retrieve job url

                record = (title, company, location, job_site, glassdoor_position, post_date_new, extract_date,
                          job_url)  # add all variables into record (tuple)

                records.append(record)  # append current job card to records list

            page_x_of_x = soup.find(name="div", class_="cell middle hideMob padVertSm").text.replace('Page ', '')  # remove the 'page' from variable i.e. 'page 1 of 2' -> '1 of 2'
            no_of_current_page = page_x_of_x.split()[0]  # retrieve current page number
            no_of_pages = page_x_of_x.split()[-1]  # retrieve last page number
            current_page = self.driver.current_url  # retrieve current url

            try:
                if int(no_of_current_page) < int(no_of_pages):  # if current page < last page i.e. can access next page
                    if int(no_of_pages) == 1:  # if no_of_pages = 1...
                        break  # don't click to next page

                    if int(no_of_pages) > 1 and int(no_of_current_page) == 1:  # if current page is 1 and there are more than 1 page then click to page 2
                        next_page = current_page.replace('.htm', '') + '_IP' + str(int(
                            no_of_current_page) + 1) + '.htm'  # creating 'next page' url i.e. glassdoor-page2, glassdoor-page3... everytime we loop
                        self.driver.get(next_page)  # retrieve 'next page'
                        sleep(5)  # loading time

                    if int(no_of_pages) > 2 and int(no_of_current_page) > 1:  # if current page is > 1 and there are more than 2 pages then click to page 3.. then page 4... etc.
                        split_url = current_page[current_page.rindex('_')+1:]  # splitting url so we can access last part i.e. 'page2' and change it to 'page3'
                        next_page = current_page.replace(split_url, '') + 'IP' + str(int(no_of_current_page) + 1) + '.htm'  # creating 'next page' url i.e. glassdoor-page2, glassdoor-page3... everytime we loop
                        self.driver.get(next_page)  # retrieve 'next page'
                        sleep(5)  # loading time
                else:
                    break  # current page is not less than no of pages i.e. we on the last page of results
            except AttributeError:
                break  # no more pages to iterate through

        with open('Job_Listings_Duplicates.csv', 'a', newline='', encoding='utf-8') as jlf:  # open '.csv' file and append job info
            job_listings_file = csv.writer(
                jlf)  # initialising csv writer - provides ability to append ('a') rows into spreadsheet
            job_listings_file.writerows(records)  # appending all job records we retrieved

    def retrieve_jobs(self, glassdoor_position, glassdoor_location):
        self.job_search(glassdoor_position,
                        glassdoor_location)  # call 'job_search' function and pass in 'position' and 'location' arguments
        sleep(5)  # loading time
        self.get_job_info(glassdoor_position)  # call 'get_job_info' function
        sleep(5)  # loading time


if __name__ == '__main__':  # runs program in its entirety and signifies the program is being run as standalone or is imported. '__name__' = special variable initialised at runtime
    with open('Login_Credentials/login_credentials.json') as login_file:  # open the '.json' file and load all the data
        login_file = json.load(login_file)  # loads all the data (deserialises data to a Python object)

    glassdoor_bot = GlassdoorJobScraper(
        login_file)  # creating an instance (object) of class and passing in 'login_credentials.csv' - provides login functionality in '__init__' function

    with open('Job_Details/input_glassdoor.txt', 'r') as glassdoor_file:  # open the '.txt' file and read all the data
        glassdoor_input = csv.reader(glassdoor_file)  # initialising csv writer - provides ability to read ('r') rows
        for row in glassdoor_input:  # iterate through each element (row) on each line
            glassdoor_bot.retrieve_jobs(row[0], row[
                1])  # call 'retrieve_function' with 'position' and 'location' of job passed in from file
