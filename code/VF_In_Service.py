def Vence_Api(customer,dbuser,dbpassword,start_time,end_time):

    import os
    import sys
    import re
    import warnings
    import requests
    from requests.structures import CaseInsensitiveDict
    import datetime
    import numpy as np #JRB add in numpy
    import pandas as pd
    import json

    #api code written by andrew antaya, for questions contact aantaya@arizona.edu
    #API code adapted to jupyter notebook by Jameson Brennan
    #v2.1 comment out columns that have string 'GpsLocationExtIndicationCowHeading' as they no longer seem available
    json_string = "" + '{' + '"'    + "customer" +'"'+  ":"+ '"'+customer+'"' +","+'"'    + "dbuser" +'"'+  ":"+ '"'+dbuser+'"' +","+'"'    + "dbpassword" +'"'+  ":"+ '"'+dbpassword+'"'+ ","+ '"'+"start_time"+'"'+  ":"+ '"'+start_time+'"'+ ","+ '"'+"end_time"+'"'+  ":"+ '"'+end_time+'"'+'}' 
    # store the URL of the API in a object
    url = "https://5rxy4xetnd.execute-api.us-west-2.amazonaws.com/production/messages"

    headers = CaseInsensitiveDict()

    headers["Content-Type"] = "application/json"

    # read in the configuration JSON from the project directory
    # this is read in as a dictionary
    # TODO add warning message for incorrect date formatting in JSON
    #with open('config/config.json') as file:
    json_config_dict = json.loads(json_string)

    # use the dict to interate through the start time and end time
    # index the dictionary to get the start time inside of the json file
    # we will leave the start time unchanged in the JSON file and change the date inside of Python
    json_start_date_string = json_config_dict['start_time']

    # do the same for the end date inside of the json file
    json_end_date_string = json_config_dict['end_time']

    # convert the start date string into a datetime object
    json_start_date_datetime = datetime.datetime.strptime(json_start_date_string, '%Y-%m-%d %H:%M:%S.%f')

    # convert the end date string into a datetime object
    json_end_date_datetime = datetime.datetime.strptime(json_end_date_string, '%Y-%m-%d %H:%M:%S.%f')

    # TODO I can specify the date input as a sys.arg to accept inputs from the command line interface

    # compare the difference in time between the start and end dates
    time_difference_days = (json_end_date_datetime - json_start_date_datetime).days

    # need to split the time delta into 12 hours chunks to be safe (avoid timeout)
    # json_end_date_datetime

    #################################################JRB added loop to optimize time delta
    date = json_start_date_datetime

    #times to ping and try
    trys=[48,24,12,6,4,3,1]
    response_codes=[]
    #loop through times, get response code
    for i in range(len(trys)):
    #print(trys[i])

        try1=date+datetime.timedelta(hours = trys[i])
        json_config_dict['end_time']=try1.strftime("%Y-%m-%d %H:%M:%S.%f")
        data = json.dumps(json_config_dict)
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            response_codes.append( True)
        else:
            response_codes.append( False)
    #select time based on optimal time and used below for time delta input
    opt_time=np.where(response_codes)[0][0]
    #time_delta = datetime.timedelta(hours = trys[opt_time])
    print('optimal time window:' , trys[opt_time], 'hours')

    ##########################################################JRB end section added
    
    time_delta = datetime.timedelta(days = 0.25) #JRB change line to opt_time from loop above line commented out
    
    
    

    # initialize an empty list to store our list of dates to feed to the API
    dates_to_call = [json_start_date_datetime]

    

    while(date < json_end_date_datetime):
        date = date + time_delta
        dates_to_call.append(date)

    # initialize an empty pandas data frame
    all_data = pd.DataFrame()

    window_size = 2

    # for i in range(len(dates_to_call) - window_size + 1):
    #     print(dates_to_call[i: i + window_size])

    # dates_to_call[0: 0 + window_size][0]
    # dates_to_call[0: 0 + window_size][1]

    for i in range(len(dates_to_call) - window_size + 1):
        # the time difference in and of itself doesn't matter
        # rather its the amount of time it takes the server to respond to with that much data
        # if its takes too much time, then you will get a server error

        # convert the start datetime to a string
        # the formatting part is specific to the date formatting the API expects
        start_date_datetime = dates_to_call[i: i + window_size][0]
        start_date_string = start_date_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        print('Start Date: ' + start_date_string)

        # assign in the new start and end dates to the json converted to dictionary
        json_config_dict['start_time'] = start_date_string

        # grab the first intermediate end date from the list
        intermediate_date_datetime = dates_to_call[i: i + window_size][1]
        intermediate_date_string = intermediate_date_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        print('End Date: ' + intermediate_date_string)

        json_config_dict['end_time'] = intermediate_date_string

        # convert the dict to a json string
        data = json.dumps(json_config_dict)

        # make call to API, store response in a object
        response = requests.post(url, headers=headers, data=data)

        # stop execution if http response returns an error
        # there are many possible reasons that it may return an error
        if response.status_code != 200:
            sys.exit(("Error: HTTP Response" + " " + str(response.status_code) + " " + response.reason))

        # informative response status code would be helpful for diagnosing server issues
        print('HTTP Status Code: ' + str(response.status_code) + ' ' + response.reason)

        # check the character encoding of the API response
        # it should be in utf-8

        # index the response variable to get the "content" of the response
        # the response text will work better than response content
        message_text = response.text

        # drop the first and last characters from the message so string splitting will create symmetrical messages
        # first we need to know the length of the message (i.e., number of characters) to create an index
        message_length = len(message_text)

        # stop execution if the http response is empty but status code is 200
        # for whatever reason, the server returns two braces with nothing inside
        if message_length <= 3:
            sys.exit("Error: Empty Response from Server")

        # TODO instead of creating new variables when cleaning up the message string, just overwrite the message string

        # drop the last character of the message which is an extra right brace "]"
        # this is just an extra unnecessary character
        message_text_drop_last_char = message_text[0:(message_length - 1)]

        # drop the first character of the message which is an extra left brace "["
        # this is just an extra unnecessary character
        message_text_drop_first_char = message_text_drop_last_char[1:]

        # drop the empty space characters too
        message_text_drop_empty_spaces = str.replace(message_text_drop_first_char, " ", "")

        # the message text also has apostrophe characters that we need to drop
        # these characters are leftovers from the message data
        message_text_drop_apostrophe_char = str.replace(message_text_drop_empty_spaces, "'", "")

        # drop the extra brace characters too
        message_text_drop_left_brace_char = str.replace(message_text_drop_apostrophe_char, "[", "")

        # there are actually two message types returned from the beta API
        # split the message response into two separate messages on a specific combination of characters
        message_list = message_text_drop_left_brace_char.split(sep="]),")

        # search for dates that are missing the seconds field
        # intialize an empty list to store if the date in each message is a match to the regex
        # this object will be used to test if the type is a re.match or none (not a match)
        missing_seconds = []

        # search for dates in the message list that are missing the seconds field and the microseconds field
        for i in range(len(message_list)):
            missing_seconds.append(re.search("datetime.datetime\(\d*,\d*,\d*,\d*,\d*\)", message_list[i]))

        # initialize and empty list to store the messages that are missing a date field
        messages_missing_seconds = []
        messages_missing_seconds_index = []

        # this for loop will tell you which messages are missing a date by their index
        for i in range(len(missing_seconds)):
            if type(missing_seconds[i]) == re.Match:
                messages_missing_seconds.append(message_list[i])
                messages_missing_seconds_index.append(int(i))
                #print('This message is missing seconds: (index number = ' + str(i) + ')')

        # intialize an empty list to store the offending messages that have zeros added
        # the zeros are so that when we go to evaluate the date expression
        # it doesn't fail because their are uneven number of inputs
        # dates that are missing a field have 6 inputs
        # dates that aren't missing a field have 7 inputs
        offending_messages_add_seconds = []

        for i in range(len(messages_missing_seconds)):
            offending_messages_add_seconds.append(re.sub(pattern="\)", repl=",00)", string=messages_missing_seconds[i]))

        # this uses the index of the messages missing seconds to replace the messages in the orginal data
        for i in range(len(messages_missing_seconds)):
            message_list[messages_missing_seconds_index[i]] = offending_messages_add_seconds[i]

        # search for dates that are missing the microseconds field
        # intialize an empty list to store if the date in each message is a match to the regex
        # this object will be used to test if the type is a re.match or none (not a match)
        missing_microseconds = []

        # search for dates in the message list that are missing the microseconds field
        # this regular expression may need to change if the inputs are different
        # this for loop tells you which dates are missing a field based on regular expression match
        for i in range(len(message_list)):
            missing_microseconds.append(re.search("datetime.datetime\(\d*,\d*,\d*,\d*,\d*,\d*\)", message_list[i]))

        # initialize and empty list to store the messages that are missing a date field
        messages_missing_microseconds = []
        messages_missing_microseconds_index = []

        # this for loop will tell you which messages are missing a date by their index
        for i in range(len(missing_microseconds)):
            if type(missing_microseconds[i]) == re.Match:
                messages_missing_microseconds.append(message_list[i])
                messages_missing_microseconds_index.append(int(i))
                #print('This message is missing microseconds: (index number = ' + str(i) + ')')

        # intialize an empty list to store the offending messages that have zeros added
        # the zeros are so that when we go to evaluate the date expression
        # it doesn't fail because their are uneven number of inputs
        # dates that are missing a field have 6 inputs
        # dates that aren't missing a field have 7 inputs
        offending_messages_add_microseconds = []

        for i in range(len(messages_missing_microseconds)):
            offending_messages_add_microseconds.append(re.sub(pattern="\)", repl=",00000)", string=messages_missing_microseconds[i]))

        # this uses the index of the messages missing seconds to replace the messages in the orginal data
        for i in range(len(messages_missing_microseconds)):
            message_list[messages_missing_microseconds_index[i]] = offending_messages_add_microseconds[i]

        # double check that the messages are not missing any date values
        # intialize an empty list to store the data
        regex_search = []

        # implement a for loop that reads in each element from the message_list
        # and checks for a pattern match on the regular expression
        # if there is a pattern match, the for loop will print a success message
        # if there is not a pattern match, the for loop will print an error message and stop the for loop
        # error message include the index number so you can take a look at where in the data the for loop stopped
        for i in range(len(message_list)):
            regex_search.append(re.search("datetime.datetime\(\d*,\d*,\d*,\d*,\d*,\d*,\d*\)", message_list[i]))
            if type(regex_search[i]) == re.Match:
                pass # TODO figure out what to put here
            elif type(regex_search[i]) != re.Match:
                warnings.warn('Not a match: (index number = ' + str(i) + ')' + ' ' + message_list[i])
                offending_message = message_list[i]
                index = int(i)
                print(offending_message)
                break

        # initialize an empty list to store the unevaluated date expressions
        date_expressions = []

        # extract just the date expression from the
        for i in range(len(regex_search)):
            date_expressions.append(regex_search[i].group())

        # check that the length of the date list matches the length of the message list
        len(date_expressions)
        len(message_list)

        # print a warning message if there are missing dates in the message data
        # there might be problems caused by missing dates that this script currently cannot handle
        if len(date_expressions) == len(message_list):
            print("All missing dates were fixed. Proceed.")
        elif len(date_expressions) != len(message_list):
            warnings.warn('Warning Message: It looks like some dates might be missing. STOP.')

        # It makes more sense to store the date as string rather (in ISO format)
        # Rather than as a datetime object when writing to a csv file
        # some programs like Excel have problems displaying datetime formats
        # initialize an empty list to store the datetimes converted into isoformat 8601 date strings
        isodate_list = []

        # evaluate the string as a Python expression and temporarily store the output as a "datetime" object
        # datetime objects are a special class of objects with special properties
        # then convert the datetime object into an isoformat 8601 date string
        for i in range(len(date_expressions)):
            date_time_object = (eval(date_expressions[i]))
            isodate_list.append(date_time_object.isoformat())

        # initialize an empty list for the cleaned dates
        message_list_cleaned_dates = []

        # for loop through the message list, replacing each unevaluated Python date expression with a date string in iso format
        # it looks like a paranthesis was dropped or changed in this message type
        for i in range(len(message_list)):
            message_list_cleaned_dates.append(
                re.sub("datetime.datetime\(\d*,\d*,\d*,\d*,\d*,\d*,\d*\)", isodate_list[i], message_list[i]))

        # check the output in the console to see if the date strings were correctly replaced
        # you should now see iso 8601 formatted dates instead of unevaluated Python expressions
        # for index, value in enumerate(message_list_cleaned_dates):
        #     print(index, value)

        # split the message text on the comma delimiter
        # store the string split message data in a new object
        # its important to note that we are changing data formats by splitting
        # we are going from a string to a list

        # write a for loop that
        # indexes message list to extract each message
        # splits each message by every comma
        # returns a nested list with each message stored in the parent list and split apart into
        # if you run this list multiple times you will need to clear

        # initialize an empty list for storing the nested data
        message_list_split = []

        for i in range(len(message_list_cleaned_dates)):
            message_split = (message_list_cleaned_dates[i].split(sep=","))
            message_list_split.append(message_split)

        # initialize empty lists to store each of the message types
        GpsLocationExtIndication = []
        #GpsLocationExtIndicationCowHeading = []
        ShockEventExtIndication = []
        DeviceStatusIndication = []

        # TODO this could be more efficient if I created groups of each message type based on the element length
        # separate each message type by the number elements in each list
        for element in message_list_split:
            if len(element) == 10:
                GpsLocationExtIndication.append(element)
            #elif len(element) == 11:
             #   GpsLocationExtIndicationCowHeading.append(element)
            elif len(element) == 21:
                ShockEventExtIndication.append(element)
            elif len(element) == 27:
                DeviceStatusIndication.append(element)

        location_extent_df = pd.DataFrame(GpsLocationExtIndication,
                                          columns=['uuid',
                                                   'date',
                                                   'collar',
                                                   'messagetype',
                                                   'latitude',
                                                   'longitude',
                                                   'accuracy',
                                                   'reliable',
                                                   'more',
                                                   'sequence']
                                          )
        location_extent_df.index.name = "index"

        #location_extent_cow_heading_df = pd.DataFrame(GpsLocationExtIndicationCowHeading,
         #                                             columns=['uuid',
          #                                                     'date',
           #                                                    'collar',
            #                                                   'messagetype',
             #                                                  'latitude',
              #                                                 'longitude',
               #                                                'accuracy',
                #                                               'cowHeading',
                 #                                              'tiltAngle',
                  #                                             'reliable',
                   #                                            'more',
                    #                                           'sequence']
                     #                                 )
        #location_extent_cow_heading_df.index.name = "index"

        shock_event_df = pd.DataFrame(ShockEventExtIndication,
                                      columns=['uuid',
                                               'date',
                                               'collar',
                                               'messagetype',
                                               'soundDisabled',
                                               'shockDisabled',
                                               'soundSuspended',
                                               'shockSuspended',
                                               'soundEvent',
                                               'shockEvent',
                                               'latitude',
                                               'longitude',
                                               'trackingState',
                                               'headingReportingEnabled',
                                               'headingManagementEnabled',
                                               'shockCount',
                                               'soundCount',
                                               'shockCountCumulative',
                                               'reliable',
                                               'more',
                                               'sequence']
                                      )

        shock_event_df.index.name = "index"

        # this data frame does not split on an equals sign
        # instead it uses column names
        device_status_df = pd.DataFrame(DeviceStatusIndication,
                                        columns=['uuid',
                                                 'date',
                                                 'collar',
                                                 'messagetype',
                                                 'sequenceNumber',
                                                 'trackingState',
                                                 'headingReportingEnabled',
                                                 'headingManagementEnabled',
                                                 'soundDisabled',
                                                 'shockDisabled',
                                                 'soundSuspended',
                                                 'shockSuspended',
                                                 'shockCountAttempts',
                                                 'soundCountAttempts',
                                                 'shockCountApplied',
                                                 'soundCountApplied',
                                                 'shockCountSuspend',
                                                 'soundCountSuspend',
                                                 'shockCountCumulative',
                                                 'currVoltageMv',
                                                 'lastTxVoltageMv',
                                                 'lastShockVoltageMv',
                                                 'mmuTempDegC',
                                                 'mcuTempDegC',
                                                 'reliable',
                                                 'more',
                                                 'sequence']
                                        )

        device_status_df.index.name = "index"

        # concatenate dataframes
        combined_df = pd.concat([device_status_df, location_extent_df,  shock_event_df], #location_extent_cow_heading_df,
                                ignore_index=True)

        # specify the order of the column names in the combined dataframe
        column_names = ['uuid',
                        'date',
                        'collar',
                        'messagetype',
                        'latitude',
                        'longitude',
                        'trackingState',
                       # 'cowHeading',
                        #'tiltAngle',
                        'headingReportingEnabled',
                        'headingManagementEnabled',
                        'soundDisabled',
                        'shockDisabled',
                        'soundSuspended',
                        'shockSuspended',
                        'soundEvent',
                        'shockEvent',
                        'shockCount',
                        'soundCount',
                        'shockCountAttempts',
                        'soundCountAttempts',
                        'shockCountApplied',
                        'soundCountApplied',
                        'shockCountSuspend',
                        'soundCountSuspend',
                        'shockCountCumulative',
                        'currVoltageMv',
                        'lastTxVoltageMv',
                        'lastShockVoltageMv',
                        'mmuTempDegC',
                        'mcuTempDegC',
                        'reliable',
                        'more',
                        'sequence',
                        'accuracy']

        # reorder the columns so that latitude and longitude are right after 'messagetype'
        reindex_combined_df = combined_df.reindex(columns=column_names)

        # clean up all of the rows with equals signs
        # replace the string on the left side of the equals sign with nothing ""
        reindex_combined_df.uuid = reindex_combined_df.uuid.str.replace("(", "", regex=False)

        reindex_combined_df.latitude = reindex_combined_df.latitude.str.replace("latitude=", "")

        reindex_combined_df.longitude = reindex_combined_df.longitude.str.replace("longitude=", "")

        reindex_combined_df.accuracy = reindex_combined_df.accuracy.str.replace("accuracy=", "")

        reindex_combined_df.reliable = reindex_combined_df.reliable.str.replace("reliable=", "")

        reindex_combined_df.more = reindex_combined_df.more.str.replace("more=", "")

        reindex_combined_df.sequence = reindex_combined_df.sequence.str.replace("sequence=", "")

        #reindex_combined_df.cowHeading = location_extent_cow_heading_df.cowHeading.str.replace("cowHeading=", "")

        #reindex_combined_df.tiltAngle = location_extent_cow_heading_df.tiltAngle.str.replace("tiltAngle=", "")

        reindex_combined_df.soundDisabled = reindex_combined_df.soundDisabled.str.replace("soundDisabled=", "")

        reindex_combined_df.shockDisabled = reindex_combined_df.shockDisabled.str.replace("shockDisabled=", "")

        reindex_combined_df.soundSuspended = reindex_combined_df.soundSuspended.str.replace("soundSuspended=", "")

        reindex_combined_df.shockSuspended = reindex_combined_df.shockSuspended.str.replace("shockSuspended=", "")

        reindex_combined_df.soundEvent = reindex_combined_df.soundEvent.str.replace("soundEvent=", "")

        reindex_combined_df.shockEvent = reindex_combined_df.shockEvent.str.replace("shockEvent=", "")

        reindex_combined_df.trackingState = reindex_combined_df.trackingState.str.replace("trackingState=", "")

        reindex_combined_df.headingReportingEnabled = reindex_combined_df.headingReportingEnabled.str.replace(
            "headingReportingEnabled=", "")

        reindex_combined_df.headingManagementEnabled = reindex_combined_df.headingManagementEnabled.str.replace(
            "headingManagementEnabled=", "")

        reindex_combined_df.shockCount = reindex_combined_df.shockCount.str.replace("shockCount=", "")

        reindex_combined_df.soundCount = reindex_combined_df.soundCount.str.replace("soundCount=", "")

        reindex_combined_df.shockCountCumulative = reindex_combined_df.shockCountCumulative.str.replace(
            "shockCountCumulative=", "")

        # reindex_combined_df.sequenceNumber = reindex_combined_df.sequenceNumber.str.replace("sequenceNumber=", "")

        reindex_combined_df.headingReportingEnabled = reindex_combined_df.headingReportingEnabled.str.replace(
            "headingReportingEnabled=", "")

        reindex_combined_df.headingManagementEnabled = reindex_combined_df.headingManagementEnabled.str.replace(
            "headingManagementEnabled=", "")

        reindex_combined_df.shockCountAttempts = reindex_combined_df.shockCountAttempts.str.replace("shockCountAttempts=",
                                                                                                    "")

        reindex_combined_df.soundCountAttempts = reindex_combined_df.soundCountAttempts.str.replace("soundCountAttempts=",
                                                                                                    "")

        reindex_combined_df.shockCountApplied = reindex_combined_df.shockCountApplied.str.replace("shockCountApplied=", "")

        reindex_combined_df.soundCountApplied = reindex_combined_df.soundCountApplied.str.replace("soundCountApplied=", "")

        reindex_combined_df.shockCountSuspend = reindex_combined_df.shockCountSuspend.str.replace("shockCountSuspend=", "")

        reindex_combined_df.soundCountSuspend = reindex_combined_df.soundCountSuspend.str.replace("soundCountSuspend=", "")

        reindex_combined_df.currVoltageMv = reindex_combined_df.currVoltageMv.str.replace("currVoltageMv=", "")

        reindex_combined_df.lastTxVoltageMv = reindex_combined_df.lastTxVoltageMv.str.replace("lastTxVoltageMv=", "")

        reindex_combined_df.lastShockVoltageMv = reindex_combined_df.lastShockVoltageMv.str.replace("lastShockVoltageMv=",
                                                                                                    "")

        reindex_combined_df.mmuTempDegC = reindex_combined_df.mmuTempDegC.str.replace("mmuTempDegC=", "")

        reindex_combined_df.mcuTempDegC = reindex_combined_df.mcuTempDegC.str.replace("mcuTempDegC=", "")

        # the very last sequence=false has a couple extra characters that we need to remove
        reindex_combined_df.sequence = reindex_combined_df.sequence.str.replace("])", "", regex=False)

        # add the index column name back in
        reindex_combined_df.index.name = "index"

        # arrange the data frame by date from oldest to most recent
        sort_by_date_combined_df = reindex_combined_df.sort_values('date')

        reset_index_combined_df = sort_by_date_combined_df.reset_index(drop=True)

        # fill 'nan' values with 'NA' strings so they're won't be any blank/missing values in the data
        fillna_combined_df = reset_index_combined_df.fillna('NA')

        # TODO deprecated .append method
        all_data = all_data.append(fillna_combined_df)

        all_data = all_data.reset_index(drop=True)

    # create a filename based on the date range you specified for the HTTP request
    # convert the datetime object to a string but use a more friendly format for filenames
    start_date_filename = json_start_date_datetime.strftime("%Y-%m-%d")


    end_date_filename = json_end_date_datetime.strftime("%Y-%m-%d")

    # concatenate strings to create a flexible filename
    filename = "data/" + start_date_filename + "_" + end_date_filename + "_Vence-message-data" + ".csv"

    # check if the "data" directory exists,
    # if it does not, create new directory
    cwd = os.getcwd()

    path = os.path.join(cwd, "data")

    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError as error:
            print(error)

    # print in the console to check the filename string
    print(filename)
    return(all_data)
    # write out the data frame as a csv file using the flexible filename convention
    all_data.to_csv(filename)
 
