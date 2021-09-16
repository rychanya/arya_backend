import re
from parser.models import Counter
from parser.parsers import locators
from random import uniform
from time import sleep
from typing import Optional, Union

from bson.py3compat import reraise_instance
from pydantic import ValidationError
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from arya_backend.db.QA import QACRUD
from arya_backend.models.qa import QA, DragAnswer, JoinAnswer, ManyAnswer, OneAnswer


def random_sleep():
    sleep(uniform(0.1, 0.5))


def is_last_correct(
    last: Optional[Counter], curent: Optional[Counter]
) -> Optional[bool]:
    if not last or not curent:
        return
    unanswered_dif = last.unanswered - curent.unanswered
    if unanswered_dif != 1:
        return

    passed_dif = curent.passed - last.passed
    failed_dif = curent.failed - last.failed
    if passed_dif == 1 and failed_dif == 0:
        return True
    elif passed_dif == 0 and failed_dif == 1:
        return False
    else:
        return


def _wait_xpath(driver, xpath) -> Optional[WebElement]:
    try:
        return WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
    except TimeoutException:
        return


def get_counter(driver: WebDriver) -> Optional[Counter]:
    passed = _wait_xpath(driver, locators.STAT_PASSED)
    if passed is None:
        return
    failed = _wait_xpath(driver, locators.STAT_FAILED)
    if failed is None:
        return
    unanswered = _wait_xpath(driver, locators.STAT_UNANSWERED)
    if unanswered is None:
        return
    try:
        return Counter(
            passed=passed.text, failed=failed.text, unanswered=unanswered.text
        )
    except ValidationError:
        return


class QAEl:
    def __init__(self, driver: WebDriver) -> None:
        def filter_func(el: WebElement) -> bool:
            return el.is_displayed()

        self.driver = driver
        self.selected_answer: Union[
            OneAnswer, ManyAnswer, None, DragAnswer, JoinAnswer
        ] = None
        self.is_correct: Optional[bool] = None

        self.stat_counter = get_counter(self.driver)

        questions: list[WebElement] = WebDriverWait(self.driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "wtq-question"))
        )
        questions = list(filter(filter_func, questions))
        if not questions:
            raise ValueError
        self.el: WebElement = questions[0]
        self.answers_el: list[WebElement] = self.el.find_elements_by_class_name(
            "wtq-item-text-cell-main"
        )
        _type = self.el.find_element_by_class_name("wtq-q-instruction").text
        if _type == QA.type_enum.join:
            answers_text = list([a.text for a in self.answers_el])
            self.qa: QA = QA(
                question=self.el.find_element_by_class_name("wtq-q-question-text").text,
                answers=answers_text[0::2],
                extra_answers=answers_text[1::2],
                type=_type,
            )
        else:
            self.qa: QA = QA(
                question=self.el.find_element_by_class_name("wtq-q-question-text").text,
                answers=list([a.text for a in self.answers_el]),
                type=_type,
            )
        self.qa_from_db = QACRUD().load_or_create_complete_qa(self.qa)

    def wait_to_hide(self) -> Optional[bool]:
        if self.el is None:
            return
        try:
            WebDriverWait(self.el, 30).until_not(lambda el: el.is_displayed())
            return True
        except TimeoutException:
            return False

    def _select_answers(self):
        if isinstance(self.selected_answer, OneAnswer):
            for el in self.answers_el:
                if self.selected_answer == el.text:
                    el.click()
                    random_sleep()

        elif isinstance(self.selected_answer, ManyAnswer):
            for el in self.answers_el:
                if el.text in self.selected_answer:
                    el.click()
                    random_sleep()
        elif isinstance(self.selected_answer, DragAnswer):
            ac = ActionChains(self.driver)
            ac.drag_and_drop(self.answers_el[0], self.answers_el[1])
            ac.perform()
            list_answer = list(self.selected_answer)
            web_list_answer = list()
            n = 0
            while list_answer != web_list_answer:
                if n > 200:
                    self.selected_answer = None
                    break
                answers = self.el.find_elements_by_class_name("wtq-item-text-cell-main")
                web_list_answer = [el.text for el in answers]
                for i, el in enumerate(list_answer):
                    if web_list_answer[i] != el:
                        ac.drag_and_drop(answers[web_list_answer.index(el)], answers[i])
                        ac.perform()
                        # break

            # for i, ans in enumerate(self.selected_answer):
            #     self.answers_el: list[WebElement] = self.el.find_elements_by_class_name(
            #         "wtq-item-text-cell-main"
            #     )
            #     answers_text = [el.text for el in self.answers_el]
            #     web_index = answers_text.index(ans)
            #     if web_index != i:
            #         ac.drag_and_drop(self.answers_el[web_index], self.answers_el[i])
            #         ac.perform()
        elif isinstance(self.selected_answer, JoinAnswer):
            left = self.el.find_elements_by_xpath(locators.JOIN_LEFT)
            right = self.el.find_elements_by_xpath(locators.JOIN_RIGHT)
            ac = ActionChains(self.driver)
            ac.drag_and_drop(right[0], right[1])
            ac.perform()
            answer_dict = dict(self.selected_answer)
            web_answer_dict = dict()
            print(answer_dict)
            n = 0
            while answer_dict != web_answer_dict:
                n += 1
                if n > 200:
                    self.selected_answer = None
                    break
                left = self.el.find_elements_by_xpath(locators.JOIN_LEFT)
                right = self.el.find_elements_by_xpath(locators.JOIN_RIGHT)
                left_text: list[str] = [el.text for el in left]
                right_text: list[str] = [el.text for el in right]
                web_answer_dict = dict(zip(left_text, right_text))
                for k, v in answer_dict.items():
                    print(f"{k} {v} {web_answer_dict[k]} {v == web_answer_dict[k]}")
                for k, v in answer_dict.items():
                    if web_answer_dict[k] != v:
                        source = right[right_text.index(web_answer_dict[k])]
                        target = right[right_text.index(v)]
                        print(k, source.text, target.text)
                        ac.drag_and_drop(source, target)
                        ac.perform()
                        break
                sleep(3)
                # for i, el in enumerate(right_text):
                #     l_el = left_text[i]
                #     if web_answer_dict[l_el] != answer_dict[l_el]:
                #         cor = answer_dict[l_el]
                #         ac.drag_and_drop(right[right_text.index(cor)], right[i])
                #         ac.perform()
                #         break

        else:
            raise ValueError

    def answer(self):
        if self.qa_from_db:
            self.selected_answer = self.qa_from_db.get_answer()
            random_sleep()

            self._select_answers()

            random_sleep()

            btn = _wait_xpath(self.driver, locators.Q_SUBMIT_BTN)
            if btn:
                btn.click()
            else:
                raise ValueError
        else:
            raise ValueError

    def set_correct(self, new_counter: Optional[Counter]):
        self.is_correct = is_last_correct(self.stat_counter, new_counter)


