import os
from utilities import common_utilities as util
import logging
import logging.config
import traceback

#Read logging details from config file

logging_configuration = util.read_config(util.get_project_directory())
logging.config.fileConfig(logging_configuration)
logger = logging.getLogger("root")

def get_module_name():
    try:
        config = util.read_config(util.get_project_directory())
        module_name = config.get('Data', 'Module_Name')
        return module_name
    except Exception as e:
        logging.error("Error in fetching Module Name " +str(e))

def create_environment_var():
    try:
        config = util.read_config(util.get_project_directory())

        #Following feature will download latest browser driver dynamically at runtime
        runtime_driver_update = config.get('Execution', 'download_driver_update_runtime').lower()
        runtime_driver_update = str(runtime_driver_update)
        if runtime_driver_update == 'true':
            os.environ['WDM_LOG_LEVEL'] = '0'

        #For Allure:
        project_dir = util.get_project_directory()
        allure_ver = config.get('Application_Details', 'Allure_Version')
        if allure_ver == "":
            raise Exception("Allure version needs to be specified in configuration file! ")
        allure_path = os.path.join(project_dir,'allure-'+allure_ver,'bin')
        os.environ['ALLURE_PATH'] = allure_path

    except Exception as e:
        logging.error(" Exception : "+str(e))
        traceback.print_exc()
        traceback.print_exception()

if __name__ == '__main__':
    temp_path = "*"
