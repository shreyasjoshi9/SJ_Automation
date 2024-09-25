import configparser
import datetime
import traceback
from pathlib import Path
import os
import random
import string
import logging
from selenium.webdriver.support.wait import WebDriverWait
from programs import log_settings
import allure
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

Overall_total_time = []
runtime_dict = {}

#get current working directory
def get_project_directory():
    try:
        project_path = Path(__file__).parents[1]
        return project_path
    except Exception as e:
        logging.error(log_settings.testcase_id + ' found Error '+ str(e))

def find_dict_duplicate(dict, value_key):
    try:
        duplicate_status = ""
        duplicate_status = "key not found"
        dict_keys = dict.keys()
        for item in dict_keys:
            if str(value_key).lower() == str(item).lower():
                duplicate_status = "key found"
                break
    except Exception as e:
        logging.error(log_settings.testcase_id + " | Error while loading Variable Dictionary - | " + str(e))
    finally:
        return duplicate_status

def add_to_dict(dict, value_key, Value):
    try:
        duplicate_key_found = find_dict_duplicate(dict,value_key)
        if str(duplicate_key_found).lower() == "key found":
            logging.info("Duplicate key error for the dictionary load - " + value_key)
        if str(duplicate_key_found).lower() == "key not found":
            dict[value_key] = Value
    except Exception as e:
        logging.info(log_settings.testcase_id + "Error loading runtime variable dictionary - " + str(e))
        incorret_dynamic_storage_attempt(value_key, str(e))


def incorret_dynamic_storage_attempt(key, exception_thrown):
    raise Exception("The dynamic variable storage attempt was made for - '" + key + "' and exception was  - " + exception_thrown)

#Read configuration from Config.ini file
def read_config(project_directory):
    try:
        config_file_path = os.path.join(project_directory,'configuration','config.ini')
        config = configparser.RawConfigParser()
        config.read(config_file_path)
        return config
    except Exception as e:
        logging.error(log_settings.testcase_id + ' found Error '+ str(e))

def get_bytes_from_file(file_name_with_extension):
    try:
        return open(file_name_with_extension, "rb").read()
    except Exception as e:
        logging.error("Error found in file conversion: " +str(e))

def get_random_string(n):
    try:
        return ''.join(random.choices(string.ascii_uppercase+string.digits,k=n))
    except Exception as e:
        logging.error(log_settings.testcase_id + ' found Error '+ str(e))

class Error(Exception):
    pass

@allure.step('broken locator found at ''"{control_name}"')
def broken_locator(control_name, locator):
    raise Exception("Testcase_ID = '"+log_settings.testcase_id + "' Locator name : '"+control_name+"' and value : "+locator+ " is not available. Search timed out!")

def highlight_locator(web_driver, locator):
    config = read_config(get_project_directory())
    highlight_color = config.get('Data','color')
    element = web_driver.find_element_by_xpath(locator)
    web_driver.execute_script("arguments[0].setAttribute('style',arguments[1]);", element, "background:#"+highlight_color)

def remove_duplicates(list):
    entry_list = []
    for entry in list:
        if entry not in entry_list:
            entry_list.append(entry)
    return entry_list

def wait_for_element_to_load(driver,control_name, locator):
    try:
        locator_found = True
        timeout = read_config(get_project_directory()).getint('Application_Details', 'timeout')
        time_start = datetime.datetime.now()
        config = read_config(get_project_directory())
        highlight = config.get('Data', 'object_highlighter')
        logging.info("Testcase ID : "+log_settings.testcase_id+" trying to search the control name "+control_name+ " using locator: "+locator)

        element_present = EC.presence_of_element_located((By.XPATH, locator))
        element_present_and_clickable = EC.element_to_be_clickable((By.XPATH, locator))
        WebDriverWait(driver, timeout).until(element_present)
        WebDriverWait(driver, timeout).until(element_present_and_clickable)
        time_end = datetime.datetime.now()
        if highlight == "True":
            highlight_locator(driver, locator)

        total_time = time_end - time_start
        total_time = total_time.seconds
        total_time_percentage = str((total_time/timeout)*100)
        total_time = str(total_time)
        Overall_total_time.append(total_time)
        logging.info("Testcase ID : "+log_settings.testcase_id+" with the control name "+control_name+ " using locator: "+locator+ " found!")
        logging.info("Testcase ID : "+log_settings.testcase_id+" with the control name "+control_name+ " using locator: "+locator+ " took "+total_time+ " seconds to be operable and consumed "+total_time_percentage+ " of the time specified.")
        locator_found = True
    except Exception or Error as e:
        print(e)
        locator_found = False
        logging.error("Error occurred for "+log_settings.testcase_id+" as its timed out while trying to search the control name "+control_name+ " using locator: "+locator)
        broken_locator(control_name,locator)
    finally:
        return locator_found
if __name__ == "__main__":
    pass


