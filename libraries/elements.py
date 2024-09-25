import json
import pickle

from programs import log_settings
import allure
import re
import traceback
import time
from utilities import common_utilities as util
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import logging
from selenium.webdriver.support.ui import Select

active_element = ""
keyword = ""
config = util.read_config(util.get_project_directory())

@allure.step
def mark_broken_sub_step(comment):
    raise Exception(comment)

def get_locator(web_driver, df_temp_locator, control_name, wait_status):
    try:
        status = True
        xpath = df_temp_locator['xpath'].iloc[0]
        active_element = str(xpath)
        if wait_status == 'True':
            status = util.wait_for_element_to_load(web_driver,control_name,xpath)
    except Exception as e:
        logging.error("Error occurred for "+log_settings.testcase_id+" while fetching the locator. "+str(e))
    finally:
        return active_element, status

def common_exception(df_temp_locator, e):
    try:
        status = False
        traceback.print_exc()
        if "single positional indexer is out-of-bounds" in str(e):
            logging.error("Error "+str(e)+" occurred for Testcase: '"+log_settings.testcase_id+"' in keyword: '"+keyword+ "' as uimap and control name mismatched! , status:  "+str(status))
            mark_broken_sub_step("Failure due to control name mismatch found in uimap and combination file while using '"+keyword+"'.")
        else:
            logging.error("Error "+str(e)+" occurred for Testcase: '"+log_settings.testcase_id+"' in keyword: '"+keyword+ " for element: '"+df_temp_locator['ControlName'].iloc[0]+"'.")
            mark_broken_sub_step("'"+df_temp_locator['ControlName'].iloc[0]+ "' failed while working with keyword '"+keyword+"'.")
    except Exception as exception:
        logging.error("Error " + str(exception) + " occurred for Testcase: '" + log_settings.testcase_id + "' in combination_file_exception.")
    finally:
        return status

def load_cookies(web_driver, cookie_location):
    status = True
    try:
        with open(cookie_location, 'r') as cookiesfile:
            cookies = json.load(cookiesfile)
            for cookie in cookies:
                # Ensure the domain is correct and matches the current domain in the browser
                if 'sameSite' in cookie:
                    del cookie['sameSite']
                web_driver.add_cookie(cookie)
        web_driver.refresh()
        logging.info("Cookies from location '" + cookie_location + "' are loaded.")
    except Exception as e:
        logging.error("Error " + str(e) + " occurred while loading cookies.")


def switch_to_i_frame(web_driver, df_temp_locator):
    status = True
    try:
        control_name = df_temp_locator['ControlName'].iloc[0]
        control_name = control_name.strip()
        if str(df_temp_locator['xpath'].iloc[0]) != 'nan':
            active_locator, status = get_locator(web_driver, df_temp_locator, control_name, wait_status = True)
            xpath = active_locator
            web_driver.switch_to.frame(xpath)
            logging.info("Successfully switch to the required iframe!")
        else:
            status = False
    except Exception as e:
        status = ("Error occurred in switching I frames"+str(e))
    finally:
        return status, active_locator

def switch_to_default_content(web_driver):
    status = True
    try:
        web_driver.switch_to.default_content()
    except Exception as e:
        status = False
        logging.error(log_settings.testcase_id + " | Error : " + str(e))
        traceback.print_exc()
        mark_broken_sub_step(e)
    return status

