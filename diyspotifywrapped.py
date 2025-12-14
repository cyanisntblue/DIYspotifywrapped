import os
import pandas as pd
from datetime import datetime


def main():
    directory = autoDetectDirectory()
    if directory == False:
        directory = removeQuotes(greenInput('Enter the "Spotify Extended Streaming History" Directory > '))
    else:
        print("Path Auto-Detected")

    print("Loading song data! May take a second...")
    df = loadSongData(directory)

    #df = pd.read_csv('spotify_data.csv')
    #df['ts'] = pd.to_datetime(df['ts'])

    years = list({i for i in df['ts'].dt.year}) # retrieve all available years

    selectyear = True

    while True:

        # year selection loop
        while selectyear == True:

            year = greenInput(f"From which year would you like data? ({min(df['ts']).year}-{max(df['ts']).year}) > ")

            if year.lower() == 'quit':
                exit()
            elif year.lower() == 'all' or year.lower() == 'all time':
                break
            elif not year.isdigit():
                print(f"invalid year selection, available years are: {years}")
            elif int(year) in years:
                break
            else:
                print(f"invalid year selection, available years are: {years}")
            
        selectyear = False


        # START choice selection loop
        choice = greenInput(f"What would you like to see? (Artists, Songs, Albums) type quit to exit > ")

        if choice.lower() == 'quit':
            exit()
        elif choice.lower() == 'artist' or choice.lower() == 'artists' or choice.lower() == 'ar':
            count = greenInput("How many to display? (default 5) > ")

            data = yearFilter(df, year).groupby('master_metadata_album_artist_name')[['sec_played']].sum().sort_values('sec_played',ascending=False).head(numToDisplay(count))
            print(f"\nTop artists of {year}:")

            for i, song in enumerate(data.index):
                print(f"{i+1}. {song}")
            print()
            selectyear = True

        elif choice.lower() == 'song' or choice.lower() == 'songs' or choice.lower() == 's':
            count = greenInput("How many to display? (default 5) > ")

            data = yearFilter(df, year).groupby(['master_metadata_track_name', 'master_metadata_album_artist_name', 'spotify_track_uri'])[['sec_played']].sum().sort_values('sec_played',ascending=False).head(numToDisplay(count))
            print(f"\nTop songs of {year}:")

            for i, song in enumerate(data.index):
                print(f"{i+1}. {song[0]} - {song[1]}") # [0] is song name, [1] is artist name, [2] is spotify id
            print()
            selectyear = True

        elif choice.lower() == 'album' or choice.lower() == 'album' or choice.lower() == 'al':
            count = greenInput("How many to display? (default 5) > ")

            data = yearFilter(df, year).groupby('master_metadata_album_album_name')[['sec_played']].sum().sort_values('sec_played',ascending=False).head(numToDisplay(count))
            print(f"\nTop albums of {year}:")

            for i, song in enumerate(data.index):
                print(f"{i+1}. {song}")
            print()
            selectyear = True
        else:
            print("choice not recognized, please try again")
        # END choice selection loop



def autoDetectDirectory():
    # auto-detect if this program is ran INSIDE the target folder
    if os.path.dirname(os.path.realpath(__file__)).endswith("Spotify Extended Streaming History"):
        directory = os.path.dirname(os.path.realpath(__file__))
        return directory
    # implement elif in case the program is ran neighboring the target folder?
    else:
        return False

def removeQuotes(directory):
    # remove single quotes around directory (if drag and dropped to terminal)
    if directory.startswith("'") and directory.endswith("'"):
        directory = directory[1:-1]
    return directory

def loadSongData(directory):
    # list of all audio streaming history files
    files = [file.name for file in os.scandir(directory) if ('Streaming_History_Audio' in file.name)]

    df = pd.DataFrame()
    for file in files:
        toAdd = pd.read_json(f"{directory}/{file}")
        df = pd.concat([df,toAdd])

    # DATA CLEANING!

    # ms to sec
    df['ms_played'] = df['ms_played'] / 1000
    df.rename(columns={'ms_played': 'sec_played'}, inplace=True)

    # convert date/time column to datetime object for easy comparison
    df['ts'] = pd.to_datetime(df['ts'], format='%Y-%m-%dT%H:%M:%SZ')

    return df

def yearFilter(data, year):
    # return top of all time? i think
    if year == 'all' or year == 'all time':
        return data
    else: 
        return (data[(data['ts'] >= datetime(int(year),1,1)) & (data['ts'] <= datetime(int(year),12,31))]).sort_values('ts')

def numToDisplay(count):
    # number of songs/artists/albums to display (defaults to 5 if input invalid)
    if count.isdigit():
        pass
    else:
        count = 5
    return int(count)

def greenInput(msg): # input() but green!
    print(msg + "\033[92m", end="")
    userinput = input()
    print("\033[0m", end="")
    return userinput

if __name__ == "__main__":
    main()