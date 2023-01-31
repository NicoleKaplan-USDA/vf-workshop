def Vence_Api(customer,dbuser,dbpassword,start_time,end_time):
    # import the "requests" library if you don't already have it installed
    # python -m pip install requests
    # python -m pip install pandas

    # load required libraries
    import os
    import sys
    import re
    import warnings
    import requests
    from requests.structures import CaseInsensitiveDict
    import datetime

    import pandas as pd
    import json

    # store the URL of the API in a object
    url = "https://5rxy4xetnd.execute-api.us-west-2.amazonaws.com/production/messages"

    headers = CaseInsensitiveDict()

    headers["Content-Type"] = "application/json"

    # read in the configuration JSON from the project directory
    # this is read in as a dictionary
    # TODO add warning message for incorrect date formatting in JSON
    # TODO add validation for date input if date range is not valid, return error message
    # incorrect date range are returning empty csv file
    json_string = "" + '{' + '"'    + "customer" +'"'+  ":"+ '"'+customer+'"' +","+'"'    + "dbuser" +'"'+  ":"+ '"'+dbuser+'"' +","+'"'    + "dbpassword" +'"'+  ":"+ '"'+dbpassword+'"'+ ","+ '"'+"start_time"+'"'+  ":"+ '"'+start_time+'"'+ ","+ '"'+"end_time"+'"'+  ":"+ '"'+end_time+'"'+'}'
    # store the URL of the API in a object
    url = "https://5rxy4xetnd.execute-api.us-west-2.amazonaws.com/production/messages"

    headers = CaseInsensitiveDict()

    headers["Content-Type"] = "application/json"

    # read in the configuration JSON from the project directory
    # this is read in as a dictionary
    # TODO add warning message for incorrect date formatting in JSON
    # with open('config/config.json') as file:
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

    # compare the difference in time between the start and end dates
    time_difference_days = (json_end_date_datetime - json_start_date_datetime).days

    # need to split the time delta into 12 hours chunks to be safe (avoid timeout)
    # json_end_date_datetime

    # TODO can we tune the timedelta to optimize the amount data that is returned from each request?
    # pass in a vector or list of values for the timedelta
    time_delta = datetime.timedelta(days=0.5)

    # TODO add retry if return is bad, wait X amount of time and then retry
    # after y amount of retries
    # initialize an empty list to store our list of dates to feed to the API
    dates_to_call = [json_start_date_datetime]

    date = json_start_date_datetime

    while date < json_end_date_datetime:
        date = date + time_delta
        dates_to_call.append(date)

    # initialize an empty pandas data frame
    all_data = pd.DataFrame()

    window_size = 2

    # for i in range(len(dates_to_call) - window_size + 1):
    # print(dates_to_call[i: i + window_size])

    # dates_to_call[0: 0 + window_size][0]
    # dates_to_call[0: 0 + window_size][1]

    # initialize an empty string to hold the combined responses from each call to the API
    combined_response_text = ''

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
        # TODO decide if combined_message_text variable is necessary or can we leave it as
        combined_message_text = response.text

        # print an informative message to indicate to users that no data was returned for the date range
        if combined_message_text == '[]':
            print("Empty response: No data returned for this date range.")

        # replace the contents of an empty response '[]' with empty string to avoid adding those characters to combined response
        if combined_message_text == '[]':
            combined_message_text = re.sub(pattern="\[]", repl="", string=combined_message_text)

        # add the response text from the current iteration to the text from previous iterations of the for loop
        # TODO these variable names are confusing and need to be renamed
        combined_response_text = combined_response_text + combined_message_text

    # print error message and exit if no data was returned from date ranges in config file
    if len(combined_response_text) == 0:
        sys.exit("No data was returned for dates in `config.json`. Exiting.")

    # TODO this is might be unnecessary and can probably be dropped
    #  but first need to check for variable references in script
    # drop the first and last characters from the message so string splitting will create symmetrical messages
    # first we need to know the length of the message (i.e., number of characters) to create an index
    message_length = len(combined_response_text)

    # TODO instead of creating new variables when cleaning up the message string, just overwrite the message string

    # drop the last character of the message which is an extra right brace "]"
    # this is just an extra unnecessary character
    message_text_drop_last_char = combined_response_text[0:(message_length - 1)]

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
        print('This message is missing seconds: (index number = ' + str(i) + ')')

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
            print('This message is missing microseconds: (index number = ' + str(i) + ')')

    # intialize an empty list to store the offending messages that have zeros added
    # the zeros are so that when we go to evaluate the date expression
    # it doesn't fail because their are uneven number of inputs
    # dates that are missing a field have 6 inputs
    # dates that aren't missing a field have 7 inputs
    offending_messages_add_microseconds = []

    for i in range(len(messages_missing_microseconds)):
        offending_messages_add_microseconds.append(
            re.sub(pattern="\)", repl=",00000)", string=messages_missing_microseconds[i]))

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
            pass  # TODO figure out what to put here
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
    # print(index, value)

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
    GpsLocationExtIndicationCowHeading = []
    ShockEventExtIndication = []
    DeviceStatusIndication = []

    # TODO this could be more efficient if I created groups of each message type based on the element length
    # TODO search through each message type to look for phrase/keyword that is unique

    # separate each message type by the number elements in each list
    for element in message_list_split:
        if len(element) == 10:
            GpsLocationExtIndication.append(element)
        elif len(element) == 11:
            GpsLocationExtIndicationCowHeading.append(element)
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

    location_extent_cow_heading_df = pd.DataFrame(GpsLocationExtIndicationCowHeading,
                                                columns=['uuid',
                                                        'date',
                                                        'collar',
                                                        'messagetype',
                                                        'latitude',
                                                        'longitude',
                                                        'accuracy',
                                                        'cowHeading',
                                                        'tiltAngle',
                                                        'reliable',
                                                        'more',
                                                        'sequence']
                                                )
    location_extent_cow_heading_df.index.name = "index"

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
    combined_df = pd.concat([device_status_df,
                            location_extent_df,
                            location_extent_cow_heading_df,
                            shock_event_df],
                            ignore_index=True)

    # specify the order of the column names in the combined dataframe
    column_names = ['uuid',
                    'date',
                    'collar',
                    'messagetype',
                    'latitude',
                    'longitude',
                    'trackingState',
                    'cowHeading',
                    'tiltAngle',
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

    reindex_combined_df.cowHeading = location_extent_cow_heading_df.cowHeading.str.replace("cowHeading=", "")

    reindex_combined_df.tiltAngle = location_extent_cow_heading_df.tiltAngle.str.replace("tiltAngle=", "")

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

    fillna_combined_df = fillna_combined_df.reset_index(drop=False)

    # create a filename based on the date range you specified for the HTTP request
    # convert the datetime object to a string but use a more friendly format for filenames
    start_date_filename = json_start_date_datetime.strftime("%Y-%m-%d")

    end_date_filename = json_end_date_datetime.strftime("%Y-%m-%d")

    # concatenate strings to create a flexible filename
    filename = start_date_filename + "_" + end_date_filename + "_Vence-message-data" + ".csv"

    path = os.path.join("drive/My Drive/Vence_API", filename)
    # print in the console to check the filename string

    print(path)

    # TODO print a message with successful file out saying where the file has been saved
    # write out the data frame as a csv file using the flexible filename convention
    fillna_combined_df.to_csv(path, index=False)
