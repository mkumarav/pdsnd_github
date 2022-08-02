#!/usr/bin/env python
# coding: utf-8

# In[1]:


import time
import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display


# In[2]:


#Setting city names as keys and mapping to appropriate data file using dictionary
CITY_DATA = { 'chicago': 'chicago.csv',
              'new york city': 'new_york_city.csv',
              'washington': 'washington.csv' }


# In[3]:


#Assigning a few global variables to use in functions

#Create a dictionary that holds all month names mapped to month number eg.'january': 1
calendar_months= [name.lower() for name in calendar.month_name[1:]]
month_dict={calendar_months[i]:i+1 for i in range(len(calendar_months))}

#weekdays in a list
#['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
calendar_days= [name.lower() for name in calendar.day_name[0:]]


# In[4]:


def get_filters():
    """
    Asks user to specify a city, month, and day to analyze.

    Returns:
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    """
    #Welcome message
    print('Welcome! Thank you for your interest in exploring US bikeshare data!\nLet\'s get your preferences.\n')
    time.sleep(3)
    
    #Declaring nicknames to use for a personalized and interactive experience with the user
    city_nickname = { 'chicago': 'The Windy city',
                      'new york city': 'The Big Apple',
                      'washington': 'Our Nation\'s Capital' }
    
    #Declaring possible alternate entries for New York city by users
    new_york_city_altnames=['new york','newyork','newyorkcity','newyork city','new yorkcity']
    
    #Get user input for city (chicago, new york city, washington). 
    city=''
    while city not in ['chicago','new york city','washington']:
        city=(input('Which city are you interested in?\nI have data for Chicago, New York city or Washington.\nPlease pick one.')).lower()
        if city not in ['chicago','new york city','washington'] and city !=None:
            if city in new_york_city_altnames:
                confirm = input("I think you meant to type 'New York city'. Is that correct? Yes/No").lower()
                if confirm in ('yes','y'):
                    city='new york city'
                    break
                else:
                    continue    
            print("\nSorry, I do not have data for that city.\n")
            time.sleep(1.5)
    print('Great! You selected {}, {}.\n'.format(city.upper(),city_nickname[city.lower()]))
    time.sleep(2)
    
    #Get user input for month (all, january, february, ... , june)
    month=''
    print("You can view data for a specific month:\n {}.\n".format(calendar_months[0:6]))
    time.sleep(2)
    if 'all' not in calendar_months:
        calendar_months.append('all')
    #Validate month is within Jan to June or 'all'
    while month not in calendar_months[0:6]+[calendar_months[-1]]:
        month=(input("Which month are you interested in?\n Enter the full name of the month (Eg: January) or 'all'.")).lower()
        if month not in calendar_months[0:6]+[calendar_months[-1]]:
            if month in calendar_months[6:12]:
                print("\nSorry, I do not have data for that month.")
                time.sleep(1.5)
            else:
                print("\nSorry, that is not a valid month.")
                time.sleep(1.5)
    print('\nNice choice. You selected {}.'.format(month.upper()))
    time.sleep(1.5)
    
    #Get user input for day of week (all, monday, tuesday, ... sunday)
    day=''
    print("\nYou can view data for a specific day of the week:\n{}\n".format(calendar_days))
    time.sleep(1.5)
    if 'all' not in calendar_days:
        calendar_days.append('all')
    while day not in (calendar_days):
        day=(input("Which day of the week are you interested in?\n Enter the full name of the day (Eg: Sunday) or 'all'")).lower()
        if day not in (calendar_days) and day!=None:
            print("\nSorry, that's not a valid day of week.")
            time.sleep(3)
    print('\nAwesome! You selected {}.'.format(day.upper()))
    time.sleep(1)
    
    #Summarize user choices and return values
    print('*'*40)
    print('\nGreat choices! You selected {}, {}, {}.\n'.format(city.upper(),month.upper(),day.upper()))
    print('-'*40)
    return city, month, day


# In[5]:


