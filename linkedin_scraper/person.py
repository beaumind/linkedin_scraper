import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .objects import Experience, Education, Scraper, Interest, Accomplishment, Contact
import os


class Person(Scraper):
    __TOP_CARD = "pv-top-card"

    def __init__(
            self,
            linkedin_url=None,
            name=None,
            about=[],
            experiences=[],
            educations=[],
            interests=[],
            accomplishments=[],
            company=None,
            job_title=None,
            contacts=[],
            skills=[],
            driver=None,
            get=True,
            scrape=True,
            close_on_complete=True,
    ):
        self.linkedin_url = linkedin_url
        self.name = name
        self.about = about
        self.experiences = experiences
        self.educations = educations
        self.interests = interests
        self.accomplishments = accomplishments
        self.also_viewed_urls = []
        self.skills = []
        self.contacts = contacts
        self.first_name = None
        self.last_name = None
        self.phone = None
        self.mobile = None
        self.email = None

        if driver is None:
            try:
                if os.getenv("CHROMEDRIVER") == None:
                    driver_path = os.path.join(
                        os.path.dirname(__file__), "drivers/chromedriver"
                    )
                else:
                    driver_path = os.getenv("CHROMEDRIVER")

                driver = webdriver.Chrome(driver_path)
            except:
                driver = webdriver.Chrome()

        if get:
            driver.get(linkedin_url)

        self.driver = driver

        if scrape:
            self.scrape(close_on_complete)

    def add_about(self, about):
        self.about.append(about)

    def add_experience(self, experience):
        self.experiences.append(experience)

    def add_education(self, education):
        self.educations.append(education)

    def add_interest(self, interest):
        self.interests.append(interest)

    def add_accomplishment(self, accomplishment):
        self.accomplishments.append(accomplishment)

    def add_location(self, location):
        self.location = location

    def add_contact(self, contact):
        self.contacts.append(contact)

    def scrape_min(self, close_on_complete=True):
        driver = self.driver
        root = driver.find_element_by_class_name(self.__TOP_CARD)
        self.name = root.find_elements_by_xpath("//section/div/div/div/*/li")[
            0
        ].text.strip()

        self.scrape_experiences()
        self.scrape_educations()
        self.scrape_about()
        self.scrape_location()
        self.scrape_skills()
        self.scrape_about()
        self.scrape_info()
        driver.quit()

    def scrape_experiences(self):
        driver = self.driver
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )
        try:
            _ = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.ID, "experience-section"))
            )
            exp = driver.find_element_by_id("experience-section")
        except:
            exp = None

        if exp is not None:
            for position in exp.find_elements_by_class_name("pv-position-entity"):
                position_title = position.find_element_by_tag_name("h3").text.strip()
                try:
                    company = position.find_elements_by_tag_name("p")[1].text.strip()
                    try:
                        seperator = position.find_elements_by_tag_name("p")[1].find_element_by_class_name('separator').text.strip()
                        company = company.replace(seperator, '').strip()
                    except:
                        print('none')
                except:
                    company = None

                try:
                    times = str(
                        position.find_elements_by_tag_name("h4")[0]
                            .find_elements_by_tag_name("span")[1]
                            .text.strip()
                    )
                    from_date = " ".join(times.split(" ")[:2])
                    to_date = " ".join(times.split(" ")[3:])
                    duration = (
                        position.find_elements_by_tag_name("h4")[1]
                            .find_elements_by_tag_name("span")[1]
                            .text.strip()
                    )
                except:
                    from_date, to_date, duration = (None, None, None)

                try:
                    location = (
                        position.find_elements_by_tag_name("h4")[2]
                            .find_elements_by_tag_name("span")[1]
                            .text.strip()
                    )
                except:
                    location = None

                experience = Experience(
                    position_title=position_title,
                    from_date=from_date,
                    to_date=to_date,
                    duration=duration,
                    location=location,
                )
                experience.institution_name = company
                self.add_experience(experience)

    def scrape_about(self):
        # get about
        try:
            see_more = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='lt-line-clamp__more']",
                    )
                )
            )
            driver.execute_script("arguments[0].click();", see_more)

            about = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//*[@class='lt-line-clamp__raw-line']",
                    )
                )
            )
        except:
            about = None
        if about:
            self.add_about(about.text.strip())

    def scrape_location(self):
        driver = self.driver
        location = driver.find_element_by_class_name(f"{self.__TOP_CARD}--list-bullet")
        location = location.find_element_by_tag_name("li").text
        self.add_location(location)

    def scrape_educations(self):
        driver = self.driver
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/1.5));"
        )
        try:
            _ = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.ID, "education-section"))
            )
            edu = driver.find_element_by_id("education-section")
        except:
            edu = None
        if edu:
            for school in edu.find_elements_by_class_name(
                    "pv-profile-section__list-item"
            ):
                university = school.find_element_by_class_name(
                    "pv-entity__school-name"
                ).text.strip()

                try:
                    degree = (
                        school.find_element_by_class_name("pv-entity__degree-name")
                            .find_elements_by_tag_name("span")[1]
                            .text.strip()
                    )
                except:
                    degree = None

                try:
                    field_of_study = (
                        school.find_element_by_class_name("pv-entity__fos")
                            .find_elements_by_tag_name("span")[1]
                            .text.strip()
                    )
                except:
                    field_of_study = None

                try:
                    times = (
                        school.find_element_by_class_name("pv-entity__dates")
                            .find_elements_by_tag_name("span")[1]
                            .text.strip()
                    )
                    from_date, to_date = (times.split(" ")[0], times.split(" ")[2])
                except:
                    from_date, to_date = (None, None)

                education = Education(
                    from_date=from_date, to_date=to_date, degree=degree, field_of_study=field_of_study
                )
                education.institution_name = university
                self.add_education(education)

    def scrape_skills(self):
        driver = self.driver
        driver.execute_script(
            "window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));"
        )
        try:
            _ = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pv-skill-categories-section"))
            )
            skills = driver.find_element_by_class_name("pv-skill-categories-section")
        except:
            skills = None

        if skills:
            try:
                skills.find_element_by_class_name("pv-profile-section__card-action-bar").click()
            except:
                print("skip")
            for skill in driver.find_elements_by_class_name("pv-skill-category-entity__name-text"):
                self.skills.append(skill.text.strip())

    def scrape_info(self):
        driver = self.driver
        driver.execute_script(
            "window.scrollTo(0, 0);"
        )

        try:
            driver.get(self.linkedin_url + '/detail/contact-info/')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@aria-labelledby='pv-contact-info']")))
            element = driver.find_element_by_xpath("//*[@aria-labelledby='pv-contact-info']")
            profile_header = element.find_element_by_class_name('pv-contact-info__header').text.strip()
            self.first_name = profile_header.replace('’s Profile', '')
            self.last_name = self.name.replace(self.first_name+' ', '')
        except:
            self.first_name = None
            self.last_name = None

    @property
    def company(self):
        if self.experiences:
            return (
                self.experiences[0].institution_name
                if self.experiences[0].institution_name
                else None
            )
        else:
            return None

    @property
    def job_title(self):
        if self.experiences:
            return (
                self.experiences[0].position_title
                if self.experiences[0].position_title
                else None
            )
        else:
            return None

    def __repr__(self):
        return "{name}\n\nAbout\n{about}\n\nExperience\n{exp}\n\nEducation\n{edu}\n\nInterest\n{int}\n\nAccomplishments\n{acc}\n\nContacts\n{conn}".format(
            name=self.name,
            about=self.about,
            exp=self.experiences,
            edu=self.educations,
            int=self.interests,
            acc=self.accomplishments,
            conn=self.contacts,
        )
