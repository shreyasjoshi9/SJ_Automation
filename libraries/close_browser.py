import logging
from libraries import open_browser
from utilities import common_utilities as util

#Read logging details from config file
logging_configuration = util.read_config(util.get_project_directory())
logging.config.fileConfig(logging_configuration)
logger = logging.getLogger("root")

config = util.read_config(util.get_project_directory())
browser_type = config.get('Browser', 'browser')

class CloseBrowser():
    @staticmethod
    def close_browser(driver,browser):
        try:
            if browser_type == "":
                browser_name = browser_type
            else:
                browser_name = browser
            if (browser_type == "") and (browser == ""):
                browser_name = "Chrome"
            logging.info("'"+browser_name+"' browser closed!")
            driver.quit()
        except Exception as e:
            logging.error("Error while closing the browser " +str(e))

if __name__ == '__main__':
    cls = open_browser.BrowserDetails(1)
    driver = cls.get_driver()
    CloseBrowser.close_browser(driver)

