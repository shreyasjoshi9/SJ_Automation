import os
import logging
import logging.config
import traceback
import allure
import pandas as pd
from utilities import common_utilities as util
from libraries import close_browser
from programs import log_settings
from libraries.open_browser import BrowserDetails
from libraries import elements
from libraries import utilities_key_library
from utilities import environment_xml_creator
from utilities import environment_variables_setup

# Read logging details from config file
logging_configuration = util.read_config(util.get_project_directory())
logging.config.fileConfig(logging_configuration)
logger = logging.getLogger("root")

TestCase_Scenario = ""
Test_Case_ID = ""
config = util.read_config(util.get_project_directory())
browsers_list = []


# Following function will fetch the module name provided by the user in config file
def fetch_module_name():
    try:
        module_name = config.get('Data', 'Module_Name')
        return module_name
    except Exception as e:
        logging.error("Error occurred for " + log_settings.testcase_id + " while fetching the module name. " + str(e))


# Following function will fetch the resource file path when the user provides the file name
def fetch_resource_file_name(name):
    filename = ""
    try:
        extension = name.find('.csv')
        slash_position = name.find('/')
        filename = name[slash_position + 1:extension]
    except Exception as e:
        logging.error(
            "Error occurred for " + log_settings.testcase_id + " while fetching resource file name. " + str(e))
    finally:
        return filename


# Following function will read data from the uimap csv file of the current testcase getting executed
def read_data_from_uimap_csv(ui_path):
    try:
        uimap_file_path = os.path.join(util.get_project_directory(), *ui_path.split('/'))
        df_ui = pd.read_csv(uimap_file_path, delimiter='\t', encoding='utf-8' or 'utf-16')
    except Exception as e:
        logging.error("Error in reading uimap file " + str(e))
    finally:
        return df_ui


# Following function will read data from the testdata csv file of the current testcase getting executed
def read_data_from_testdata_csv(td_path, sequence, get_sequence):
    df_td = ""
    try:
        df_td = pd.read_csv(td_path, delimiter='\t', encoding='utf-8' or 'utf-16')
        if get_sequence == True:
            df_td = df_td.sort_values('Sequence')
            df_td = df_td[df_td['Sequence'] == float(sequence)]
    except Exception as e:
        logging.error("Error in reading test data file " + str(e))
    finally:
        return df_td


# Following function will read testrepo file and provide more details about the selected testcases
def get_testcase_parameters_from_testrepo():
    try:
        project_dir = util.get_project_directory()
        tc_file_name = 'testrepo.' + fetch_module_name() + '.csv'
        tc_file_path = os.path.join(project_dir, 'resources', fetch_module_name(), 'testcases', tc_file_name)
        df_tc = pd.read_csv(tc_file_path, delimiter='\t', encoding='utf-8' or 'utf-16')
        print(df_tc)
        df_tc = df_tc.fillna("None")
        df_tc = df_tc[df_tc['Execute'] == 1]
        tc_id_list = list(df_tc['TC_ID'])
        tc_name_list = list(df_tc['TC_Name'])
        tc_severity_list = list(df_tc['TC_Severity'])
        tc_browser_list = list(df_tc['Browser'])
        testcase_id = config.get('Execution', 'Testcase_ID')
        tc_param_list = []
        for tc in range(len(tc_id_list)):
            tc_param_list.append((tc_id_list[tc], tc_name_list[tc], tc_severity_list[tc], tc_browser_list[tc],
                                  testcase_id))

        return tc_id_list
    except Exception as e:
        if 'Execute' in e:
            logging.error("Error occurred for " + testcase_id + " :" + str(e))
        else:
            logging.error(
                "Error occurred for " + log_settings.testcase_id + "Error in getting testcase parameters " + str(e))


def mark_broken_step(combination_file_path, test_data_path, step_title):
    raise Exception(
        "Error found in combination file " + combination_file_path + " while using test data from " + test_data_path + "at step" + step_title)


def mark_broken_sub_step(comment):
    raise Exception(comment)


