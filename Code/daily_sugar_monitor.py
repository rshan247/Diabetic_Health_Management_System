import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import insulin_usage_chart as insulin_utilization


isf_df = pd.read_csv("..\Datasets\ISF.csv")
daily_log_df = pd.read_csv("..\Datasets\daily_sugar_log.csv")
daily_log_df_date_str = daily_log_df['Date']
daily_log_df['Date'] = pd.to_datetime(daily_log_df['Date'], format = '%m/%d/%Y')

daily_insulin_log =pd.read_csv("..\Datasets\daily_insulin_log.csv")
daily_insulin_log['Date'] = pd.to_datetime(daily_insulin_log['Date'], format='%m/%d/%Y')
daily_insulin_log['Morning Insulin Time'] = pd.to_datetime(daily_insulin_log['Morning Insulin Time'], format='%m/%d/%Y %H:%M')
daily_insulin_log['Night Insulin Time'] = pd.to_datetime(daily_insulin_log['Night Insulin Time'], format='%m/%d/%Y %H:%M')
# print(daily_log_df.head())
# print(daily_log_df[daily_log_df['Blood Sugar (mg/dL)'].notna()].iloc[-1])
print(daily_log_df['Blood Sugar (mg/dl)'].notna())

event = daily_log_df[((daily_log_df['Event'] == 'Food') | (daily_log_df['Event'] == 'Snack')) & (daily_log_df['Blood Sugar (mg/dl)'].isna())]
print(event)


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
        return cummulative_morning_insulin + cummulative_night_insulin, insulin_left
    elif morning_insulin_time <= time <= morning_finish_time and time < night_insulin_time:
        print("Morning")
        cummulative_morning_insulin = insulin_utilization.get_insulin_usage(mi_units, time_from_morning, False)
        insulin_left = mi_units - cummulative_morning_insulin
        print("insulin_to_reduce:", cummulative_morning_insulin)
        return cummulative_morning_insulin, insulin_left
    elif night_insulin_time <= time <= night_finish_time and time < morning_insulin_time:
        print("Night")
        cummulative_night_insulin = insulin_utilization.get_insulin_usage(ni_units, time_from_night, False)
        insulin_left = ni_units - cummulative_night_insulin
        print("insulin_to_reduce:", cummulative_night_insulin)
        return cummulative_night_insulin, insulin_left
    return 0, 0

def calculate_active_insulin(cur_date, cur_time, last_sugar_time):
    print("Sur date:", cur_date)
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

    insulin_to_reduced, _ = get_insulin(last_sugar_time, morning_insulin_time_dt, morning_insulin_finish_time, night_insulin_time_dt, night_insulin_finish_time, mi_units, ni_units)
    active_insulin, insulin_left = get_insulin(cur_time, morning_insulin_time_dt, morning_insulin_finish_time, night_insulin_time_dt, night_insulin_finish_time, mi_units, ni_units)

    print("Insulins:", active_insulin , insulin_to_reduced)
    return round(active_insulin - insulin_to_reduced, 2), round(insulin_left, 2)


def update_blood_sugar_log(df, event_time, food_carbs, isf):
    date = df[df['Blood Sugar (mg/dl)'].notna()].iloc[-1]['Date']
    date_str = datetime.strftime(date, "%m/%d/%Y")
    last_time = df[df['Blood Sugar (mg/dl)'].notna()].iloc[-1]['Time']
    last_time_dt = pd.to_datetime(f"{date.date()} {last_time}")
    current_time = event_time.split()
    current_time_dt = datetime.strptime(event_time, "%m/%d/%Y %H:%M")
    time_diff_hours = (current_time_dt - last_time_dt).seconds / 3600

    todays_insulin, t_insulin_left = calculate_active_insulin(date, current_time_dt, last_time_dt)
    yesterdays_insulin, y_insulin_left = calculate_active_insulin(date - pd.Timedelta(days=1), current_time_dt, last_time_dt)
    active_insulin = todays_insulin + yesterdays_insulin
    insulin_left = t_insulin_left + y_insulin_left
    print("Active insulin:", active_insulin, insulin_left)

    prev_blood_sugar = df[df['Blood Sugar (mg/dl)'].notna()].iloc[-1]['Blood Sugar (mg/dl)']
    if food_carbs != 0:
        pass
    new_blood_sugar = round(prev_blood_sugar - (isf * active_insulin), 2)

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

    df['DateTime'] = pd.to_datetime(daily_log_df_date_str + ' ' + df['Time'])

    pd.set_option('display.max_columns', None)
    new_row_df = pd.DataFrame(new_row)
    df = pd.concat([df, new_row_df], ignore_index=True)
    # print(df, "\n------------------------------------------------------------------------")


    df = df.sort_values(by='DateTime')
    # print(df, "\n------------------------------------------------------------------------")
    df = df.drop(columns=['DateTime'])

    df = df.reset_index(drop=True)

    return df
def save_file(df):
    df.to_csv("..\Datasets\daily_sugar_log.csv", index=False)
    print("Saved")


isf = isf_df['Calculated ISF (mg/dL per unit)'].mean()
updated_daily_log_df = update_blood_sugar_log(daily_log_df, "9/16/2024 18:14", 0, isf)
save_file(updated_daily_log_df)
