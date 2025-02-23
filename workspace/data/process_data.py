import sys
import sqlite3
import pandas as pd
import numpy as np
from sqlalchemy import create_engine 

def load_data(messages_filepath, categories_filepath):
    # load messages dataset
    messages = pd.read_csv(messages_filepath)
    # load categories dataset
    categories = pd.read_csv(categories_filepath)

    # merge datasets
    df = messages.merge(categories, how='outer', on=['id'])

    return df


def clean_data(df):
    # create a dataframe of the 36 individual category columns
    categories = df['categories'].str.split(';', expand=True, n=36)

    # Extract a list of new column names for categories
    row = categories[1:2]
    category_colnames = row.apply(lambda x : x.str.slice(0,-2))
    # Apply the names to the columns
    category_colnames_list = category_colnames.values.tolist()
    categories.columns = category_colnames_list

    categories_clean = categories.copy()

    for column in category_colnames_list:
        # set each value to be the last character of the string
        categories_clean[column] = categories_clean[column].apply(lambda x : x.str.slice(-1))
    
        # convert column from string to numeric
        categories_clean[column] = categories_clean[column].astype(int)
    
    # Drop child_alone from categories dataframe.
    categories_clean.drop('child_alone', axis = 1, inplace = True)

    df_clean_one = df.drop(columns=['categories'])

    # concatenate the original dataframe with the new `categories` dataframe
    df_clean_two = pd.concat([df_clean_one, categories_clean],join='inner', axis=1)

    # drop duplicates
    df_clean_two.drop_duplicates(inplace = True)   

    # Remove rows with a related value of 2 from the dataset
    df_clean_two = df_clean_two[df_clean_two['related'] != 2]

    return df_clean_two



def save_data(df, database_filename):
    engine = create_engine('sqlite:///' + database_filename)
    df.to_sql('messages', engine, index=False)


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()