import datetime

from appium import webdriver

from parser import TrapAdvisorParser, ApplicationRunner

date1 = datetime.datetime.now()
date2 = datetime.datetime.now() + datetime.timedelta(days=3)
date3 = datetime.datetime.now() + datetime.timedelta(days=27)
date4 = datetime.datetime.now() + datetime.timedelta(days=27)
date5 = datetime.datetime.now() + datetime.timedelta(days=33)
date6 = datetime.datetime.now() + datetime.timedelta(days=34)
date7 = datetime.datetime.now() + datetime.timedelta(days=43)
date8 = datetime.datetime.now() + datetime.timedelta(days=44)
date9 = datetime.datetime.now() + datetime.timedelta(days=44)
date10 = datetime.datetime.now() + datetime.timedelta(days=75)
date11 = datetime.datetime.now() - datetime.timedelta(days=3)
date12 = datetime.datetime.now() - datetime.timedelta(days=75)

caps = {
    "appium:automationName": "uiautomator2",
    "platformName": "Android",
    "appium:ensureWebviewsHavePages": True,
    "appium:nativeWebScreenshot": True,
    "appium:newCommandTimeout": 3600,
    "appium:connectHardwareKeyboard": True,
}

driver = webdriver.Remote("http://localhost:4723", caps)
text_to_type = "The Grosvenor Hotel"
# trap_advisor_parser = TrapAdvisorParser(driver)
# print(trap_advisor_parser.parse(prompt=text_to_type, start_date=date1, end_date=date2))
# print(trap_advisor_parser.parse(prompt=text_to_type, start_date=date3, end_date=date4))
# print(trap_advisor_parser.parse(prompt=text_to_type, start_date=date5, end_date=date6))
# print(trap_advisor_parser.parse(prompt=text_to_type, start_date=date7, end_date=date8))
# print(trap_advisor_parser.parse(prompt=text_to_type, start_date=date9, end_date=date10))
# print(trap_advisor_parser.parse(prompt=text_to_type, start_date=date11, end_date=date12))
# print(date5, date6)
# TrapAdvisorParser(driver).test_parse(start_date=date5, end_date=date6)

# print(date1, date2)
# TrapAdvisorParser(driver).test_parse(start_date=date1, end_date=date2)

# print(date9, date10)
# TrapAdvisorParser(driver).test_parse(start_date=date9, end_date=date10)

app_runner = ApplicationRunner(driver)
app_runner.launch()