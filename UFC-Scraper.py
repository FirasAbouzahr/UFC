import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_stats(URL):
    # no point in wasting extra computation power manually getting these from every website
    total_labels = ['Fighter', 'KD', 'Sig.str.landed','Sig.str.attempted', 'Sig.str.%', 'Totalstr.landed','Totalstr.attempted', 'Td.landed','Td.attempted', 'Td%', 'Sub.att', 'Rev.', 'Ctrl']

    sig_strike_labels = ['Fighter', 'Sig.str.landed','Sig.str.attempted', 'Sig.str.%', 'Head.landed','Head.attempted', 'Body.landed','Body.attempted', 'Leg.landed','Leg.attempted', 'Distance.landed','Distance.attempted', 'Clinch.landed','Clinch.attempted', 'Ground.landed','Ground.attempted']


    r = requests.get(URL)

    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')
    stats = soup.find_all('p', class_='b-fight-details__table-text')

    totals = []
    significants = []

    #############################################
    #############################################
    #################  TOTALS ###################
    #############################################
    #############################################

    for index in range(20):
        stat = stats[index]

        if index <= 1:
            totals.append(stat.get_text().replace("\n","")[:-1])

        else:
            string = stat.get_text().replace(" ","").replace("\n","")
            if "of" in string:
                land_or_attempt = string.replace("of"," ").split()
                totals.append([int(land_or_attempt[0]),int(land_or_attempt[1])])

            elif "%" in string:
                new_string = int(string.replace("%",""))
                totals.append(new_string)

            elif "---" in string:
                totals.append(string)

            elif ":" in string:
                new_string = string.replace(":"," ").split()
                mins = int(new_string[0])*60
                secs = int(new_string[1])
                time = mins + secs
                totals.append(time)

            else:
                totals.append(float(string))
                
    #############################################
    #############################################
    ################# SIG STRIKES ###############
    #############################################
    #############################################

    for index in range(40,58):
        stat = stats[index]
        i = index - 40 # lets reset this to zero to make this easier on me

        if i <= 1:
            significants.append(stat.get_text().replace("\n","")[:-1])
            
        else:
            string = stat.get_text().replace(" ","").replace("\n","")
            if "of" in string:
                land_or_attempt = string.replace("of"," ").split()
                significants.append([int(land_or_attempt[0]),int(land_or_attempt[1])])

            elif "%" in string:
                new_string = int(string.replace("%",""))
                significants.append(new_string)
                
            elif "---" in string:
                significants.append(string)
        
            else:
                significants.append(float(string))
                
    df_totals = pd.DataFrame(columns = total_labels)
    print(df_totals)
    total_1,total_2 = [],[]
    for i in range(len(totals)):
        if i % 2 == 0:
            if isinstance(totals[i], list) == True:
                total_1.extend((totals[i][0],totals[i][1]))
            else:
                total_1.append(totals[i])
        else:
            if isinstance(totals[i], list) == True:
                total_2.extend((totals[i][0],totals[i][1]))
            else:
                total_2.append(totals[i])
    print(totals,len(total_1),len(total_2),len(total_labels))

    df_sigs = pd.DataFrame(columns = sig_strike_labels)
    significant_1,significant_2 = [],[]
    for i in range(len(significants)):
        if i % 2 == 0:
            if isinstance(significants[i], list) == True:
                significant_1.extend((significants[i][0],significants[i][1]))
            else:
                significant_1.append(significants[i])
        else:
            if isinstance(significants[i], list) == True:
                significant_2.extend((significants[i][0],significants[i][1]))
            else:
                significant_2.append(significants[i])
                
    df_totals.loc[0] = total_1
    df_totals.loc[1] = total_2
    df_sigs.loc[0] = significant_1
    df_sigs.loc[1] = significant_2

    return df_totals,df_sigs


URL = "http://www.ufcstats.com/fight-details/6d04fbef6b8e4551"
df_totals,df_sigs = get_stats(URL)
print(df_totals)
print(df_sigs)
