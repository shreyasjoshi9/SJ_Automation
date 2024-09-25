import time
import traceback
import utilities.common_utilities as util
import os
import logging

#Read logging details from config file

logging_configuration = util.read_config(util.get_project_directory())
logging.config.fileConfig(logging_configuration)
logger = logging.getLogger("root")

def wait(time_in_seconds):
    #this can be used as a keyword for static wait
    status = True
    try:
        time.sleep(time_in_seconds)
    except Exception as e:
        status = False
        traceback.print_exc()
    return status

#This will take screenshots at each step for the testcases:
def capture_screenshot(web_driver):
    try:
        screen_path = os.path.join(util.get_project_directory(),'output', 'screenshots', util.get_random_string(10)+'.png')
        print(screen_path)
        web_driver.get_screenshot_as_file(screen_path)
        return screen_path
    except Exception as e:
        logging.error("Error in capturing the screenshot. "+str(e))

def capture_screenshot_in_png(web_driver):
    try:
        return web_driver.get_screenshot_as_png()
    except Exception as e:
        logging.error("Error in capturing the screenshot as png. "+str(e))


if __name__ == '__main__':
    print(capture_screenshot(1))


