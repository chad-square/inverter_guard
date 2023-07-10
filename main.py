import requests
from requests import get, post
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def login():
    url = "https://af.solarcloudsystem.com/WManage/web/login"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    payload = {
        'account': 'squareHome',
        'password': 'Wilderness4'
    }
    sesh = requests.Session()
    sesh.post(url=url, data=payload, headers=headers)
    cookie_value = ''
    for cook in sesh.cookies:
        cookie_value = cook.value
    return cookie_value


def get_grid_wattage(cookie_value):
    cookies = {'JSESSIONID': cookie_value}
    url = "https://af.solarcloudsystem.com/WManage/api/inverter/getInverterRuntime?"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        "serialNum": "2413053854"
    }
    post_response = post(url=url, data=payload, headers=headers, cookies=cookies)
    print('current grid usage: ', post_response.json()['pToUser'])
    return post_response.json()['pToUser']


def get_heater_state():
    url = "http://192.168.18.69:8123/api/states/switch.heater_socket_1"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3ODg2NzU1MmMzMmY0YjYzYjdkNmEyMjUwNmVlYzZjNSIsImlhdCI6MTY4ODgyOTkzMCwiZXhwIjoyMDA0MTg5OTMwfQ.HTaXzFFG4v8VJGGA4_OyjNseRU53v0p1KCO7FIizCKo",
        "content-type": "application/json"
    }
    response = get(url, headers=headers)
    print('current heater state: ' + response.json()['state'])
    return response.json()['state']


def turn_off_heater():
    url = "http://192.168.18.69:8123/api/webhook/-woLhqKHfe3SXezyloRyMRF5j"
    headers = {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3ODg2NzU1MmMzMmY0YjYzYjdkNmEyMjUwNmVlYzZjNSIsImlhdCI6MTY4ODgyOTkzMCwiZXhwIjoyMDA0MTg5OTMwfQ.HTaXzFFG4v8VJGGA4_OyjNseRU53v0p1KCO7FIizCKo",
    }

    post_response = post(url=url, headers=headers)
    print(post_response.text)


def inverter_guard():
    if get_heater_state == 'on':
        current_grid_wattage = get_grid_wattage(login())
        if current_grid_wattage == 0:
            turn_off_heater()


if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(inverter_guard, 'interval', seconds=30, max_instances=1)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        scheduler.shutdown()