import math
#from utm.error import OutOfRangeError

__all__ = ['to_latlon', 'from_latlon']

K0 = 0.9996

E = 0.00669438
E2 = E * E
E3 = E2 * E
E_P2 = E / (1.0 - E)

SQRT_E = math.sqrt(1 - E)
_E = (1 - SQRT_E) / (1 + SQRT_E)
_E2 = _E * _E
_E3 = _E2 * _E
_E4 = _E3 * _E
_E5 = _E4 * _E

M1 = (1 - E / 4 - 3 * E2 / 64 - 5 * E3 / 256)
M2 = (3 * E / 8 + 3 * E2 / 32 + 45 * E3 / 1024)
M3 = (15 * E2 / 256 + 45 * E3 / 1024)
M4 = (35 * E3 / 3072)

P2 = (3. / 2 * _E - 27. / 32 * _E3 + 269. / 512 * _E5)
P3 = (21. / 16 * _E2 - 55. / 32 * _E4)
P4 = (151. / 96 * _E3 - 417. / 128 * _E5)
P5 = (1097. / 512 * _E4)

R = 6378137

ZONE_LETTERS = "CDEFGHJKLMNPQRSTUVWXX"


def to_latlon(easting, northing, zone_number, zone_letter=None, northern=None, strict=True):
    """This function convert an UTM coordinate into Latitude and Longitude

        Parameters
        ----------
        easting: int
            Easting value of UTM coordinate

        northing: int
            Northing value of UTM coordinate

        zone number: int
            Zone Number is represented with global map numbers of an UTM Zone
            Numbers Map. More information see utmzones [1]_

        zone_letter: str
            Zone Letter can be represented as string values. Where UTM Zone
            Designators can be accessed in [1]_

        northern: bool
            You can set True or False to set this parameter. Default is None


       .. _[1]: http://www.jaworski.ca/utmzones.htm

    """
    if not zone_letter and northern is None:
        raise ValueError('either zone_letter or northern needs to be set')

    elif zone_letter and northern is not None:
        raise ValueError('set either zone_letter or northern, but not both')

    if strict:
        if not 100000 <= easting < 1000000:
            raise OutOfRangeError('easting out of range (must be between 100.000 m and 999.999 m)')
        if not 0 <= northing <= 10000000:
            raise OutOfRangeError('northing out of range (must be between 0 m and 10.000.000 m)')
    if not 1 <= zone_number <= 60:
        raise OutOfRangeError('zone number out of range (must be between 1 and 60)')

    if zone_letter:
        zone_letter = zone_letter.upper()

        if not 'C' <= zone_letter <= 'X' or zone_letter in ['I', 'O']:
            raise OutOfRangeError('zone letter out of range (must be between C and X)')

        northern = (zone_letter >= 'N')

    x = easting - 500000
    y = northing

    if not northern:
        y -= 10000000

    m = y / K0
    mu = m / (R * M1)

    p_rad = (mu +
             P2 * math.sin(2 * mu) +
             P3 * math.sin(4 * mu) +
             P4 * math.sin(6 * mu) +
             P5 * math.sin(8 * mu))

    p_sin = math.sin(p_rad)
    p_sin2 = p_sin * p_sin

    p_cos = math.cos(p_rad)

    p_tan = p_sin / p_cos
    p_tan2 = p_tan * p_tan
    p_tan4 = p_tan2 * p_tan2

    ep_sin = 1 - E * p_sin2
    ep_sin_sqrt = math.sqrt(1 - E * p_sin2)

    n = R / ep_sin_sqrt
    r = (1 - E) / ep_sin

    c = _E * p_cos**2
    c2 = c * c

    d = x / (n * K0)
    d2 = d * d
    d3 = d2 * d
    d4 = d3 * d
    d5 = d4 * d
    d6 = d5 * d

    latitude = (p_rad - (p_tan / r) *
                (d2 / 2 -
                 d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2)) +
                 d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2))

    longitude = (d -
                 d3 / 6 * (1 + 2 * p_tan2 + c) +
                 d5 / 120 * (5 - 2 * c + 28 * p_tan2 - 3 * c2 + 8 * E_P2 + 24 * p_tan4)) / p_cos

    return (math.degrees(latitude),
            math.degrees(longitude) + zone_number_to_central_longitude(zone_number))