def type_text(web_driver, value, df_temp_locator):
    #this keyword can be used to type text into the textbox and special dropdowns.
    status = True
    try:
        control_name = df_temp_locator['ControlName'].iloc[0]
        control_name = control_name.strip()
        browser = config.get('Browser', 'browser')
        if str(df_temp_locator['xpath'].iloc[0]) != 'nan':
            active_element, status = get_locator(web_driver, df_temp_locator, control_name, wait_status=True)
            xpath = active_element
            available_value = str(value)
            if available_value == 'nan':
                available_value = ""
            if pickup_text(web_driver,df_temp_locator) != "":
                util.highlight_locator(web_driver, active_element)
                web_driver.find_element_by_xpath(xpath).clear()
                if browser.lower() != "firefox":
                    web_driver.find_element_by_xpath(xpath).send_keys(Keys.NULL)
        web_driver.find_element_by_xpath(xpath).send_keys(available_value)
        util.highlight_locator(web_driver, active_element)
        logging.info("Text '"+available_value+ "' is typed in the filed '"+control_name+"' for the Testcase: " +log_settings.testcase_id)
    except Exception as e:
        logging.error("Problem in 'Type_Text' operation with error" +str(e))
        status = False
    finally:
        logging.info("Operation 'Type_Text' is successfully performed for the locator: "+control_name+" with value "+available_value+ "- for the Testcase: "+log_settings.testcase_id)
        return status, active_element

def switch_to_tab(web_driver, title):
    status = True
    try:
        handles = web_driver.window_handles
        for each_tab in handles:
            web_driver.switch_to.window(each_tab)
            cur_title = web_driver.title
            if cur_title == title:
                break
    except Exception as e:
        status = False
        logging.error("TR_ID = " + config.get('Application', 'TR_Output_Dir') + ", TC_ID = " + log_settings.testcaseid + " | Error : " + str(e))
        traceback.print_exc()

    return status

def waitcustom(web_driver, wait_value):
        status = True
        try:
            time.sleep(float(wait_value))
            logging.info(
                "Total seconds of wait '" + wait_value + "' is applied for the Testcase: " + log_settings.testcase_id)
        except Exception as e:
            logging.error("Error " + str(
                e) + " occurred for Testcase: '" + log_settings.testcase_id + "' in keyword: '" + keyword + "' with status " + status)

def verify_text(web_driver,value_to_verify, df_temp_locator):
    status = True
    try:
        control_name = df_temp_locator['ControlName'].iloc[0]
        control_name = control_name.strip()
        if str(df_temp_locator['xpath'].iloc[0]) != 'nan':
            available_value = str(value_to_verify)
        status, text, active_element = pickup_text(web_driver, df_temp_locator)
        util.highlight_locator(web_driver, active_element)
        if str(value_to_verify) == str(text):
            logging.info("Text '" + str(text) + "' does match with value '" + str(value_to_verify) + "' for the Testcase: " + log_settings.testcase_id)
        else:
            status = False
    except Exception as e:
        logging.error("Problem in 'Verify_Text' operation with error" + str(e))
        status = False
    finally:
        logging.info("Operation 'Type_Text' is successfully performed for the locator: '"+control_name+"' with value '"+available_value+ "' - for the Testcase: "+log_settings.testcase_id)
        return status, active_element



def pickup_text(web_driver, df_temp_locator):
    #This keyword will pick up the text present on the given location
    status = True
    text = ''
    try:
        control_name = df_temp_locator['ControlName'].iloc[0]
        control_name = control_name.strip()
        if str(df_temp_locator['xpath'].iloc[0]) != 'nan':
            active_element, status = get_locator(web_driver, df_temp_locator, control_name, wait_status=True)
            xpath = active_element
            text_found = False
            if text_found == False:
                text = web_driver.find_element_by_xpath(xpath).text
                text_found = True
            if text_found == False:
                text = web_driver.find_element_by_xpath(xpath).get_attribute('value')
                text_found = True
            if text == '':
                text_found = False
            if text == None:
                text_found = False
            if text == 'nan':
                text_found = False
            if text_found == False:
                text = web_driver.find_element_by_xpath(xpath).get_attribute('alt')
                text_found = True

            util.highlight_locator(web_driver, active_element)
            logging.info("Testcase ID : "+log_settings.testcase_id+" "+df_temp_locator['ControlName'].iloc[0] + " is picked up as "+str(text))
    except NoSuchElementException as e:
        status = False
        logging.error("Error "+str(e)+" occurred for Testcase: '"+log_settings.testcase_id+"' in keyword: '"+keyword+ "' for element: '"+df_temp_locator['ControlName'].iloc[0]+"' with status "+status)
    finally:
        return status, str(text), active_element