def prep_data(city):
    """
    Loads data for the specified city and splits for granular data
    Args:
        (str) city - name of the city to analyze
    Returns:
        df - Pandas DataFrame containing data for specific city passed in argument
    """    
    #load data from .csv file for the city passed in argument into a pandas dataframe
    #Load date columns in datetime format 
    print("Loading data for {} per your request...\n".format(city.upper()))
    if city.lower() in CITY_DATA.keys():
        bike_df = pd.read_csv(CITY_DATA.get(city.lower()),parse_dates=['Start Time', 'End Time'],infer_datetime_format=True)
      
        #City level stats
        columns=list(bike_df.columns)
        del columns[0]
        print("For {}, these are the available columns:\n {}".format(city.upper(),columns))
        print("And there are {} rows of data available.".format(len(bike_df)))
        
        print("\nI did some quick Data Quality checks. No data cleaning necessary.\n")
        
        #Check for Duplicated Values
        if bike_df.duplicated().sum()==0:
            print("Duplicate values: None\n")
        else:
            print(bike_df.duplicated().sum())

        #Check for Missing values in our data.
        check = bike_df.isna().sum()    
        print("Missing values check:\n{}\n".format(check))
        if city=='chicago':
            print("Some missing values only in Gender and Birth Year.")
            #Rounding Birth Year to calculate Age
            bike_df["Age"] = 2017-bike_df["Birth Year"]
        if city=='new york city':
            print("Some missing values only in User Type, Gender and Birth Year.")
            #Rounding Birth Year to calculate Age
            bike_df["Age"] = 2017-bike_df["Birth Year"]
            
        #Splitting granular data into individual columns for analysis
        bike_df["Start_Year"]=bike_df["Start Time"].dt.year
        bike_df["Start_Month"]=bike_df["Start Time"].dt.month
        bike_df["Start_Day"]=bike_df["Start Time"].dt.day
        bike_df["Start_Day_of_week"]=bike_df["Start Time"].dt.day_name()
        bike_df["Start_Hour"]=bike_df["Start Time"].dt.hour
        bike_df["Start_Minute"]=bike_df["Start Time"].dt.minute
        bike_df["Start_Second"]=bike_df["Start Time"].dt.second
        bike_df["Trip Route"] = bike_df["Start Station"] + "to" + bike_df["End Station"]
    
    return bike_df


# In[6]:


def filter_data(df, city, month, day):
    """
    Filters data based on month and day choices.

    Args:
        (Pandas DataFrame) df - dataframe containing city data unfiltered
        (str) city - name of the city to analyze
        (str) month - name of the month to filter by, or "all" to apply no month filter
        (str) day - name of the day of week to filter by, or "all" to apply no day filter
    Returns:
        df - Pandas DataFrame containing city data filtered by month and day
    """
    #Check for 'all' to avoid filters
    if month=='all' and day=='all':
        print("\nYou selected 'ALL' for month and day, so no further filtering is needed.\n")
        return df   
    
    #Filter data for the month chosen by user. Generates boolean True for filter condition or None if 'all'.
    if month!='all':
        month_flag=[]
        for value in df["Start_Month"]:
            if value==month_dict[month]:
                month_flag.append(True)
            else:
                month_flag.append(False)    

        month_flag = np.array(month_flag)
    else:
        month_flag=None
        
    #filter data for the day chosen by user. Generates boolean True for filter condition or None if 'all'.
    if day!='all':
        day_flag=[]
        for value in df["Start_Day_of_week"]:
            if value.lower()==day:
                day_flag.append(True)
            else:
                day_flag.append(False)
        day_flag = np.array(day_flag) 
    else:
        day_flag=None
    
    #Applying one or both filters on data as applicable  
    if (month_flag is not None) and (day_flag is not None):
        filter = month_flag & day_flag
    elif (month_flag is None) and (day_flag is not None):
        filter = day_flag
    elif (month_flag is not None) and (day_flag is None):
        filter = month_flag
        
    is_chosen_day_month =pd.Series(filter)
    month_day_filtered_df=df[is_chosen_day_month]
    
    #Filtered Row count
    print("\nI filtered {} data for {} and {} and see {} rows of data available.".format(city.upper(),month.upper(),day.upper(),len(month_day_filtered_df)))
    
    return month_day_filtered_df


# In[7]:


