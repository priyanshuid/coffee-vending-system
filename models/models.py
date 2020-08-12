import threading


class IngredientReserve:

    def __init__(self, ingredients: dict, low_threshold: int):
        self.lock = threading.Lock()
        self.ingredients = ingredients
        self.low_threshold = low_threshold

    def use_ingredient(self, name, quantity):

        self.lock.acquire()
        return_val = 0
        # no such ingredient
        try:
            if name not in self.ingredients.keys():
                return_val = -1
            # not sufficient ingredient
            if self.ingredients[name] < quantity:
                # not returning here in order to release lock
                return_val = -2
            # ok used ingredient return 0
            self.ingredients[name] = self.ingredients[name] - quantity
        finally:
            self.lock.release()
        return return_val

    def indicate_low_ingredients(self):

        low_on_vol_ingredients = list()

        for name in self.ingredients:
            if self.ingredients[name] < self.low_threshold:
                low_on_vol_ingredients.append({name: self.ingredients[name]})

        if len(low_on_vol_ingredients) == 0:
            return {"status": "NO INGREDIENTS LOW", "ingredients": []}

        return {"status": "SOME INGREDIENTS LOW", "ingredients": low_on_vol_ingredients}

