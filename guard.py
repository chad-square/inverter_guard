import os
import signal
import threading

import sys
import requests
from requests import post

from model.inverterData import InverterData
from model.HomeAssistantProperties import HomeAssistantProperties
from model.luxpower_properties import LuxPowerProperties


class Guard:
    content_type = 'Content-Type'
    app_url_form_en = 'application/x-www-form-urlencoded'
    account = 'account'
    password = 'password'
    j_session_id = 'JSESSIONID'
    inverterSn = 'inverterSn'
    index = 'index'
    serialNum = 'serialNum'
    authorization = 'Authorization'

    def __init__(self, config):
        self.lux_cookie = ''
        self.luxPower_config = LuxPowerProperties(config)
        self.home_assistant_config = HomeAssistantProperties(config)

    def run_guard(self):

        if len(self.lux_cookie) == 0:
            self.login()

        try:
            self.refresh_inverter_data()
            inverter_data = self.get_inverter_data()
            print(inverter_data)

            # using backup power aka batteries
            if inverter_data.backup_power_usage > 0:
                print("Using backup power, turning off heater")
                print("inverterData.backupPowerUsage: " + inverter_data.backup_power_usage.__str__())
                self.turn_off_heater()

            # if current solar yield is less than what the household needs
            if inverter_data.solar_yield <= inverter_data.off_grid_home_demand and inverter_data.grid_import == 0:
                print("Solar yield is too low, turning off heater")
                print(f"inverterData.solar: {inverter_data.solar_yield},"
                      f" inverterData.homeInverterDemand: {inverter_data.off_grid_home_demand}, "
                      f"inverterData.gridImport: {inverter_data.grid_import}")
                self.turn_off_heater()

            print("--------------------------------------------------------------------------------------------------------------\n")

        except Exception as e:
            print(e)
            self.login()
            self.run_guard()

    def login(self) -> None:
        print('logging in...')

        url = self.luxPower_config.base_url + self.luxPower_config.login_path
        headers = {self.content_type: self.app_url_form_en}
        payload = {self.account: self.luxPower_config.username, self.password: self.luxPower_config.password}

        sesh = requests.Session()
        sesh.post(url=url, data=payload, headers=headers)
        with threading.Lock():
            self.lux_cookie = sesh.cookies.get('JSESSIONID')

    def refresh_inverter_data(self) -> None:
        print('refresh_inverter_data...')
        url = self.luxPower_config.base_url + self.luxPower_config.refresh_data_path
        cookies = {self.j_session_id: self.lux_cookie}
        headers = {self.content_type: self.app_url_form_en}

        try:
            payload = {
                self.inverterSn: self.luxPower_config.serial_number,
                self.index: 1
            }

            post(url=url, data=payload, headers=headers, cookies=cookies)
        except Exception as e:
            print(f'Exception thrown while refreshing with index: 1, {e}')
            self.login()
            raise

        try:
            payload = {
                self.inverterSn: self.luxPower_config.serial_number,
                self.index: 2
            }

            post(url=url, data=payload, headers=headers, cookies=cookies)
        except Exception as e:
            print(f'Exception thrown while refreshing with index: 2, {e}')
            self.login()
            raise

        try:
            payload = {
                self.inverterSn: self.luxPower_config.serial_number,
                self.index: 3
            }

            post(url=url, data=payload, headers=headers, cookies=cookies)
        except Exception as e:
            print(f'Exception thrown while refreshing with index: 3, {e}')
            self.login()
            raise

    def get_inverter_data(self) -> InverterData:
        url = self.luxPower_config.base_url + self.luxPower_config.inverter_data_path
        cookies = {self.j_session_id: self.lux_cookie}
        headers = {self.content_type: self.app_url_form_en}
        payload = {self.serialNum: self.luxPower_config.serial_number}

        try:
            post_response = post(url=url, data=payload, headers=headers, cookies=cookies)
            if post_response.json()['success'] is False and post_response.json()['msgCode'] == 151:
                print(post_response.json())
                os.kill(os.getpid(), signal.SIGUSR1)
            return InverterData(post_response.json()['pToUser'], post_response.json()['ppv'],
                                post_response.json()['soc'], post_response.json()['peps'], post_response.json()['pinv'])
        except Exception as e:
            print(f'Exception thrown while getting grid wattage, {e}')
            self.login()
            self.get_inverter_data()

    def turn_off_heater(self) -> None:
        url = self.home_assistant_config.base_url + self.home_assistant_config.heater_url
        headers = {self.authorization: self.home_assistant_config.access_token}

        print('turning off the heater...')
        post_response = post(url=url, headers=headers)
        print(f'turning off the heater: {post_response}\n')
