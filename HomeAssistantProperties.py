class HomeAssistantProperties:
    def __init__(self, config):
        self.base_url = config['homeAssistant'].get("baseUrl")
        self.access_token = config['homeAssistant'].get("accessToken")
        self.heater_url = config['homeAssistant'].get("heaterTurnOffEndpoint")

    def __str__(self):
        return f"base_url: {self.base_url}, access_token: {self.access_token}, heater_url: {self.heater_url}"
