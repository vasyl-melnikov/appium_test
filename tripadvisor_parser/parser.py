import calendar
import datetime
import time
from collections import Counter
from typing import Optional

from appium import webdriver
from appium.webdriver import WebElement
from appium.webdriver.common.mobileby import MobileBy

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tripadvisor_parser import NoDealsAvailableForDate, InvalidDate, DateRangeIsNotAvailable
from ui_elements import UiElements, Keys


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

    def _repeat_key(self, key, count_of_repetitions: int):
        for _ in range(count_of_repetitions):
            self.driver.press_keycode(key)

    def confirm_date_range(self):
        btn = self.driver.find_element(MobileBy.ID, UiElements.confirm_date_range_btn)
        btn.click()

    def go_to_date_range_page(self):
        btn = self.wait.until(
            EC.presence_of_element_located(
                (MobileBy.ID, UiElements.date_range_page_btn)
            )
        )
        btn.click()

    def back_form_deals_page(self):
        btn = self.driver.find_element(MobileBy.ID, UiElements.back_from_deals_page_btn)
        btn.click()

    def reset_search_page(self):
        for _ in range(2):
            self.go_to_search_page()

    def go_to_search_page(self):
        element = self.wait.until(
            EC.presence_of_element_located((MobileBy.ID, UiElements.search_page_btn))
        )
        element.click()

    def get_to_all_deals_page(self):
        try:
            btn = self.wait.until(
                EC.presence_of_element_located(
                    (MobileBy.ID, UiElements.all_deals_page_btn)
                )
            )
        except Exception:
            raise Exception
        btn.click()

    def seek_page_to_start(self):
        processed_titles = Counter()
        self._repeat_key(Keys.tab, 3)  # Move selector to date view

        date_title = self.driver.find_elements(MobileBy.ID, UiElements.cur_date_title)[
            -1
        ].text
        current_data_frame = (
            f"{calendar.month_name[self.current_date.month]} {self.current_date.year}"
        )
        while date_title != current_data_frame and processed_titles[date_title] <= 5:
            self.driver.press_keycode(Keys.arrow_up)
            processed_titles[date_title] += 1
            date_title = self.driver.find_elements(
                MobileBy.ID, UiElements.cur_date_title
            )[-1].text

        self._repeat_key(
            Keys.arrow_up, 2
        )  # Move selector a little below to load more data for specific month

        self._repeat_key(Keys.tab, 3)  # Move selector to date view

    def search_for_prompt(self, prompt: str):
        edit_text = self.wait.until(
            EC.presence_of_element_located(
                (MobileBy.ID, UiElements.search_page_edit_prompt)
            )
        )
        edit_text.click()

        time.sleep(1)  # sleeping 1 second for application to process actions

        edit_text = self.wait.until(
            EC.presence_of_element_located(
                (MobileBy.ID, UiElements.search_page_edit_prompt)
            )
        )
        edit_text.send_keys(prompt)

        self.driver.press_keycode(Keys.enter)  # clicking enter to start searching

    def click_on_second_found_option(self):
        elements = self.wait.until(
            EC.presence_of_all_elements_located(
                (MobileBy.ID, UiElements.search_result_object)
            )
        )
        elements[1].click()  # second object in list start is 1 index

    def _get_needed_day_from_date_view(
            self, search_date_of_view: str, needed_day: str, view_without_date: bool = False
    ) -> Optional[WebElement]:
        visible_views = self.driver.find_elements(
            MobileBy.ID, UiElements.month_view_object
        )
        for view in visible_views:
            try:
                date_title = view.find_element(MobileBy.ID, UiElements.cur_date_title)
            except Exception:
                if view_without_date:
                    needed_view = view
                    break
                continue
            if date_title.text == search_date_of_view:
                needed_view = view
                break
        days = needed_view.find_elements(MobileBy.ID, UiElements.day_txt)

        for day in days:
            if day.get_attribute("text") == needed_day:
                return day

    def find_needed_date(
            self, date: datetime.datetime, submit_date: bool = False
    ) -> None:
        """
        :param date: needed date to submit
        :param submit_date: parameter for submitting day as a first value (clicking twice on day entry)
        :return: None
        """
        if self.current_date > date:
            raise Exception

        # Trying to find wanted date frame view
        searched_date_frame = f"{calendar.month_name[date.month]} {date.year}"
        current_month_view = date.month == self.current_date.month
        if not current_month_view:
            date_title = self.driver.find_elements(
                MobileBy.ID, UiElements.cur_date_title
            )[-1].text
            while searched_date_frame != date_title:
                self.driver.press_keycode(Keys.arrow_down)
                date_title = self.driver.find_elements(
                    MobileBy.ID, UiElements.cur_date_title
                )[-1].text

        # Trying to find wanted day in date frame view
        needed_day = self._get_needed_day_from_date_view(
            searched_date_frame, str(date.day), view_without_date=current_month_view
        )
        while needed_day is None:
            self.driver.press_keycode(Keys.arrow_down)
            needed_day = self._get_needed_day_from_date_view(
                searched_date_frame, str(date.day), view_without_date=current_month_view
            )

        if submit_date:
            needed_day.click()
        needed_day.click()

        # Handling cases when date is not submitted or error popup appeared
        search_date = f"{calendar.month_abbr[date.month]} {date.day}"
        while (
                self.handle_invalid_date_range()
                or search_date
                not in self.driver.find_element(
            MobileBy.ID, UiElements.date_range_final_date
        ).get_attribute("text")
        ):
            needed_day.click()

    def parse_prices(self) -> dict[str, str]:
        time.sleep(10)  # sleeping 10s for data being loaded
        prices = {}

        while True:
            self.driver.press_keycode(Keys.tab)
            focused_elem = self.driver.switch_to.active_element
            if (
                focused_elem.get_attribute("resource-id")
                != UiElements.hotel_offer_object
            ):
                continue
            try:
                provider_name = focused_elem.find_element(
                    MobileBy.ID, UiElements.hotel_offer_provider
                ).text
            except Exception:
                continue

            try:
                price = focused_elem.find_element(
                    MobileBy.ID, UiElements.hotel_offer_price
                ).text
            except Exception:
                price = "Not Available"

            if provider_name in prices:  # verifying whether provider is already in prices dict
                break
            prices[provider_name] = price
        return prices

    def get_to_all_deals_page(self):
        try:
            btn = self.wait.until(
                EC.presence_of_element_located(
                    (MobileBy.ID, UiElements.all_deals_page_btn)
                )
            )
        except Exception:
            raise NoDealsAvailableForDate
        btn.click()

    def launch_app_and_parse_data(self, prompt: str, start_date: datetime.datetime, end_date: datetime.datetime) -> \
    dict[str, str]:
        self.__app_runner.launch()
        self.go_to_search_page()
        self.search_for_prompt(prompt)
        self.click_on_second_found_option()
        self.go_to_date_range_page()
        self.seek_page_to_start()

        try:
            self.find_needed_date(start_date, submit_date=True)
            self.find_needed_date(end_date)
        except Exception:
            prices = f"Such date range is not available {start_date} to {end_date}"
            self.confirm_date_range()
            self.reset_search_page()
            return prices

        self.confirm_date_range()
        try:
            self.get_to_all_deals_page()
        except Exception:
            prices = f"Deals for such date range are not available {start_date} to {end_date}"
        else:
            prices = self.parse_prices()
            self.back_form_deals_page()
        self.reset_search_page()
        return prices


    def __del__(self):
        self.driver.quit()