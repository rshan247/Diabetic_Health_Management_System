import pandas as pd
from datetime import datetime
import insulin_usage_chart as insulin_utilization


def calculate_isf(actual_bs_reduction, active_insulin):
    if active_insulin == 0:
        return None
    return round(actual_bs_reduction / active_insulin, 2)

def estimate_blood_sugar_increase(carbs):
    return carbs * 4

def calculate_food_carbs(food, food_data):
    quantity = 1
    if food[0].isdigit():
        quantity, food = food.split()
        quantity = int(quantity)
        # print(quantity, food)
    return quantity * food_data.loc[food_data["Food"] == food, "Carbohydrates (g)"].values[0]


def time_diff_from_insulin_intake(row):
    time_format = "%H:%M"
    if row['Pre-Meal Sugar Time'] is None:
        return 0
    else:
        pre_meal_sugar_time = datetime.strptime(row['Pre-Meal Sugar Time'], time_format)
        insulin_intake_time = datetime.strptime(row['Insulin Intake Time'], time_format)

        time_diff = (pre_meal_sugar_time - insulin_intake_time)
        print(pre_meal_sugar_time, insulin_intake_time, time_diff)

        # if time_diff.total_seconds() < 0:
        #     return 0

        hours_diff = round(time_diff.total_seconds() / 3600, 1)
        print(hours_diff)

        return hours_diff

def update_row(df, index, food_df):
    row = df.iloc[index]
    total_carbs = 0
    if row['Food Consumed']:
        food_items = row['Food Consumed'].split(",") if row['Food Consumed'] != "None" else []
        # print(food_items)

        for food in food_items:
            total_carbs += calculate_food_carbs(food, food_data)
        print("Total carbs: ", total_carbs)

    expected_bs_increase = estimate_blood_sugar_increase(total_carbs)

    actual_bs_reduction = row['Pre-Meal Blood Sugar (mg/dL)'] + expected_bs_increase - row['Post-Meal Blood Sugar (mg/dL)']

    time_after_insulin = time_diff_from_insulin_intake(row) + row['Time After Meal (hrs)']

    active_insulin = round(insulin_utilization.get_insulin_usage(row['Insulin Dosage (units)'], time_after_insulin, True), 2)
    print("Active insulin:", active_insulin)

    insulin_to_reduce = round(insulin_utilization.get_insulin_usage(row['Insulin Dosage (units)'], time_diff_from_insulin_intake(row), True), 2)
    print("Insulin to be reduced:", insulin_to_reduce)

    isf = calculate_isf(actual_bs_reduction, active_insulin - insulin_to_reduce)

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

if __name__ == "__main__":
    food_data = pd.read_csv("..\Datasets\Food_Dataset.csv")
    isf_data = pd.read_csv("..\Datasets\ISF.csv")
    isf_data['Food Consumed'] = isf_data['Food Consumed'].fillna("")

    isf_data = update_row(isf_data, 3, food_data)
    pd.set_option('display.max_columns', None)
    print(isf_data)
    isf_data.to_csv("..\Datasets\ISF.csv", index=False)


