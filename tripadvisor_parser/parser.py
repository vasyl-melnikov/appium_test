import datetime

from appium import webdriver
from appium.webdriver.common.mobileby import MobileBy

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ui_elements import UiElements


class ApplicationRunner:
    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.actions = ActionChains(self.driver)

    def go_to_app_list(self):
        self.actions.w3c_actions = ActionBuilder(self.driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        self.actions.w3c_actions.pointer_action.move_to_location(441, 1335)
        self.actions.w3c_actions.pointer_action.pointer_down()
        self.actions.w3c_actions.pointer_action.move_to_location(540, 791)
        self.actions.w3c_actions.pointer_action.release()
        self.actions.perform()

    def launch_application_from_app_list(self):
        app = self.driver.find_element(MobileBy.XPATH, UiElements.trapadvisor_app_element)
        app.click()

    def _click_if_exists(self, element_id: str):
        try:
            btn = self.wait.until(
                EC.presence_of_element_located(
                    (MobileBy.ID, element_id)
                )
            )
            btn.click()
        except Exception:
            pass

    def skip_google_login_page(self):
        self._click_if_exists(UiElements.cancel_google_login_page)

    def skip_login_page(self):
        self._click_if_exists(UiElements.skip_trapadvisor_login_page)

    def skip_location_permission_page(self):
        self._click_if_exists(UiElements.skip_page_btn)

    def skip_notification_page(self):
        self._click_if_exists(UiElements.skip_page_btn)

    def launch(self):
        self.go_to_app_list()
        self.launch_application_from_app_list()
        self.skip_google_login_page()
        self.skip_login_page()
        self.skip_location_permission_page()
        self.skip_notification_page()

    class TrapAdvisorParser:
        def __init__(self, driver: webdriver.Remote):
            self.driver = driver
            self.wait = WebDriverWait(self.driver, 30)
            self.current_date = datetime.datetime.now()
            self.__app_runner = ApplicationRunner(self.driver)