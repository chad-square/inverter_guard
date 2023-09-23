class InverterData:
    def __init__(self, grid_import: int, solar_yield: int, battery_soc: int, backup_power_usage: int,
                 normal_consumption: int):
        self.grid_import = grid_import
        self.solar_yield = solar_yield
        self.battery_soc = battery_soc
        self.backup_power_usage = backup_power_usage
        self.off_grid_home_demand = normal_consumption

    def __str__(self) -> str:
        return (f"InverterData: grid_import: {self.grid_import}, solar_yield: {self.solar_yield}, batter_soc: "
                f"{self.battery_soc}, backup_power_usage: {self.backup_power_usage}, off_grid_home_demand: "
                f"{self.off_grid_home_demand}")