class Standalone:
    total_tcs = get_testcase_parameters_from_testrepo()
    web_driver = None
    active_element = None
    var_list = ()

    # Following function will read test design csv file for provided testcase
    @staticmethod
    def read_test_design_csv(tc_id):
        try:
            test_design_file_name = tc_id + fetch_module_name() + '.csv'
            project_dir = util.get_project_directory()
            test_design_file_path = os.path.join(project_dir, 'resources', +fetch_module_name() + 'testdesigns',
                                                 test_design_file_name)
            df_tdesign = pd.read_csv(test_design_file_path, delimiter='\t', encoding='utf-8' or 'utf-16')
            return df_tdesign
        except Exception as e:
            logging.error(
                "Error occurred for " + log_settings.testcase_id + "Error in getting test design data " + str(e))

    # Following function will iterate through keywords as per user's requirement stated in csv files
    @staticmethod
    def execute_standalone(combination_file_path, test_data_file_path, browser, step_title=None):
        global active_element, value
        keyword = ""
        sequence = ""
        locator_name = ""
        status = ""
        try:
            logging.info(
                "--------------------------------------------------------------------------------------------------")
            logging.info("Testcase ID : " + log_settings.testcase_id + combination_file_path + "has started execution")
            logging.info(
                "Testcase ID : " + log_settings.testcase_id + test_data_file_path + "is being referred for testdata")
            logging.info(
                "--------------------------------------------------------------------------------------------------")

            status = True
            combo_file_path = os.path.join(util.get_project_directory(), *combination_file_path.split('/'))
            td_file_path = os.path.join(util.get_project_directory(), *test_data_file_path.split('/'))
            df_cf = pd.read_csv(combo_file_path, delimiter='\t', encoding='utf-8' or 'utf-16')
            df_cf = df_cf[df_cf['Active'] == 1]
            df_cf = df_cf.sort_values('Sequence')
            for index, row in df_cf.iterrows():
                if status == False:
                    break

                keyword = row['Keyword'].strip()
                elements.keyword = str(keyword).lower()
                sequence = str(row['Sequence']).strip()
                uimap_path = str(row['Uimap']).strip()
                locator_name_list = row['locator_name'].split(';')
                keyword = keyword.lower()

                if Standalone.web_driver:
                    Standalone.web_driver.implicitly_wait(config.get('Application_Details', 'timeout'))

                if keyword == 'browseropen':
                    for locator_name in locator_name_list:
                        if browser == "" or str(browser).lower() == "none":
                            browser_type = config.get('Browser', 'browser')
                        else:
                            browser_type = browser
                        active_element = browser_type
                        Standalone.web_driver = BrowserDetails(browser_type).get_driver()
                        browser_type = browser_type.title()
                        browsers_list.append(browser_type)
                        if str(Standalone.web_driver).lower() == "none":
                            status = False
                        else:
                            allure.attach(utilities_key_library.capture_screenshot_in_png(Standalone.web_driver),
                                          name=log_settings.testcase_teststep_id + "-" + keyword,
                                          attachment_type=allure.attachment_type.PNG)
                            log_settings.key_value = browser_type
                            logging.info(
                                "Testcase ID: " + log_settings.testcase_id + log_settings.keyword + " - " + log_settings.key_value)
                            status = True
                            if status == False:
                                break

                elif keyword == 'openurl':
                    df_td_sheet = read_data_from_testdata_csv(test_data_file_path, sequence, get_sequence=True)
                    for locator_name in locator_name_list:
                        url_value = df_td_sheet[df_td_sheet['locator_Name'] == locator_name]
                        url_value = url_value['Data'].values[0]
                        if str(url_value) == "" or str(url_value) == "nan":
                            url_value = config.get('Application_Details', 'URL')
                        active_element = url_value
                        Standalone.web_driver.get(url_value)
                        allure.attach(utilities_key_library.capture_screenshot_in_png(Standalone.web_driver),
                                      name=log_settings.testcase_teststep_id + "-" + keyword,
                                      attachment_type=allure.attachment_type.PNG)
                        log_settings.key_value = url_value
                        logging.info(
                            "Testcase ID: " + log_settings.testcase_id + log_settings.keyword + " - " + log_settings.key_value)

                elif keyword == 'switchtoiframes':
                    df_ui = read_data_from_uimap_csv(uimap_path)
                    '''by default multiple locators will be taken'''
                    for locator_name in locator_name_list:
                        df_temp_locator = df_ui[df_ui['ControlName'] == locator_name]
                        status, active_locator = elements.switch_to_i_frame(Standalone.web_driver, df_temp_locator)
                        if (status == False) and str(
                                config.get('Execution_Control', 'StopTcOnAnyFailures')).lower() == "true":
                            break

                elif keyword == 'switchtodefaultcontent':
                    status = elements.switch_to_default_content(Standalone.web_driver)
                    allure.attach(utilities_key_library.capture_screen_png(Standalone.web_driver),
                                  name=log_settings.tc_ts_id + '_' + keyword,
                                  attachment_type=allure.attachment_type.PNG)
                    logging.info("TR_ID =  " + config.get('Application',
                                                          'TR_Output_Dir') + ", TC_ID = " + log_settings.testcaseid + log_settings.keyword + " | " + log_settings.kv)

                elif keyword == 'typetext':
                    df_ui = read_data_from_uimap_csv(uimap_path)
                    df_td_sheet = read_data_from_testdata_csv(test_data_file_path, sequence, get_sequence=True)
                    for locator_name in locator_name_list:
                        sheet_index = df_td_sheet[df_td_sheet['locator_Name'] == locator_name].index.values
                        value_to_be_set = df_td_sheet[df_td_sheet['locator_Name'] == locator_name]
                        value_to_be_set = str(value_to_be_set['Data'].values[0])
                        value_to_be_set = str(value_to_be_set).strip()
                        value_to_be_set = str(value_to_be_set)
                        df_locator_name = df_ui[df_ui['ControlName'] == locator_name]
                        status, active_element = elements.type_text(Standalone.web_driver, value_to_be_set,
                                                                    df_locator_name)
                        if status == False:
                            break

                elif keyword == 'click':
                    df_ui = read_data_from_uimap_csv(uimap_path)
                    for locator_name in locator_name_list:
                        df_locator_name = df_ui[df_ui['ControlName'] == locator_name]
                        status, active_element = elements.click(Standalone.web_driver, df_locator_name)
                        if status == False:
                            break

                elif keyword == 'pickuptext':
                    df_ui = read_data_from_uimap_csv(uimap_path)
                    for locator_name in locator_name_list:
                        df_locator_name = df_ui[df_ui['ControlName'] == locator_name]
                        status, active_element = elements.pickup_text(Standalone.web_driver, df_locator_name)
                        if status == False:
                            break

                else:
                    status = False
                    logging.error(
                        "Error occurred for '" + log_settings.testcase_id + "' Invalid Keyword! '" + keyword + "' , status: " + str(
                            status))
                    mark_broken_step(combination_file_path, test_data_file_path, step_title)

        except Exception as e:
            status = False
            if "index 0 is out of bounds for axis 0 with size 0" in str(e):
                logging.error("Error occurred for '" + log_settings.testcase_id + " - " + log_settings.keyword + str(
                    e) + "locator name in combination file and test data file does not match!")
                mark_broken_sub_step(
                    "Execution failed as error occurred due to mismatch in locator name in combination and testdata files!")
            else:
                logging.error("Error occurred for '" + log_settings.testcase_id + " - " + log_settings.keyword + str(e))
                mark_broken_step(combination_file_path, test_data_file_path, step_title)
        finally:
            return sequence, locator_name, keyword, status, active_element

    def standalone_executioner(self, get_testcase_parameters_from_testrepo):
        config = util.read_config(util.get_project_directory())
        framework_Release_Date = config.get('Application_Details', 'Framework_Release_Date')
        framework_Version = config.get('Application_Details', 'Framework_Version')
        logging.info(
            "------                 " + fetch_module_name() + " Framework Version: " + framework_Version + " Release Date: " + framework_Release_Date + "                 ------")
        environment_variables_setup.create_environment_var()
        global Test_Case_ID

        for tc in Standalone.total_tcs:
            Test_Case_ID = tc
            df_test_design = self.read_test_design_csv(Test_Case_ID)
            tc_status = True
            status_list = []

            try:
                project_dir = util.get_project_directory()
                tc_file_name = 'testrepo.' + fetch_module_name() + '.csv'
                tc_file_path = os.path.join(project_dir, 'resources', fetch_module_name(), 'testcases', tc_file_name)
                df_tc = pd.read_csv(tc_file_path, delimiter='\t', encoding='utf-8' or 'utf-16')
                df_tc = df_tc[df_tc['Execute'] == 1]
                print(df_tc)
                tc_list = list(df_tc['TC_ID'])
                browser = df_tc['Browser']
                browser_name = browser.to_string(index=False)

                test_design = df_test_design[df_test_design['TC_ID'] == Test_Case_ID]
                test_design = test_design[test_design['Active'] == 1]
                test_design = test_design.sort_values('Sequence')

                for index, row in test_design.iterrows():
                    combination_file_path = row['CombinationFile'].strip()
                    test_data_file_path = row['TestData'].strip()
                    step_title = row['StepTitle'].strip()
                    step_id = str(row['Sequence']).strip()
                    if step_id.find(".") > 0:
                        step_id = step_id[:-2]
                    step_title_report = "Step " + step_id + " - " + step_title

                    log_settings.testcase_id = row['TC_ID'] + "In step " + str(row['Sequence']) + " - " + row[
                        'StepTitle']
                    log_settings.testcase_teststep_id = row['TC_ID'] + " TestStep " + step_id + " - keyword"
                    logging.info("In progress with the Execution of Testcase ID: " + row['TC_ID'] + "")
                    tc_sequence, locator_name, keyword, tc_status, tc_active_element = self.execute_standalone(
                        combination_file_path, test_data_file_path, browser.strip(), step_title=step_title_report)
                    if tc_status == False:
                        mark_broken_step(combination_file_path, test_data_file_path, step_title=step_title)
                    status_list.append(tc_status)
                    logging_info = str(status_list)
                    logging.info(
                        "Testcase ID : " + log_settings.testcase_id + "with all status values: " + logging_info)

                if Standalone.web_driver:
                    Standalone.var_list.clear()
                    close_browser.CloseBrowser.close_browser(Standalone.web_driver, browser_name)
                    Standalone.web_driver = None
            except Exception as e:
                tc_status = False
                traceback.print_exc()
                logging.error(
                    "Error occurred for '" + log_settings.testcase_id + "' as its failed due to Assertion error!")
                raise AssertionError(
                    "Test Case failed at \n Step Title: " + step_title + "\n Combination File: " + fetch_resource_file_name(
                        combination_file_path) + "'\n Step: " + tc_sequence + "'\n keyword: " + keyword + "'\n Locator: " + locator_name + "'\n identified by: " + tc_active_element + "'")
            finally:
                if False in status_list and tc_status:
                    tc_status = False
                    print("End of execution!")


if __name__ == '__main__':
    Standalone.standalone_executioner(get_testcase_parameters_from_testrepo([]))


