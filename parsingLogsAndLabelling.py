import pandas as pd
from statistics import mean
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
import datetime

""" # parsing the file
with open("logs.json", "r") as f:
    logs = json.load(f)

times = [
    datetime.datetime.strptime(i["timestamp"], "%Y-%m-%d %H:%M:%S")
    + datetime.timedelta(hours=12)
    for i in logs
]
states = [i["text"] for i in logs]
times.reverse()
states.reverse()

logData = {"times": times, "states": states} """

def convertLogNote(filepath: str, on: str, off: str):
    '''
    LOGNOTE MUST HAVE 24 HOUR TIME!!! DO THIS MANUALLY, OR MAKE A SCRIPT
    converts a lognote file with 24 hour timestamps and alernating on and off

    Parameters
    ----------
    on: str, required
        the lognote string of the text on
    off: str, required
        the lognote string of the text off 
    filepath: str, required
        the absolute/relative path of the lognote file you want to convert
    '''
    with open(filepath,'r') as f:
        file = json.load(f)
    
    data = {'times': [], 'states':  [] }
    for note in reversed(file):
        data['times'].append(datetime.datetime.strptime(note['timestamp'], "%Y-%m-%d %H:%M:%S"))
        data['states'].append('in') if note['text'] == on else data['states'].append('out') if note['text'] == off else print('hello weird value')
    
    df = pd.DataFrame.from_dict(data)
    return df


def combineLogsAndRawData(dfLogs: pd.DataFrame, raw: str, saveLocation: str):
    '''
    combines a lognote in dataframe form, and the path to the raw bigquery data of a puck mat, by labelling with 1s and 0s

    Parameters
    ----------
    df: pd.DataFrame, required
        the dataframe of the lognote, the output of convertLogNote
    raw: str, required
        the absolute/relative path of the bigquery data in csv
    saveLocation: str, required
        the absolute/relative path of where you want to save the final labelled csv
    '''

    df = pd.read_csv(raw)
    df["deviceTimestamp"] = pd.to_datetime(df["deviceTimestamp"])
    df["deviceTimestamp"] = df["deviceTimestamp"].dt.tz_localize(tz=None)
    df["state"] = None
    # Iterate over each timestamp in the first table
    for i, row in df.iterrows():
        timestamp = row["deviceTimestamp"]

        # Find where the timestamp falls in the second table
        for j in range(len(dfLogs)):
            start_time = dfLogs.loc[j, "times"]

            if j != len(dfLogs)-1:
                end_time = dfLogs.loc[j + 1, "times"]

            state = dfLogs.loc[j, "states"]
            # print (start_time,timestamp,end_time)
            
            if j == len(dfLogs) - 1:
                if timestamp >= start_time:
                    df.loc[i, "state"] = 1 if state == "in" else 0
                    break
            
            else:
                if start_time <= timestamp < end_time:
                    df.loc[i, "state"] = 1 if state == "in" else 0
                    break
    df.to_csv(saveLocation, date_format="%Y-%m-%d %H:%M:%S",index=False)


# this is main:
dfLogs = convertLogNote(filepath="lognote.json",on="On",off="Off")
combineLogsAndRawData(dfLogs=dfLogs, raw='11-02Data.csv', saveLocation='temp.csv')