import pandas as pd
from datetime import datetime
import insulin_usage_chart as insulin_utilization

food_data = pd.read_csv("..\Datasets\Food_Dataset.csv")
isf_data = pd.read_csv("..\Datasets\ISF.csv")

def calculate_isf(actual_bs_reduction, active_insulin):
    if active_insulin == 0:
        return None
    return actual_bs_reduction / active_insulin

def estimate_blood_sugar_increase(carbs):
    return carbs * 4

def calculate_food_carbs(food):
    quantity = 1
    if food[0].isdigit():
        quantity, food = food.split()
        quantity = int(quantity)
        # print(quantity, food)
    return quantity * food_data.loc[food_data["Food"] == food, "Carbohydrates (g)"].values[0]
def update_row(df, index, food_df):
    row = df.iloc[index]

    food_items = row['Food Consumed'].split(",")
    # print(food_items)
    total_carbs = 0
    for food in food_items:
        total_carbs += calculate_food_carbs(food)
    # print(total_carbs)

    expected_bs_increase = estimate_blood_sugar_increase(total_carbs)

    actual_bs_reduction = row['Pre-Meal Blood Sugar (mg/dL)'] + expected_bs_increase - row['Post-Meal Blood Sugar (mg/dL)']

    active_insulin = insulin_utilization.plot_insulin_curve(30, 5, 2, 10, row['Time After Meal (hrs)'], False)

    isf = calculate_isf(actual_bs_reduction, active_insulin)

    df.at[index, 'Carbohydrates (g)'] = total_carbs
    df.at[index, 'Expected Blood Sugar Increase (mg/dL)'] = expected_bs_increase
    df.at[index, 'Actual Blood Sugar Reduction (mg/dL)'] = actual_bs_reduction
    df.at[index, 'Active Insulin (units)'] = 30 - active_insulin
    df.at[index, 'Calculated ISF (mg/dL per unit)'] = isf

    cur_date_time = datetime.now()
    cur_date = cur_date_time.strftime("%m/%d/%Y")
    cur_time = cur_date_time.strftime("%H:%M")

    df.at[index, 'Date'] = cur_date
    df.at[index, 'Time'] = cur_time

    return df


isf_data = update_row(isf_data, 1, food_data)
isf_data.to_csv("..\Datasets\ISF.csv", index=False)
pd.set_option('display.max_columns', None)
print(isf_data)