def most_common(df,factor):
    """
    Displays the statistical mode of the factor to answer what the most common value is.

    Args:
        (Pandas DataFrame) df - dataframe containing data
        (str) factor - name of the column the mode would be calculated for
    Returns:
        object - numpy.ndarray containing the mode
    """
    #Find mode. If more than one, reference the first one for counting number of occurrences
    common_factor=df[factor].mode()
    get_val=common_factor.values
    mode_val=get_val[0]
    
    #Find number of occurrences of mode value
    count=df[factor].value_counts()[mode_val]
    
    factor_string=(factor.replace('_',' ')).upper()
       
    if len(common_factor)==1:
        print("The most common {} is: {} with {} occurrences\n".format(factor_string,get_val,count))
    else:
        print("The most common {} is: {} with {} occurrences\n".format(factor_string+'s',get_val,count))
        
    return common_factor.values


# In[8]:


def display_records(df,city):
    """
    Displays raw data in increments of 5 records if user chooses to see.

    Args:
        (Pandas DataFrame) df - dataframe containing data
        (str) city - name of the city to analyze
    Returns:
        row_index - index of the last row the user viewed
    """
    #User confirmation to see raw data
    row_index = 0
    if city!='washington':
        raw_data_df=df[["Start Time", "End Time","Trip Duration","Start Station","End Station","User Type","Gender","Birth Year"]]
    else:
        raw_data_df=df[["Start Time", "End Time","Trip Duration","Start Station","End Station","User Type"]]
    #raw_choice=''
    while True: 
        if row_index == 0:
            raw_choice = input('\nWould you like to see 5 records of bikeshare data? Yes/No\n').lower()
        else:
            raw_choice = input('\nWould you like to see more data? Yes/No\n').lower() 
            
        if raw_choice in ('yes','y'):
            print("\nHere are 5 records for your review.\n")
            time.sleep(1)
            for i in range(0,5):
                print("\nRow Index#: {}".format(row_index))
                print('~'*15)
                print(raw_data_df.iloc[row_index])
                print('-'*40)
                row_index+=1
        elif raw_choice in ('no','n'):
            print('*'*40)
            print('\n')
            break
        elif raw_choice not in ('yes','y','no','n',''):
            print("I do not recognize your answer. Please select Yes or No.\n")
        else:
            continue

    return (row_index)


# In[9]:


def time_stats(df):
    """
    Displays statistics on the most frequent times of travel.

    Args:
        (Pandas DataFrame) df - dataframe containing data
    """
    print('#1 Popular times of Travel')
    print('-'*20)
    start_time = time.time()
    
    #Displays the most common month
    common_month_num=df.Start_Month.mode()
    common_month=[]
    for m, value in month_dict.items():
        if value in common_month_num.values:
            common_month.append(m)
            common_month = [x.upper() for x in common_month]  
    
    #Handles the possibility of multiple mode values
    if len(common_month)==1:
        print("The most common MONTH is :{}.\n".format(common_month))
    else:
        print("The most common MONTHS are :{}.\n".format(common_month))
        
    #Shows frequency bar chart
    fig, axes = plt.subplots(1,2, figsize=(20,8))
    df["Start_Day_of_week"].value_counts().plot(kind='bar',ax=axes[0],color='green',xlabel='Day of Week',ylabel='count',title='Bikeshare Frequency by Day of week')
    axes[0].legend(loc=1)    

    #Displays the most common day of week
    most_common(df,"Start_Day_of_week")
    print("I created some visuals or charts you can review.\n")
    print('-'*12)
    df["Start_Hour"].value_counts().plot(kind='bar',ax=axes[1],color='yellow',xlabel='Hour of Day',ylabel='count')
    axes[1].legend(loc=1)  
    plt.title("Bikeshare Frequency by Hour of Day")
    plt.show (block=False)        
    
    #Displays the most common start hour
    most_common(df,"Start_Hour")
    
    print("\nThis calculation took %s seconds." % round((time.time() - start_time),2))
    print('~'*40)
    time.sleep(3)


# In[10]:


def station_stats(df):
    """
    Displays statistics on the most popular stations and trip.
    Args:
        (Pandas DataFrame) df - dataframe containing data
    """
    print('#2 Popular stations and Trip')
    print('-'*20)
    #print('\nCalculating The Most Popular Stations and Trip...\n')
    start_time = time.time()

    #Displays the most commonly used start station
    most_common(df,"Start Station")

    #Displays the most commonly used end station
    most_common(df,"End Station")

    #Displays the most frequent combination of start station and end station trip
    most_common(df,"Trip Route")

    print("\nThis calculation took %s seconds." % round((time.time() - start_time),2))
    print('~'*40)
    time.sleep(3)


# In[11]:


def trip_duration_stats(df):
    """
    Displays statistics on the total and average trip duration.

    Args:
        (Pandas DataFrame) df - dataframe containing data
    """
    
    print('#3 Trip duration')
    print('-'*20)
    #print('\nCalculating Trip Duration...\n')
    start_time = time.time()

    #Displays total travel time
    total_travel_time = df['Trip Duration'].sum()
    trip_count=df['Trip Duration'].count()
    print('The Total Travel time is {} seconds ({} minutes).\nThis is from a total of {} bike trips!'.format(round(total_travel_time,2),total_travel_time//60,trip_count))

    #Displays mean travel time
    mean_duration = round(df['Trip Duration'].mean(),2)
    print('\nThe Average Duration is: {} seconds ({} minutes).'.format(mean_duration,mean_duration//60))

    print("\nThis calculation took %s seconds." % round((time.time() - start_time),2))
    print('~'*40)
    time.sleep(3)


# In[12]:


def user_stats(df):
    """
    Displays statistics on bikeshare users.

    Args:
        (Pandas DataFrame) df - dataframe containing data
    """    
    print('#4 User Statistics')
    print('-'*20)
    #print('\nCalculating User Stats...\n')
    start_time = time.time()

    #Display counts of user types
    user_stats=(df["User Type"].value_counts()).to_frame()
    display(user_stats)    
    print('-'*40)

    #Display counts of gender   
    if 'Gender' not in df.columns:
        print('No data is found for Gender for this city.\n')
    else:
        gender_stats=(df.Gender.value_counts()).to_frame()
        print("Gender Stats:\n")
        display(gender_stats)
        fig, axes = plt.subplots(1,2, figsize=(10,5))
        df.Gender.value_counts().plot(kind='pie',ax=axes[0],xlabel='Gender')
        axes[0].legend(loc=1) 
    print('-'*40)
    
    #Display earliest, most recent, and most common year of birth
    if 'Birth Year' not in df.columns:
        print('No data is found for Birth Year for this city.\n')
    else:
        most_common(df,"Birth Year")
        df["Birth Year"].value_counts().plot(kind='line',ax=axes[1],xlabel='Year of Birth')
        axes[1].legend(loc=1) 
        plt.show (block=False)
        earliest_year=df['Birth Year'].loc[df['Birth Year'].idxmin()]
        recent_year=df['Birth Year'].loc[df['Birth Year'].idxmax()]
        oldest_age=df['Age'].loc[df['Age'].idxmax()]
        youngest_age=df['Age'].loc[df['Age'].idxmin()]
        print("The earliest Birth Year is {}.\nThe oldest user is {} year old!\n".format(int(earliest_year),int(oldest_age)))
        print("The most recent Birth Year is {}.\nThe youngest user is {} years old!\n".format(int(recent_year),int(youngest_age)))

    print("\nThis calculation took %s seconds." % round((time.time() - start_time),2))
    print('~'*40)
    time.sleep(3)


# In[13]:


def main():
    while True:
        city, month, day = get_filters()
        city_df=prep_data(city)
        df=filter_data(city_df,city, month, day)
        display_records(df,city)
        print("Let me show you some interesting bikeshare statistics\n")
        print('='*40)
        time.sleep(2)
        time_stats(df)
        station_stats(df)
        trip_duration_stats(df)
        user_stats(df)
    
        restart = input('\nWould you like to restart? Enter yes or no.\n')
        if restart.lower() not in ('yes','y'):
            print("Thank you for reviewing bikeshare data. Have a great day!\n")
            break
        
if __name__ == "__main__":
	main()


# 