def from_latlon(latitude, longitude, force_zone_number=None):
    """This function convert Latitude and Longitude to UTM coordinate

        Parameters
        ----------
        latitude: float
            Latitude between 80 deg S and 84 deg N, e.g. (-80.0 to 84.0)

        longitude: float
            Longitude between 180 deg W and 180 deg E, e.g. (-180.0 to 180.0).

        force_zone number: int
            Zone Number is represented with global map numbers of an UTM Zone
            Numbers Map. You may force conversion including one UTM Zone Number.
            More information see utmzones [1]_

       .. _[1]: http://www.jaworski.ca/utmzones.htm
    """
    if not -80.0 <= latitude <= 84.0:
        raise OutOfRangeError('latitude out of range (must be between 80 deg S and 84 deg N)')
    if not -180.0 <= longitude <= 180.0:
        raise OutOfRangeError('longitude out of range (must be between 180 deg W and 180 deg E)')

    lat_rad = math.radians(latitude)
    lat_sin = math.sin(lat_rad)
    lat_cos = math.cos(lat_rad)

    lat_tan = lat_sin / lat_cos
    lat_tan2 = lat_tan * lat_tan
    lat_tan4 = lat_tan2 * lat_tan2

    if force_zone_number is None:
        zone_number = latlon_to_zone_number(latitude, longitude)
    else:
        zone_number = force_zone_number

    zone_letter = latitude_to_zone_letter(latitude)

    lon_rad = math.radians(longitude)
    central_lon = zone_number_to_central_longitude(zone_number)
    central_lon_rad = math.radians(central_lon)

    n = R / math.sqrt(1 - E * lat_sin**2)
    c = E_P2 * lat_cos**2

    a = lat_cos * (lon_rad - central_lon_rad)
    a2 = a * a
    a3 = a2 * a
    a4 = a3 * a
    a5 = a4 * a
    a6 = a5 * a

    m = R * (M1 * lat_rad -
             M2 * math.sin(2 * lat_rad) +
             M3 * math.sin(4 * lat_rad) -
             M4 * math.sin(6 * lat_rad))

    easting = K0 * n * (a +
                        a3 / 6 * (1 - lat_tan2 + c) +
                        a5 / 120 * (5 - 18 * lat_tan2 + lat_tan4 + 72 * c - 58 * E_P2)) + 500000

    northing = K0 * (m + n * lat_tan * (a2 / 2 +
                                        a4 / 24 * (5 - lat_tan2 + 9 * c + 4 * c**2) +
                                        a6 / 720 * (61 - 58 * lat_tan2 + lat_tan4 + 600 * c - 330 * E_P2)))

    if latitude < 0:
        northing += 10000000

    return easting, northing, zone_number, zone_letter


