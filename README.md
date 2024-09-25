# SJ_Automation
Demo Hybrid Automation Framework

This framework consist of a hybrid automation approach. It is Keyword as well as Data driven. This framework is best suitable for UI Automation.
For a fully developed web application, user does not need to make changes in the framework code.
The framework is created in such a way that only testdata needs to be changed.
Go to resoueces folder to update the testdata.

In testdata, user needs to provide ui elements in uimaps file.
test data in testdata file and create a combination file which will have the paths to both of these Ui and test data files.

The testcases marked with "1" will be executed.

# Install Dependencies

Navigate to the project directory and install required Python packages:

Make sure Python 3.10.0+ is installed.

pipenv install Pipfile

Running the Tests

Execute the tests using Pytest. This command will also generate an Allure report.

pytest --alluredir=/path/to/allure/results

After running the tests, you can view the Allure report by using:

allure serve /path/to/allure/results

Deployment

Add additional notes about how to deploy this on a live system if applicable.

Built With

Playwright - The web automation framework used

Pytest - The testing framework

Allure - Test reporting tool

Authors:

Shreyas Joshi

License: NA

Please reach out to shreyas.joshi9@gmail.com for queries.

:)
