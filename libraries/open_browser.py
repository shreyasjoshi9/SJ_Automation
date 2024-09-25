import os
import pickle
from os import path
import logging
import logging.config
from selenium.webdriver import DesiredCapabilities
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.microsoft import IEDriverManager
from utilities import common_utilities as util
import traceback

#Read logging details from config file
logging_configuration = util.read_config(util.get_project_directory())
logging.config.fileConfig(logging_configuration)
logger = logging.getLogger("root")

config = util.read_config(util.get_project_directory())
module_name = config.get('Data', 'Module_Name')
TC_ID = config.get('Execution', 'Testcase_ID')

def get_node_ip():
    try:
        node_ip = config.get('Execution', 'node_ip')
        if str(config.get('Execution', 'Remote_Execution')).lower() == "true":
            node_ip = str(node_ip)
            if node_ip == "":
                raise Exception("Invalid Remote Execution parameters. Please check node ip.")
            node_ip = "http://"+node_ip+"/wd/hub"
    except Exception as e:
        logging.error("Error in getting node ip "+str(e))
    finally:
        return node_ip

class BrowserDetails():
    def __init__(self,browser):
        self.browser = browser

    def get_driver(self):
        try:
            driver = self.browser_details(self.browser)
            return driver
        except Exception as e:
            logging.error("Error in getting driver "+str(e))


    global browser_type

    @staticmethod
    def browser_details(browser_type):
        try:
            browser_type = browser_type.lower()
            config = util.read_config(util.get_project_directory())
            driver = None
            node_ip = get_node_ip()
            runtime_driver_update = config.get('Execution', 'download_driver_update_runtime').lower()
            runtime_driver_update = str(runtime_driver_update).lower()

            if browser_type == "":
                browser_type = "chrome"
                logging.warning("Browser is not provided. Chrome will be the default browser for automation.")

            if browser_type == "firefox":
                options = webdriver.FirefoxOptions()
                options.add_argument('--start-maximized')
                if runtime_driver_update == "true":
                    driver = webdriver.Firefox(executable_path=GeckoDriverManager.install(), options=options)
                else:
                    executable_path = os.path.join(util.get_project_directory(),'drivers', 'geckodriver')
                    if str(config.get('Execution', 'Remote_Execution')).lower() == "true":
                        driver = webdriver.Remote(command_executor=node_ip,desired_capabilities=DesiredCapabilities.FIREFOX)
                    else:
                        driver = webdriver.Firefox(executable_path=executable_path, options=options)
                driver.maximize_window()

            elif browser_type == "chrome":
                options = webdriver.ChromeOptions()
                options.add_argument('--start-maximized')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option("excludeSwitches", ["enable-logging"])
                if runtime_driver_update == "true":
                    driver = webdriver.Chrome(executable_path=ChromeDriverManager.install(), options=options)
                else:
                    executable_path = os.path.join(util.get_project_directory(), 'drivers', 'chromedriver')
                    if str(config.get('Execution', 'Remote_Execution')).lower() == "true":
                        driver = webdriver.Remote(command_executor=node_ip, desired_capabilities=DesiredCapabilities.CHROME)
                    else:
                        driver = webdriver.Chrome(executable_path=executable_path, options=options)
                driver.maximize_window()

            elif browser_type == "ie":
                options = webdriver.IeOptions()
                options.add_argument('--start-maximized')
                if runtime_driver_update == "true":
                    driver = webdriver.Ie(executable_path=IEDriverManager.install(), options=options)
                else:
                    executable_path = os.path.join(util.get_project_directory(), 'drivers', 'IEDriverServer')
                    if str(config.get('Execution', 'Remote_Execution')).lower() == "true":
                        driver = webdriver.Remote(command_executor=node_ip, desired_capabilities=DesiredCapabilities.INTERNETEXPLORER)
                    else:
                        driver = webdriver.Ie(executable_path=executable_path, options=options)
                driver.maximize_window()

            elif browser_type == "edge":
                options = webdriver.ChromeOptions()
                options.add_argument('--start-maximized')
                if runtime_driver_update == "true":
                    driver = webdriver.Edge(executable_path=EdgeChromiumDriverManager.install(), options=options)
                else:
                    executable_path = os.path.join(util.get_project_directory(),'drivers', 'msedgedriver')
                    if str(config.get('Execution', 'Remote_Execution')).lower() == "true":
                        driver = webdriver.Remote(command_executor=node_ip,desired_capabilities=DesiredCapabilities.EDGE)
                    else:
                        driver = webdriver.Edge(executable_path=executable_path, options=options)
                driver.maximize_window()
            else:
                raise util.Error("Invalid Browser name : " + browser_type)
        except Exception as e:
            if str(config.get('Execution', 'Remote_Execution')).lower() == "true":
                if "No host specified" in str(e):
                    logging.error("Remote Execution Script host is not configured correctly "+str(e))
                if "Failed to establish a new connection" in str(e):
                    logging.error("Remote Execution Test host is not configured correctly "+str(e))
            logging.error("Error occurred for '" + browser_type + "' : " + str(e))
            traceback.print_exc()
            traceback.print_exception()

        finally:
            return driver

    @staticmethod
    def open_url(url):
        logging.info(url + " will now launch in '" + browser_type + "'")
        pass

if __name__ == '__main__':
    config = util.read_config(util.get_project_directory())
    cls = BrowserDetails(config.get('Browser', 'browser'))
    driver_details = cls.get_driver()
    driver_details.get(config.get('Application_Details', 'URL'))