def latitude_to_zone_letter(latitude):
    if -80 <= latitude <= 84:
        return ZONE_LETTERS[int(latitude + 80) >> 3]
    else:
        return None


def latlon_to_zone_number(latitude, longitude):
    if 56 <= latitude < 64 and 3 <= longitude < 12:
        return 32

    if 72 <= latitude <= 84 and longitude >= 0:
        if longitude <= 9:
            return 31
        elif longitude <= 21:
            return 33
        elif longitude <= 33:
            return 35
        elif longitude <= 42:
            return 37

    return int((longitude + 180) / 6) + 1


def zone_number_to_central_longitude(zone_number):
    return (zone_number - 1) * 6 - 180 + 3

def process_vf_data(df):
  import os
  import sys
  import re
  import warnings
  import requests
  from requests.structures import CaseInsensitiveDict
  import datetime
  import pandas as pd
  import json
  import numpy as np
  import pytz
  import utm
  #import utm
  from shapely.geometry import Point
  from geopandas import GeoDataFrame
  df1=df[df.latitude.str.contains("NA") == False]
  #store NA latitude values
  df_na_coordinates=df[df.latitude.str.contains("NA") == True]
#get unique collar id as last 4 characters in mac address
  df1['collar_id']= df1['collar'].str[-4:]
  #create list of unique collars 
  collars=df1.collar_id.unique()
  #collars
  #change working directory to google drive location
  cwd= '/content/drive/My Drive/Vence_API'