class QAIter:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.curent: Optional[QAEl] = None
        self.last: Optional[QAEl] = None
        self.final = WebDriverWait(self.driver, 160).until(
            EC.presence_of_element_located((By.XPATH, locators.FINAL))
        )

    def __iter__(self):
        return self

    # def _close_rubrik(self, body: WebElement):
    #     rubric: WebElement = body.find_element_by_class_name("wtq-rubric")
    #     random_sleep()
    #     rubric.find_element_by_class_name("wtq-btn-next").click()
    #     WebDriverWait(rubric, 30).until_not(lambda: rubric.is_displayed())
    #     random_sleep()

    def __next__(self):

        if self.last and self.last.wait_to_hide():
            self.last.set_correct(get_counter(self.driver))
            if (
                self.last.selected_answer is not None
                and self.last.is_correct is not None
            ):
                QACRUD().add_result(
                    self.last.qa_from_db.id,
                    self.last.selected_answer,
                    self.last.is_correct,
                )

        if self.final.is_displayed():
            raise StopIteration

        self.curent = QAEl(self.driver)
        self.curent.answer()
        self.last = self.curent


class Run:
    def __init__(self, driver: WebDriver, url: str) -> None:
        self.driver = driver
        self.url = url
        self.driver.get(self.url)

    def __enter__(self):
        print(f"start test {self.url}")
        self.parent_window = self.driver.current_window_handle
        main = WebDriverWait(self.driver, 160).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "v-main"))
        )
        subtitle = WebDriverWait(main, 160).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "v-list-item__subtitle"))
        )
        button = WebDriverWait(subtitle, 160).until(
            EC.visibility_of_element_located((By.TAG_NAME, "button"))
        )
        WebDriverWait(button, 160).until(
            lambda d: button.text in ("ПРОДОЛЖИТЬ", "НАЗНАЧИТЬ", "НАЧАТЬ")
        )
        random_sleep()
        button.click()
        if button.text in ("ПРОДОЛЖИТЬ", "НАЧАТЬ"):
            self.driver.switch_to.window(self.driver.window_handles[-1])
            print("switch to test window")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        try:
            self.driver.close()
        except NoSuchWindowException:
            pass
        self.driver.switch_to.window(self.parent_window)
        print("switch to parent window")


class Login:
    def __init__(self, user_name, password, driver: WebDriver) -> None:
        self.driver: WebDriver = driver
        self.user_name = user_name
        self.password = password

    def __enter__(self):
        print("start login")
        self.driver.maximize_window()
        random_sleep()
        self.driver.get("https://mstudy.mvideo.ru/")
        wait = WebDriverWait(self.driver, 160)
        wait.until(EC.element_to_be_clickable((By.TAG_NAME, "form")))
        inputs = wait.until(
            EC.visibility_of_any_elements_located((By.TAG_NAME, "input"))
        )
        random_sleep()
        inputs[0].send_keys(self.user_name)
        random_sleep()
        inputs[1].send_keys(self.password)
        current_url = self.driver.current_url
        random_sleep()
        self.driver.find_elements_by_tag_name("button")[1].click()
        wait.until(EC.url_changes(current_url))
        print("logined")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.driver.quit()
