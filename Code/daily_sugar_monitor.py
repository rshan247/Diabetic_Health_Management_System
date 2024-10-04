import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import insulin_usage_chart as insulin_utilization


isf_df = pd.read_csv("..\Datasets\ISF.csv")
daily_log_df = pd.read_csv("..\Datasets\daily_sugar_log.csv")
# daily_log_df_date_str = daily_log_df['Date']
daily_log_df['Date'] = pd.to_datetime(daily_log_df['Date'])#, format = '%m/%d/%Y')


daily_insulin_log =pd.read_csv("..\Datasets\daily_insulin_log.csv")
daily_insulin_log['Date'] = pd.to_datetime(daily_insulin_log['Date'], format='%m/%d/%Y')
daily_insulin_log['Morning Insulin Time'] = pd.to_datetime(daily_insulin_log['Morning Insulin Time'], format='%m/%d/%Y %H:%M')
daily_insulin_log['Night Insulin Time'] = pd.to_datetime(daily_insulin_log['Night Insulin Time'], format='%m/%d/%Y %H:%M')
# print(daily_log_df.head())


# event = daily_log_df[((daily_log_df['Event'] == 'Food') | (daily_log_df['Event'] == 'Snack')) & (daily_log_df['Blood Sugar (mg/dl)'].isna())]
# print(event)


def get_insulin(time, morning_insulin_time, morning_finish_time, night_insulin_time, night_finish_time, mi_units, ni_units):
    time_from_morning = round((time - morning_insulin_time).total_seconds() / 3600, 1)
    print("Time to reduce", time_from_morning)
    time_from_night = round((time - night_insulin_time).total_seconds() / 3600, 1)

    if morning_insulin_time <= time <= morning_finish_time and night_insulin_time <= time <= night_finish_time:
        print("Both")
        cummulative_morning_insulin = insulin_utilization.get_insulin_usage(mi_units, time_from_morning, False)
        cummulative_night_insulin = insulin_utilization.get_insulin_usage(ni_units, time_from_night, False)
        insulin_left = (mi_units - cummulative_morning_insulin) + (ni_units - cummulative_night_insulin)
        print("insulin_to_reduce:", cummulative_night_insulin + cummulative_morning_insulin)
        return "Both", cummulative_morning_insulin + cummulative_night_insulin, insulin_left
    elif morning_insulin_time <= time <= morning_finish_time and time < night_insulin_time:
        print("Morning")
        cummulative_morning_insulin = insulin_utilization.get_insulin_usage(mi_units, time_from_morning, False)
        insulin_left = mi_units - cummulative_morning_insulin
        print("insulin_to_reduce:", cummulative_morning_insulin)
        return "Morning", cummulative_morning_insulin, insulin_left
    elif night_insulin_time <= time <= night_finish_time and time > morning_finish_time:
        print("Night")
        cummulative_night_insulin = insulin_utilization.get_insulin_usage(ni_units, time_from_night, False)
        insulin_left = ni_units - cummulative_night_insulin
        print("insulin_to_reduce:", cummulative_night_insulin)
        return "Night", cummulative_night_insulin, insulin_left
    return "",0, 0

def calculate_active_insulin(cur_date, cur_time, last_sugar_time):
    print("Cur date:", cur_date)
    print("Cur Time:", cur_time)

    # print(daily_insulin_log[daily_insulin_log['Date'] == cur_date])
    morning_insulin_time = daily_insulin_log[daily_insulin_log['Date'] == cur_date]['Morning Insulin Time'].values[0]
    morning_insulin_time_dt = pd.Timestamp(morning_insulin_time)
    morning_insulin_finish_time = morning_insulin_time + pd.Timedelta(hours=12)
    print("Morning:", morning_insulin_time_dt, "to", morning_insulin_finish_time)

    night_insulin_time = daily_insulin_log[daily_insulin_log['Date'] == cur_date]['Night Insulin Time'].values[0]
    night_insulin_time_dt = pd.Timestamp(night_insulin_time)
    night_insulin_finish_time = night_insulin_time + pd.Timedelta(hours=12)
    print("Night:", night_insulin_time_dt, "to",  night_insulin_finish_time)

    mi_units = daily_insulin_log[daily_insulin_log['Date'] == cur_date]['Morning Insulin Dosage (units)'].values[0]
    ni_units = daily_insulin_log[daily_insulin_log['Date'] == cur_date]['Night Insulin Dosage (units)'].values[0]

    print("Last sugar time:", last_sugar_time)
    coverage_reduce, insulin_to_reduced, _ = get_insulin(last_sugar_time, morning_insulin_time_dt, morning_insulin_finish_time, night_insulin_time_dt, night_insulin_finish_time, mi_units, ni_units)
    print("Current sugar time:", cur_time)
    coverage_active, active_insulin, insulin_left = get_insulin(cur_time, morning_insulin_time_dt, morning_insulin_finish_time, night_insulin_time_dt, night_insulin_finish_time, mi_units, ni_units)

    if (((coverage_reduce == "Both" and coverage_active == "Morning") or (coverage_reduce == "Both" and coverage_active == "Night"))
    or ((coverage_reduce == "Morning" and coverage_active == "Night") or (coverage_reduce == "Night" and coverage_active == "Morning"))):
        active_insulin += mi_units if coverage_active == "Night" else ni_units

    if coverage_active == "" and coverage_reduce == "Morning":
        active_insulin += mi_units
    if coverage_active == "" and coverage_reduce == "Night":
        active_insulin += ni_units

    print("Insulins:", active_insulin, insulin_to_reduced)
    return round(active_insulin - insulin_to_reduced, 2), round(insulin_left, 2)


