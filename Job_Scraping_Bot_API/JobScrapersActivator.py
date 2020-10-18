import pandas as pd  # high-level data manipulation tool
import os  # module for accessing files in a directory
import csv  # format for storing and exchanging data (text separated with ',' - Common Separated Values)

if os.path.exists('Job_Listings_Duplicates.csv'):  # if previous file exists...
    os.remove('Job_Listings_Duplicates.csv')  # delete it (don't want new contents to be appended to old)

if os.path.exists('Job_Listings.csv'):  # if previous file exists...
    os.remove('Job_Listings.csv')  # delete it (don't want new contents to be appended to old)

with open('Job_Listings_Duplicates.csv', 'w', newline='', encoding='utf-8') as jlf:  # open '.csv' file and write in the headers
    job_listings_duplicates = csv.writer(jlf)  # # initialising csv writer - provides ability to write ('w') rows into spreadsheet
    job_listings_duplicates.writerow(
        ['Title', 'Company', 'Location', 'Job Site', 'Position', 'Post Date', 'Extract Date', 'Job URL'])  # write in the headers into the first row

print('Glassdoor Job Scraper Initiated!!!')
exec(open("JobScraper_Glassdoor.py").read())  # run the glassdoor job scraper
print('Glassdoor Job Scraper Finished!!!')
print('')

print('Indeed Job Scraper Initiated!!!')
exec(open("JobScraper_Indeed.py").read())  # run the indeed job scraper
print('Indeed Job Scraper Finished!!!')
print('')

print('IrishJobs Job Scraper Initiated!!!')
exec(open("JobScraper_IrishJobs.py").read())  # run the irishjobs job scraper
print('IrishJobs Job Scraper Finished!!!')
print('')

print('Linkedin Job Scraper Initiated!!!')
exec(open("JobScraper_Linkedin.py").read())  # run the linkedin job scraper
print('Linkedin Job Scraper Finished!!!')
print('')

job_listings_file = pd.read_csv("Job_Listings_Duplicates.csv")  # read in job listings duplicates csv file using pandas
job_listings_file_removed_duplicates = job_listings_file.drop_duplicates(subset=["Title", "Company", "Location"], keep="first")  # deletes all duplicate jobs posts from all job sites
job_listings_file_removed_duplicates.to_csv("Job_Listings.csv", index=False)  # exports new job listings to '.CSV' file

os.remove('Job_Listings_Duplicates.csv')  # delete the job listings file with the duplicates