def click(web_driver, df_temp_locator):
        #This function will be used for clicking the given locator
    status = True
    try:
        control_name = df_temp_locator['ControlName'].iloc[0]
        control_name = control_name.strip()
        if str(df_temp_locator['xpath'].iloc[0]) != 'nan':
            active_element, status = get_locator(web_driver, df_temp_locator, control_name, wait_status=True)
            xpath = active_element
            util.highlight_locator(web_driver, active_element)
            locator_found = util.wait_for_element_to_load(web_driver, control_name, xpath)
            if locator_found:
                web_driver.find_element_by_xpath(xpath).click()
            logging.info("Testcase ID : " + log_settings.testcase_id + " " + df_temp_locator['ControlName'].iloc[0] + " is clicked.")
        else:
            status = False
    except Exception as e:
        logging.error("Problem in 'Click' operation with error" + str(e))
        status = False
    finally:
        logging.info("Operation 'Click' is successfully performed for the locator: " + control_name + " for the Testcase: " + log_settings.testcase_id)
        return status, active_element

def select_dropdown_value(web_driver,value_to_select, df_temp_locator):
    status = True
    try:
        control_name = df_temp_locator['ControlName'].iloc[0]
        control_name = control_name.strip()
        if str(df_temp_locator['xpath'].iloc[0]) != 'nan':
            available_value = str(value_to_select)
            active_element, status = get_locator(web_driver, df_temp_locator, control_name, wait_status=True)
            xpath = active_element
            dropdown = Select(web_driver.find_element_by_xpath(xpath))
            dropdown.select_by_visible_text(str(value_to_select))
            util.highlight_locator(web_driver, active_element)
            logging.info("Option '" + str(value_to_select) + "' has been selected from the dropdown '" + control_name + "' for the Testcase: " + log_settings.testcase_id)
        else:
            status = False
    except Exception as e:
        logging.error("Problem in 'select_dropdown_value' operation with error" + str(e))
        status = False
    finally:
            logging.info("Operation 'Select_Dropdown_value' is successfully performed for the locator: '"+control_name+"' with value '"+available_value+ "' - for the Testcase: "+log_settings.testcase_id)
            return status, active_element

def verify_dropdown_value(web_driver,value_to_verify, df_temp_locator):
    status = True
    try:
        control_name = df_temp_locator['ControlName'].iloc[0]
        control_name = control_name.strip()
        if str(df_temp_locator['xpath'].iloc[0]) != 'nan':
            available_value = str(value_to_verify)
            active_element, status = get_locator(web_driver, df_temp_locator, control_name, wait_status=True)
            xpath = active_element
            #dropdown = Select(web_driver.find_element_by_xpath(xpath))
            #selected_option = dropdown.first_selected_option
            selected_option = web_driver.find_element_by_xpath(xpath).get_attribute('value')
            #logging.info("dropdown value is :" + str(selected_option))
            util.highlight_locator(web_driver, active_element)
        if str(value_to_verify) == str(selected_option):
            logging.info("Dropdown option '" + str(selected_option) + "' does match with value '" + str(value_to_verify) + "' for the Testcase: " + log_settings.testcase_id)
        else:
            status = False
    except Exception as e:
        logging.error("Problem in 'Verify_dropdown_value' operation with error" + str(e))
        status = False
    finally:
            logging.info("Operation 'Verify_Dropdown_Value' is successfully performed for the locator: '"+control_name+"' with value '"+available_value+ "' - for the Testcase: "+log_settings.testcase_id)
            return status, active_element

if __name__ == '__main__':
    pass