#loop through each unique collar ID and process data
  for i in range(0, len(collars)):

      #subset out data based on collar id number in loop
      out_df = df1[df1["collar_id"] ==collars[i]]
      out_df['latitude']= pd.to_numeric(out_df['latitude']) #convert lat to number
      out_df['longitude']= pd.to_numeric(out_df['longitude']) #convert long to number
      out_df['date']=pd.to_datetime(out_df['date'],utc=True)  #convert date to date UTC
      out_df = out_df.sort_values([ "date"], ascending = ( True)) #sort by date
      out_df ['Duration']=out_df ['date']-out_df ['date'].shift(1) #calculate duration between successive fixes
      out_df['Duration']=out_df['Duration']/np.timedelta64(1, 's')/60  #convert to minutes
      from timezonefinder import TimezoneFinder
      tf = TimezoneFinder()

      time_zone=[]
      time_convert=[] 
      #loop through each lat long and get the local timezone for each point and make list of converted date/time
      for time_z in range(0,len(out_df)):
          tz=tf.timezone_at(lng=out_df.longitude.iloc[time_z], lat=out_df.latitude.iloc[time_z]) 
          my_date_time=out_df.date.iloc[time_z]
          convert_time= my_date_time.astimezone(pytz.timezone(tz)).strftime('%Y-%m-%d %H:%M:%S %Z%z')
          #   print (tz)
          time_zone.append(tz)
          time_convert.append(convert_time)
  
      out_df['Time_Zone']=time_zone #create column for time zone
      out_df['date']=time_convert #convert to local
      out_df['date']=pd.to_datetime(out_df['date']) #convert to date
      #convert lat/long to utm
      Lat=out_df['latitude']
      Long=out_df['longitude']
      Lat_utm=[]
      Long_utm=[]
      for f in range(0,len(Lat)):
          out=utm.from_latlon(Lat.iloc[f],Long.iloc[f])
          #print (out)
          Lat_utm.append(out[0])
          Long_utm.append(out[1])
      out_df['latitude_utm']=Lat_utm
      out_df['longitude_utm']=Long_utm
      Lat_Long=pd.DataFrame({'Lat': out_df['latitude_utm'],
         'Long': out_df['longitude_utm'],})
      #create kd tree to get number of points within 30m +- 20 points form each
      counts=[]
      count_sum=[]
      from sklearn.neighbors import KDTree

      for m in range(0,len(out_df)):

          t=20 #this is for 20 points 20+ and 20-
          b=m-t
          if b <0:
              b=0
          e=m+t
          if e>len(Lat_Long):
              e=len(Lat_Long)
          #Lat_Long[b:e]
          gps_tree = KDTree(Lat_Long[b:e])
          ##count within 10m radius
          ct=gps_tree.query_radius(Lat_Long[b:e],r=30,count_only=True) #can change radius r to whatever this is set to 30m
          if m < t:
              counts.append(ct[m])
          else:
              counts.append(ct[t])
          count_sum.append(ct.sum()) 


      out_df['Count']=counts #create count column
      out_df['Sum']=count_sum #creat sum column

      #flag collars that have been stationary for a long period of time, indicates collar fell off
      out_df['Flag'] = np.where( (out_df['Sum'] >= 800), 1,0) 
      from itertools import groupby
      count_dups = [sum(1 for _ in group) for _, group in groupby(out_df['Flag'])]
      new=[]
      for p in range (0,len(count_dups)):
          a=np.repeat(count_dups[p], count_dups[p], axis=0)
          new.append(a)
      count_vector=np.hstack(new) 
      out_df['Count_Flag']=count_vector
      out_df['Count_Flag'] = np.where(out_df['Flag'] == 0, 0, out_df['Count_Flag'])
      #at 576 this would be equivalent to 5 minute fix data not moving for 2 days
      out_df['Flag_Collar_Off']=np.where(out_df['Count_Flag'] >= 576, 'Flag','Ok')
      out_df.drop(['Count', 'Flag','Count_Flag'], axis=1, inplace=True)







      #calculate euclidean distance
      out_df['Distance']= np.sqrt ((out_df['latitude_utm'].shift(1)-out_df['latitude_utm'])**2 + (out_df['longitude_utm'].shift(1) - out_df['longitude_utm'])**2) 

      out_df['Rate'] =out_df['Distance']/out_df['Duration']
      #remove points with rate of travel greater than 54m/min
      #print(len(out_df[out_df.Rate>54]))
      #out_df=out_df[out_df.Rate<54]

      #re_calculate after dropping fixes
      out_df['Distance']= np.sqrt ((out_df['latitude_utm'].shift(1)-out_df['latitude_utm'])**2 + (out_df['longitude_utm'].shift(1) - out_df['longitude_utm'])**2) 
      out_df ['Duration']=out_df ['date']-out_df ['date'].shift(1)
      out_df['Duration']=out_df['Duration']/np.timedelta64(1, 's')/60
      out_df['Rate'] =out_df['Distance']/out_df['Duration']

      #conditions=[ 
      #    (out_df['Rate'] <2.34),
      #    (out_df['Rate'] >=2.34)&(out_df['Rate'] <=25),
      #    (out_df['Rate'] >25)]
      #choices=["Rest","Graze","Walk"]
      #out_df['Behavior']=np.select(conditions,choices)



      out_csv='/content/drive/My Drive/Vence_API/csv_files/' + collars[i] +'.csv'

      out_shp='/content/drive/My Drive/Vence_API/shp_files/'  + collars[i]  +'.shp'


      out_df.to_csv(out_csv)
      geometry = [Point(xy) for xy in zip(out_df.longitude,out_df.latitude)]
      df_pts = out_df.drop(['longitude', 'latitude'], axis=1)
      df_pts['date']=df_pts['date'].astype(str)
      gdf = GeoDataFrame(df_pts, crs="EPSG:4326", geometry=geometry)



      gdf.to_file(out_shp)


