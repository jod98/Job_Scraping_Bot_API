# Job_Scraping_Bot_API-Python
Automating the Process of Searching for Jobs using the Selenium Open-Source API through 4 Major Job Sites (Indeed, Glassdoor, Linkedin, IrishJobs)

Due to recent (COVID-19) pandemic, it has proved a great challenge to secure a job directly after graduating in 2020. As a result of the circumstances, I decided to improvise and improve upon my technical skills and knowledge, one example being this project. This project gives users the ability to automate the job searching and application process while applying an array of preferred filters. 

Setup:
1. Clone the repository and store it in a directory of your choice
2. In the "Job_Scraping_Bot_API/Login_Credentials/login_credentials.json" file, simply add your 'username' and 'password' for all the following job sites
3. In the "Job_Scraping_Bot_API/Job_Details/" directory, simply add your desired 'job title' and 'location' into the various '.txt' file names in the way I have presented (this will avoid errors as some job boards job inputs are case sensitive and implement drop down menus to select location)
4. Lastly, simply run the "JobScrapersActivator.py" file and a '.csv' file containing all job listings (which removes duplicates entries if found on another site) will be created in your current directory.

