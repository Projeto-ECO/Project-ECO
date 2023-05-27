# Generated by Selenium IDE
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class TestDeposit():
  def setup_method(self, method):
    self.driver = webdriver.Chrome()
    self.vars = {}
  
  def teardown_method(self, method):
    self.driver.quit()
  
  def test_deposit(self):
    # Test name: Deposit
    # Step # | name | target | value
    # 1 | open | / | 
    self.driver.get("http://192.168.1.64:6070/")
    # 2 | setWindowSize | 1920x1080 | 
    self.driver.set_window_size(1920, 1080)
    # 3 | click | css=.btn:nth-child(1) > .flex | 
    self.driver.find_element(By.CSS_SELECTOR, ".btn:nth-child(1) > .flex").click()
    # 4 | click | name=username | 
    self.driver.find_element(By.NAME, "username").click()
    # 5 | type | name=username | Eco
    self.driver.find_element(By.NAME, "username").send_keys("Eco")
    # 6 | type | name=password | 123
    self.driver.find_element(By.NAME, "password").send_keys("123")
    # 7 | click | css=.login100-form-btn | 
    self.driver.find_element(By.CSS_SELECTOR, ".login100-form-btn").click()
    # 8 | click | name=code | 
    self.driver.find_element(By.NAME, "code").click()
    # 9 | type | name=code | 730981
    self.driver.find_element(By.NAME, "code").send_keys("730981")
    # 10 | click | css=.login100-form-btn | 
    self.driver.find_element(By.CSS_SELECTOR, ".login100-form-btn").click()
    # 11 | click | css=.checkbox | 
    self.driver.find_element(By.CSS_SELECTOR, ".checkbox").click()
    # 12 | click | id=deposit-button | 
    self.driver.find_element(By.ID, "deposit-button").click()
    # 13 | click | id=coin-deposit | 
    self.driver.find_element(By.ID, "coin-deposit").click()
    # 14 | type | id=coin-deposit | 0.02
    self.driver.find_element(By.ID, "coin-deposit").send_keys("0.02")
    # 15 | click | id=amount-deposit | 
    self.driver.find_element(By.ID, "amount-deposit").click()
    # 16 | type | id=amount-deposit | 56
    self.driver.find_element(By.ID, "amount-deposit").send_keys("56")
    # 17 | click | css=#deposit-form > button | 
    self.driver.find_element(By.CSS_SELECTOR, "#deposit-form > button").click()
    # 18 | click | css=.checkbox | 
    self.driver.find_element(By.CSS_SELECTOR, ".checkbox").click()
    # 19 | click | id=deposit-button | 
    self.driver.find_element(By.ID, "deposit-button").click()
    # 20 | click | id=coin-deposit | 
    self.driver.find_element(By.ID, "coin-deposit").click()
    # 21 | type | id=coin-deposit | 3
    self.driver.find_element(By.ID, "coin-deposit").send_keys("3")
    # 22 | click | id=amount-deposit | 
    self.driver.find_element(By.ID, "amount-deposit").click()
    # 23 | type | id=amount-deposit | 23
    self.driver.find_element(By.ID, "amount-deposit").send_keys("23")
    # 24 | click | css=#deposit-form > button | 
    self.driver.find_element(By.CSS_SELECTOR, "#deposit-form > button").click()
    # 25 | click | css=.line1 | 
    self.driver.find_element(By.CSS_SELECTOR, ".line1").click()
    # 26 | click | css=.checkbox | 
    self.driver.find_element(By.CSS_SELECTOR, ".checkbox").click()
    # 27 | click | id=deposit-button | 
    self.driver.find_element(By.ID, "deposit-button").click()
    # 28 | click | id=coin-deposit | 
    self.driver.find_element(By.ID, "coin-deposit").click()
    # 29 | type | id=coin-deposit | 4
    self.driver.find_element(By.ID, "coin-deposit").send_keys("4")
    # 30 | type | id=amount-deposit | 3.9
    self.driver.find_element(By.ID, "amount-deposit").send_keys("3.9")
    # 31 | click | css=#deposit-form > button | 
    self.driver.find_element(By.CSS_SELECTOR, "#deposit-form > button").click()
  