def update_blood_sugar_log(df, event_time, food_carbs, isf):
    current_time = event_time.split()
    date_str = current_time[0]
    date = datetime.strptime(date_str, "%m/%d/%Y")
    # date_str = datetime.strftime(date, "%m/%d/%Y")
    last_date = df[df['Blood Sugar (mg/dl)'].notna()].iloc[-1]['Date']
    last_time = df[df['Blood Sugar (mg/dl)'].notna()].iloc[-1]['Time']
    last_time_dt = pd.to_datetime(f"{last_date.date()} {last_time}")
    current_time_dt = datetime.strptime(event_time, "%m/%d/%Y %H:%M")
    time_diff_hours = (current_time_dt - last_time_dt).seconds / 3600

    print("Today:", date, current_time_dt, last_time_dt)
    todays_insulin, t_insulin_left = calculate_active_insulin(date, current_time_dt, last_time_dt)
    print("yesterday:", date - pd.Timedelta(days=1), current_time_dt, last_time_dt)
    yesterdays_insulin, y_insulin_left = calculate_active_insulin(date - pd.Timedelta(days=1), current_time_dt, last_time_dt)
    active_insulin = todays_insulin + yesterdays_insulin
    insulin_left = t_insulin_left + y_insulin_left
    print("Active insulin:", active_insulin, insulin_left)

    carbs_hike = food_carbs * 4
    print("Carbs Increased:", carbs_hike)
    print("Prev row:", df[df['Blood Sugar (mg/dl)'].notna()].iloc[-1]['Blood Sugar (mg/dl)'])
    prev_blood_sugar = df[df['Blood Sugar (mg/dl)'].notna()].iloc[-1]['Blood Sugar (mg/dl)'] + carbs_hike
    print("Previous blood sugar:", prev_blood_sugar)
    if food_carbs != 0:
        pass
    new_blood_sugar = round(prev_blood_sugar - (isf * active_insulin), 2)
    print("New blood sugar:", new_blood_sugar)

    new_row = {
        'Date': [date],
        'Time': [current_time[1]],
        'Event': ['Calculate Blood Sugar'],
        'Food Consumed': [None],
        'Carbohydrates (grams)': [None],
        'Time After Insulin (hours)': [None],
        'Insulin Left (units)': [insulin_left],
        'Blood Sugar (mg/dl)': [new_blood_sugar],
        'DateTime': [pd.to_datetime(date_str + ' ' + current_time[1])]
    }

    daily_log_df_date_str = daily_log_df['Date'].dt.strftime('%m/%d/%Y')
    df['DateTime'] = pd.to_datetime(daily_log_df_date_str + ' ' + df['Time'])

    pd.set_option('display.max_columns', None)
    new_row_df = pd.DataFrame(new_row)
    df = pd.concat([df, new_row_df], ignore_index=True)
    # print(df, "\n------------------------------------------------------------------------")


    df = df.sort_values(by='DateTime')
    print(df, "\n------------------------------------------------------------------------")
    df = df.drop(columns=['DateTime'])

    df = df.reset_index(drop=True)

    return new_row_df, df
def save_file(df):
    df.to_csv("..\Datasets\daily_sugar_log.csv", index=False)
    print("Saved")

def external_sugar_update(df, event_time, carbs, isf):
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    updated_row, updated_df = update_blood_sugar_log(df, event_time, carbs, isf)
    return updated_row

if __name__ == "__main__":
    isf = isf_df['Calculated ISF (mg/dL per unit)'].mean()
    updated_row, updated_df = update_blood_sugar_log(daily_log_df, "10/4/2024 7:30", 0, isf)
    save_file(updated_df)
