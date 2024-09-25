import os
from utilities import common_utilities as util
import logging
import logging.config
import traceback
import platform
import xml.etree.cElementTree as ET

#Read logging details from config file
logging_configuration = util.read_config(util.get_project_directory())
logging.config.fileConfig(logging_configuration)
logger = logging.getLogger("root")

def environment_xml_creation(url_list, browsers_list):
    try:
        project_dir = util.get_project_directory()
        config = util.read_config(util.get_project_directory())
        environment_file_name = 'environment.xml'

        output_directory = config.get('Execution', 'Testcase_ID')
        if output_directory.lower() == "output":
            environment_file_path = os.path.join(project_dir,'output', environment_file_name)
        elif output_directory.lower() == "":
            environment_file_path = os.path.join(project_dir,'output', environment_file_name)
        else:
            environment_file_path = os.path.join(project_dir, 'output',output_directory, environment_file_name)

        module_name = config.get('Data', 'Module_Name')
        highlights = config.get('Data','object_highlighter')
        url = ','.join(url_list)
        browser = ','.join(browsers_list)
        screenshot = config.get('Execution', 'screenshot')
        framework_release_date = config.get('Application_Details','Framework_Release_Date')
        framework_version = config.get('Application_Details','Framework_Version')
        operating_system = platform.system()
        runtime_driver_update = config.get('Execution','download_driver_update_runtime')
        if str(config.get('Execution','Remote_Execution')).lower() == "true":
            node_ip = config.get('Execution','node_ip')
        else:
            node_ip = "Local Machine"


        #This will create a xml structure which will be attached with the allure report

        environment = ET.Element("environment")
        parameter1 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter1,"key").text = "Module Name"
        ET.SubElement(parameter1, "value").text = module_name

        parameter2 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter2, "key").text = "Highlighter"
        ET.SubElement(parameter2, "value").text = highlights

        parameter3 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter3, "key").text = "url"
        ET.SubElement(parameter3, "value").text = url

        parameter4 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter4, "key").text = "browser"
        ET.SubElement(parameter4, "value").text = browser

        parameter5 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter5, "key").text = "screenshots"
        ET.SubElement(parameter5, "value").text = screenshot

        parameter6 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter6, "key").text = "Framework Release Date"
        ET.SubElement(parameter6, "value").text = framework_release_date

        parameter7 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter7, "key").text = "Framework Version"
        ET.SubElement(parameter7, "value").text = framework_version

        parameter8 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter8, "key").text = "Remote Execution Test Host IP"
        ET.SubElement(parameter8, "value").text = node_ip

        parameter9 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter9, "key").text = "Runtime Driver Updates"
        ET.SubElement(parameter9, "value").text = runtime_driver_update

        parameter10 = ET.SubElement(environment, "parameter")
        ET.SubElement(parameter10, "key").text = "Operating system"
        ET.SubElement(parameter10, "value").text = operating_system

        tree = ET.ElementTree(environment)
        logging.info("Environment file path: "+environment_file_path)
        tree.write(r'F:\SJ_Automation\output\TC_0001\environment.xml', xml_declaration= True, encoding='utf-8')

    except Exception as e:
        logging.warning("Error in generating Environment Details "+ str(e))
        traceback.print_exc()

if __name__ =="__main__":
    temp_path= '*'