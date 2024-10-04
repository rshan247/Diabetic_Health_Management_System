import pandas as pd
import daily_sugar_monitor
import sample_food_data


def concat_and_sort_df(df1, df2):
    df1['DateTime'] = pd.to_datetime(df1['Date'].astype(str) + ' ' + df1['Time'].astype(str))

    df = pd.concat([df1, df2], ignore_index=True)
    df = df.sort_values(by='DateTime')
    df = df.drop(columns=['DateTime'])
    df = df.reset_index(drop=True)

    return df

def update_blood_sugar_for_food_snack(df, isf):
    food_snack_events = df[((df['Event'] == 'Food') | (df['Event'] == 'Snack')) & (df['Blood Sugar (mg/dl)'].isna())] #.values
    print(f"Processing events \n: {food_snack_events}")

    # Calculating the blood sugar at the starting time of taking snack or food
    for index, row in food_snack_events.iterrows():
        event_time = row['Date'] + " " + row['Time']
        print(event_time)

        # print(daily_log_df)
        updated_row = daily_sugar_monitor.external_sugar_update(df, event_time, 0, isf)
        print("1.Updated row:\n", updated_row)

        new_index = df[(df['Date'] == row['Date']) &
                       (df['Time'] == row['Time']) &
                       (df['Event'] == row['Event'])].index[0]
        print(new_index)
        df.at[new_index, 'Blood Sugar (mg/dl)'] =  updated_row['Blood Sugar (mg/dl)']
        df.at[new_index, 'Insulin Left (units)'] = updated_row['Insulin Left (units)']
        print("1.Updated df:\n", df)

        # Calculating carbs of the food or snack
        food_items = row['Food Consumed']
        food_carbs = sample_food_data.calculate_carbohydrate(food_items.split(","))
        df.at[new_index, 'Carbohydrates (grams)'] = food_carbs
        print("2.Updated df:\n", df)

        # Calculating blood sugar after digestion assuming 30 mins for snack and 2 hours for food
        food_type = row['Event']
        # carbs = row['Carbohydrates (grams)']
        print("2.Carbs:", food_carbs)
        time = pd.to_datetime(row['Date'] + " " + row['Time'])

        time_to_calculate = time + pd.Timedelta(minutes=30) if food_type == 'Snack' else time + pd.Timedelta(hours=2)
        print("Time to calculate: ", time_to_calculate)

        new_row = daily_sugar_monitor.external_sugar_update(df, time_to_calculate.strftime("%m/%d/%Y %H:%M"), food_carbs,isf)
        print("3.New row:", new_row)
        df = concat_and_sort_df(df, new_row)
        print("3.Final df:", df)

    print("Result:\n", df)
    return df

def save_file(df):
    df.to_csv("..\Datasets\daily_sugar_log.csv", index=False)
    print("Saved")


if __name__ == "__main__":
    daily_log_df = pd.read_csv("..\Datasets\daily_sugar_log.csv")
    isf_df = pd.read_csv("..\Datasets\ISF.csv")
    isf = isf_df['Calculated ISF (mg/dL per unit)'].mean()
    updated_df = update_blood_sugar_for_food_snack(daily_log_df, isf)
    save_file(updated_df)
