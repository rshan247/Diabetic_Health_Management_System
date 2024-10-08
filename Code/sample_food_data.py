import pandas as pd
import insulin_usage_chart as insulin_utilization

food_data = pd.read_csv("..\Datasets\Food_Dataset.csv")
# print(food_data.head())

isf_data = pd.read_csv("..\Datasets\ISF.csv")

# carbs = food_data.loc[food_data["Food"] == "Dosa", "Carbohydrates (g)"]
# print(carbs)
# print(carbs.values)
# print(carbs.values.size)

def food_quantity(food):
    quantity = 1
    if food[0].isdigit():
        quantity, food = food.split()
        food = food.replace("-", " ")
    try:
        return int(quantity), food
    except ValueError:
        return float(quantity), food

def calculate_carbohydrate(food_items):
    total_carbs = 0
    for food in food_items:
        quantity, food = food_quantity(food)
        carbs = food_data.loc[food_data["Food"] == food, "Carbohydrates (g)"].values
        print(f"{food} contains {carbs}g of carbs")
        total_carbs += quantity * carbs[0]
    print(f"Total carbs: {total_carbs}")
    return total_carbs

def estimate_blood_sugar_increase(carbs):
    return carbs * 4

def calculate_insulin_effect(insulin_unit, isf):
    return insulin_unit * isf

def estimate_current_blood_sugar(pre_meal_sugar, food_items, time_after_meal,  time_after_insulin):
    carbs = calculate_carbohydrate(food_items, food_data)
    sugar_increase = estimate_blood_sugar_increase(carbs)
    print(f"Sugar increased by food: {sugar_increase}")
    print(f"Total blood sugar: {pre_meal_sugar + sugar_increase}")

    isf = isf_data['Calculated ISF (mg/dL per unit)'].mean()
    active_insulin = insulin_utilization.get_insulin_usage(30,time_after_insulin, False)
    insulin_to_reduce = insulin_utilization.get_insulin_usage(30, time_after_insulin - time_after_meal,False)
    print(insulin_to_reduce, active_insulin)
    insulin_effect = calculate_insulin_effect(active_insulin - insulin_to_reduce, isf)

    print("Insulin effect: ", insulin_effect)
    post_meal_sugar = pre_meal_sugar + sugar_increase - insulin_effect
    print(f"Pre meal sugar{pre_meal_sugar} + sugar increase{sugar_increase} - insulin effect{insulin_effect} is...")

    return post_meal_sugar

if __name__ == "__main":
    pre_meal_sugar = 50 # 322  # mg/dL
    food_items = ['2 Laddu', 'Vegetable Biryani']
    insulin_dosage = 30  # units
    time_after_meal = 3 # 1.5
    time_after_insulin = 3 # 4.5  # hours


    # Calculate current blood sugar level
    current_sugar_level = estimate_current_blood_sugar(pre_meal_sugar, food_items, time_after_meal, time_after_insulin)

    print(f'Estimated Blood Sugar Level: {current_sugar_level:.2f} mg/dL')