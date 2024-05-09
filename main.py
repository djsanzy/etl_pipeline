import pandas as pd
import sqlite3


def main():
    main_data = extract("apps_data.csv")
    cleaned_data = transform(main_data)
    ratings = transform_2(cleaned_data, "User, input a number? \n")
    load("test.db", ratings, 'etl')


# Extract csv file from source.
def extract(file_path):
    data = pd.read_csv(file_path)

# Information about the extracted data
    print(f"Here's a little bit of information about the data stored in {file_path}")
    print(f"There are {data.shape[0]} rows and {data.shape[1]}  columns in this dataset")
    print("The columns in this dataframe takes the following types: ")
    print(f"{data.dtypes}")
    print(f"To view the DataFrame extracted from {file_path}, display the value returned by this function")

    return data


def transform(apps):
    # Making all the columns lower cased, capiltalizing and replacing some symbols for easy manipulation
    apps.columns = [x.lower() for x in apps.columns]
    apps.drop_duplicates(inplace=True)
    apps.rename(
        columns={"content rating": "content_rating", "last updated": "last_updated", "current ver": "current_ver",
                 "android ver": "android_ver"}, inplace=True)
    apps['category'] = apps['category'].apply(lambda x: x.capitalize())
    apps['category'] = apps['category'].apply(lambda x: x.replace('_', ' '))
    apps['category'] = apps['category'].apply(lambda x: x.replace('and', '&'))
    #
    apps['price'] = apps['price'].apply(lambda x: x.replace('$', ''))

    # Removed the '$' sign in the 'price' column and changed it from string to float
    filt = apps['price'] == 'Everyone'
    apps.loc[filt, 'price'] = '0'
    apps['price'] = apps['price'].astype(float)
    apps['rating'] = apps["rating"].astype(float)

    return apps


def transform_2(data, prompt):
    filt = data["reviews"] == '3.0M'
    data.loc[filt, "reviews"] = '3'
    data['reviews'] = data["reviews"].astype(int)
    # The user is asked to enter a number that is above 158 t0 capture the numbers apart from zero
    while True:
        try:
            number = int(input(prompt))
            if number < 158:
                print("Input a review number more than 158")
            else:
                filt = data["reviews"] >= number
        # Here, almost all the columns are filtered, it's left for the user to select what is relevant to them
                return data.loc[
                    filt, ["reviews", "app", "category", "rating", "installs", "size", "content_rating"]]
        except ValueError:
            print("Please input a valid number")


# LOADING DATA
#Create a function to do this
def load(database_name, dataframe, table_name):
    # Create a connection object
    conn = sqlite3.connect(database_name)
    # Write the data to the specified table(table_name)
    dataframe.to_sql(name=table_name, con=conn, if_exists="replace", index=False)
    print("Original Dataframe has been loaded to sqlite/n")
    print("The loaded Dataframe has been read from sqlite for validation")

    loaded_dataframe = pd.read_sql(sql=f"SELECT * FROM {table_name}", con=conn)
    try:
        assert dataframe.shape == loaded_dataframe.shape
        print(f"Success!! The data in the {loaded_dataframe} has successfully been loaded and validated")

    except AssertionError:
        print("DataFrame shape is not consistent before and after loading. Take a closer look")


main()

