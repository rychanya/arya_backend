import pathlib
from parser.models import Settings
from parser.parsers import Login, QAIter, Run

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def main():
    settings = Settings.parse_file("settings.json")
    driver_path = pathlib.Path().resolve().joinpath("chromedriver")
    options = Options()
    options.headless = settings.headless

    for user in settings.users_cycle:
        driver = webdriver.Chrome(executable_path=str(driver_path), options=options)
        try:
            with Login(user.login, user.password, driver):
                for url in settings.urls:
                    with Run(driver, url):
                        qa = QAIter(driver)
                        for i in qa:
                            pass
        except Exception as error:
            print(error)
        finally:
            driver.quit()


if __name__ == "__main__":
    main()
