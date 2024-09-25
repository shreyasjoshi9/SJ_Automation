import os
from six import with_metaclass
from programs import log_settings
import logging
import configparser
from pathlib import Path
import pandas as pd
from enum import Enum
from allure_commons._core import plugin_manager, MetaPluginManager

ALLURE_UNIQUE_LABELS = ['severity', 'thread', 'host']
TestCase_Severity = list()

#get current working directory
def get_project_directory():
    try:
        project_path = Path(__file__).parents[1]
        return project_path
    except Exception as e:
        logging.error(log_settings.testcase_id + ' found Error '+ str(e))

#Read configuration from Config.ini file
def read_config(project_directory):
    try:
        config_file_path = os.path.join(project_directory,'configuration','config.ini')
        config = configparser.RawConfigParser()
        config.read(config_file_path)
        return config
    except Exception as e:
        logging.error(log_settings.testcase_id + ' found Error '+ str(e))

def get_module_name():
    try:
        config = read_config(get_project_directory())
        module_name = config.get('Data', 'Module_Name')
        return module_name
    except Exception as e:
        logging.error("Error in fetching Module Name " +str(e))

def get_testcase_severity():
    try:
        project_dir = get_project_directory()
        testcase_file_name = 'testcase.'+get_module_name()+'.csv'
        testcase_file_path = os.path.join(project_dir, 'resources', 'CyRev_Automation', 'testcases', testcase_file_name)
        df_tc = pd.read_csv(testcase_file_path, delimiter='\t', encoding='utf-16' or 'utf-8')
        df_tc_index = df_tc[df_tc['Execute'] == 1].index.values
        df_tc_index = int(df_tc_index)
        TC_Severity = df_tc.iloc[df_tc_index]['TestCase_Sevirity']
        global TestCase_Severity
        TestCase_Severity = str(TC_Severity)
    except Exception as e:
        logging.info(log_settings.testcase_id+ " Testcase severity will be set as normal by default as Testcase file contains no value! " + str(e))

class Severity(str,Enum):
    #This function will fetch the severity from TestCase file
    get_testcase_severity()
    BLOCKER = 'blocker'
    CRITICAL = 'critical'
    NORMAL = 'normal'
    MAJOR = 'major'
    MINOR = 'minor'
    CUSTOM = TestCase_Severity

class LabelType(str):
    EPIC = 'epic'
    FEATURE = 'feature'
    STORY = 'story'
    PARENT_SUITE = 'parent_suite'
    SUITE = 'suite'
    SUB_SUITE = 'sub_suite'
    SEVERITY = 'severity'
    THREAD = 'thread'
    HOST = 'host'
    TAG = 'tag'
    ID = 'id'
    FRAMEWORK = 'framework'
    LANGUAGE = 'language'

def safely(result):
    if result:
        return result[0]
    else:
        def dummy(function):
            return function
        return dummy()

def label(label_type, *labels):
    return safely(plugin_manager.hook.decorate_as_label(label_type=label_type, labels=labels))

def severity(severity_level):
    return label(LabelType.SEVERITY,severity_level)

class plugin_manager(with_metaclass(MetaPluginManager)):
    pass

if __name__ == "__main__":
    temp_path = '*'