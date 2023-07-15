import requests
from requests import get, post
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

lux_power_base_url = 'https://af.solarcloudsystem.com/WManage/'
lux_power_login_path = 'web/'
lux_power_inverter_data_path = 'api/inverter/'
lux_power_inverter_serial_number = '2413053854'

ha_base_url = 'http://192.168.18.153:8123/'
ha_action_path = 'api/webhook/'
ha_state_path = 'api/states/'

ha_long_lived_access_token = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3ODg2NzU1MmMzMmY0YjYzYjdkNmEyMjUwNmVlYzZjNSIsImlhdCI6MTY4ODgyOTkzMCwiZXhwIjoyMDA0MTg5OTMwfQ.HTaXzFFG4v8VJGGA4_OyjNseRU53v0p1KCO7FIizCKo'

wa_webhooks = {
    'ha-restart': '-LZ4NW6iFo6hRtiroRD9sqXVc',
    'turnOffHeater-chad': '-woLhqKHfe3SXezyloRyMRF5j',
    'getHeaterState-chad': 'switch.heater_socket_1',
    'luxPowerLogin': 'login',
    'luxInverterData': 'getInverterRuntime?'
}


def build_url(action):
    match action:
        case 'ha-restart':
            return ha_base_url + ha_action_path + wa_webhooks[action]
        case 'turnOffHeater-chad':
            return ha_base_url + ha_action_path + wa_webhooks[action]
        case 'getHeaterState-chad':
            return ha_base_url + ha_state_path + wa_webhooks[action]
        case 'luxPowerLogin':
            return lux_power_base_url + lux_power_login_path + wa_webhooks[action]
        case 'luxInverterData':
            return lux_power_base_url + lux_power_inverter_data_path + wa_webhooks[action]


def login():
    url = build_url('luxPowerLogin')
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'account': 'squareHome', 'password': 'Wilderness4'}
    sesh = requests.Session()
    sesh.post(url=url, data=payload, headers=headers)
    cookie_value = ''
    for cook in sesh.cookies:
        cookie_value = cook.value
    return cookie_value


def get_grid_wattage(cookie_value):
    url = build_url('luxInverterData')
    cookies = {'JSESSIONID': cookie_value}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'serialNum': lux_power_inverter_serial_number}

    post_response = post(url=url, data=payload, headers=headers, cookies=cookies)
    print('current grid usage: ', post_response.json()['pToUser'])
    return post_response.json()['pToUser']


def ha_restart():
    url = build_url('ha-restart')
    headers = {'Authorization': ha_long_lived_access_token}

    print('restarting homeAssistant ...')
    post_response = post(url=url, headers=headers)
    print(post_response)


def get_heater_state():
    url = build_url('getHeaterState-chad')
    headers = {
        'Authorization': ha_long_lived_access_token,
        'content-type': 'application/json'
    }

    response = get(url, headers=headers)
    print('current heater state: ' + response.json()['state'])
    return response.json()['state']


def turn_off_heater():
    url = build_url('turnOffHeater-chad')
    headers = {'Authorization': ha_long_lived_access_token}

    print('turning off the heater...')
    post_response = post(url=url, headers=headers)
    print('turning off the heater: ', post_response)


def inverter_guard():
    if get_grid_wattage(login()) == 0:
        turn_off_heater()


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(inverter_guard, 'interval', seconds=15, max_instances=1)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.shutdown()

