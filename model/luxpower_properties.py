class LuxPowerProperties:
    def __init__(self, config):
        self.base_url = config['luxPower'].get("baseUrl")
        self.login_path = config['luxPower'].get("loginPath")
        self.refresh_data_path = config['luxPower'].get("refreshInverterDataPath")
        self.inverter_data_path = config['luxPower'].get("inverterDataPath")
        self.serial_number = config['luxPower'].get("inverterSerialNumber")
        self.username = config['luxPower'].get("username")
        self.password = config['luxPower'].get("password")

    def __str__(self):
        return (f"LuxPowerProperties: 'base_url: {self.base_url}, login_path: {self.login_path},"
                f"refresh_data_path: {self.refresh_data_path}, inverter_data_path: {self.inverter_data_path},"
                f"serial_number: {self.serial_number}, username: {self.username}, password: {self.password}")

