from vending_machine.coffee_vending_machine import Machine


class TestCoffeeMachine:

    def __init__(self):
        self.machine = None

    def setup(self):

        outlet = {
            "count_n": 3
        }

        total_item_quantity = {
            "hot_water": 500,
            "hot_milk": 500,
            "ginger_syrup": 100,
            "sugar_syrup": 100,
            "tea_leaves_syrup": 100
        }

        low_threshold = 45
        self.machine = Machine(outlet, total_item_quantity, low_threshold)

    def test_dispense(self):

        beverages = {
            "hot_tea": {
                "hot_water": 200,
                "hot_milk": 100,
                "ginger_syrup": 10,
                "sugar_syrup": 10,
                "tea_leaves_syrup": 30
            },
            "hot_coffee": {
                "hot_water": 100,
                "ginger_syrup": 30,
                "hot_milk": 400,
                "sugar_syrup": 50,
                "tea_leaves_syrup": 30
            },
            "black_tea": {
                "hot_water": 300,
                "ginger_syrup": 30,
                "sugar_syrup": 50,
                "tea_leaves_syrup": 30
            },
            "green_tea": {
                "hot_water": 100,
                "ginger_syrup": 30,
                "sugar_syrup": 50,
                "green_mixture": 30
            }
        }

        combined_output = self.machine.fulfill_beverage_dispense_request(beverages)
        return combined_output

    def tear_down(self):
        self.machine = None


def __main__():
    test = TestCoffeeMachine()
    test.setup()
    combined_output = test.test_dispense()
    print(combined_output)
    test.tear_down()


if __name__ == "__main__":
    __main__()