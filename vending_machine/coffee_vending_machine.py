from models.models import IngredientReserve
import threading
import queue

DEFAULT_LOW_THRESHOLD = 40


class Outlet:

    def __init__(self, count_n):
        self.count_n = count_n


class Machine:

    def __init__(self, outlet: dict, total_items_quantity: dict, low_threshold=DEFAULT_LOW_THRESHOLD):
        self.outlets = Outlet(outlet["count_n"])
        # all quantities in ML
        self.item_reserve = IngredientReserve(total_items_quantity, low_threshold)
        self.beverage_configurations = dict()

    def fulfill_beverage_dispense_request(self, beverage_requests: dict):
        # to track number of beverages that were dispensed
        # 
        dispensed_beverages = 0
        combined_status = []
        beverage_remained = False
        for beverage_name in beverage_requests:
            # check if the current number of beverages served is less than or equal to outlet count of the machine
            if dispensed_beverages >= self.outlets.count_n:
                beverage_remained = True
                break
            ingredients = beverage_requests[beverage_name]
            status_dict = self.__dispense_beverage(ingredients)

            if status_dict["message"] == "DISPENSED":
                dispensed_beverages += 1
                combined_status.append("{0} is prepared".format(beverage_name))
            elif status_dict["message"] == "UNFULFILLED":
                combined_status.append("{0} cannot be prepared because {1}".format(beverage_name,
                                                                                   status_dict["reason"]))
        if beverage_remained:
            combined_status.append("Could not prepare remaining beverages, "
                                   "as only N beverages can be prepared in one dispense. Request again.")
        return combined_status

    def fulfill_beverage_concurrent(self, beverage_request: dict):

        beverage_list = [{"name": beverage_name,
                          "ingredients": beverage_request[beverage_name]} for beverage_name in beverage_request.keys()]
        index = 0
        combined_results = [None] * len(beverage_list)
        combined_output = list()
        while index < len(beverage_list):
            # number of threads at once = min(outlet_count, remaining_items)
            threads = [None] * (min(index + self.outlets.count_n, len(beverage_request)) - index + 1)
            counter = 0
            for ind in range(index, min(index + self.outlets.count_n, len(beverage_request))):
                bev = beverage_list[ind]["name"]
                ingredients = beverage_list[ind]["ingredients"]
                threads[counter] = threading.Thread(target=self.__dispense_beverage,
                                                    args=(ingredients, combined_results, ind))
                threads[counter].start()
                counter = counter + 1
                index = index + 1
            counter = 0
            for ind in range(index, min(index + self.outlets.count_n, len(beverage_request))):
                threads[counter].join()
                counter = counter + 1

        for index in range(0, len(beverage_list)):
            bev_name = beverage_list[index]["name"]
            status_dict = combined_results[index]
            if status_dict is None:
                continue
            if status_dict["message"] == "DISPENSED":
                combined_output.append("{0} is prepared".format(bev_name))
            elif status_dict["message"] == "UNFULFILLED":
                combined_output.append("{0} cannot be prepared because {1}".format(bev_name,
                                                                                   status_dict["reason"]))
        return combined_output

    def __dispense_beverage(self, ingredients, results=None, index=None):

        status_dict = dict()
        # check if ingredient is available
        for ingredient in ingredients:
            if ingredient not in self.item_reserve.ingredients.keys():
                status_dict["message"] = "UNFULFILLED"
                status_dict["reason"] = "{} is not available".format(ingredient)
                if results is not None:
                    results[index] = status_dict
                    return
                return status_dict
        # check if ingredient is sufficient
        for ingredient in ingredients:
            if ingredients[ingredient] > self.item_reserve.ingredients[ingredient]:
                status_dict["message"] = "UNFULFILLED"
                status_dict["reason"] = "{} is not sufficient".format(ingredient)
                if results is not None:
                    results[index] = status_dict
                    return
                return status_dict
        # dispense
        for ingredient in ingredients:
            # object level lock on item_reserve
            success = self.item_reserve.use_ingredient(ingredient, ingredients[ingredient])
            if success != 0:
                status_dict["message"] = "UNFULFILLED"
                status_dict["reason"] = "{} is not sufficient".format(ingredient)
                break

        status_dict["message"] = "DISPENSED"
        status_dict["reason"] = None
        if results is None:
            return status_dict
        results[index] = status_dict



