import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import numpy as np


def get_fight_URLs(URL):
    r = requests.get(URL)

    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')
    fight_sites = soup.find_all('a', class_=['b-flag b-flag_style_green','b-flag b-flag_style_bordered'])
    
    fight_urls,fight_outcomes = [],[]
    
    for urls in fight_sites:
        fight_urls.append((urls.get('href')))
        fight_outcomes.append(urls.get_text())
    
    return fight_urls,fight_outcomes
    

def get_fight_stats(URL):
    # no point in wasting extra computation power manually getting these from every website
    total_labels = ['Fighter', 'KD', 'Sig.str.landed','Sig.str.attempted', 'Sig.str.%', 'Totalstr.landed','Totalstr.attempted', 'Td.landed','Td.attempted', 'Td%', 'Sub.att', 'Rev.', 'Ctrl']

    sig_strike_labels = ['Fighter', 'Sig.str.landed','Sig.str.attempted', 'Sig.str.%', 'Head.landed','Head.attempted', 'Body.landed','Body.attempted', 'Leg.landed','Leg.attempted', 'Distance.landed','Distance.attempted', 'Clinch.landed','Clinch.attempted', 'Ground.landed','Ground.attempted']


    r = requests.get(URL)

    # Parsing the HTML
    soup = BeautifulSoup(r.content, 'html.parser')
    stats = soup.find_all('p', class_=['b-fight-details__collapse-link_tot','b-fight-details__table-text'])

    statistics = []
    
    #############################################
    #############################################
    ############# get fight stats ###############
    #############################################
    #############################################
    
    for index in range(len(stats)):
        stat = stats[index]
        
        string = stat.get_text().replace("\n","")

        
        if "of" in string:
            land_or_attempt = string.replace("of"," ").split()
            statistics.append([int(land_or_attempt[0]),int(land_or_attempt[1])])

        elif "%" in string:
            new_string = int(string.replace("%",""))
            statistics.append(new_string)

        elif "---" in string:
            statistics.append(string)

        elif ":" in string:
            new_string = string.replace(":"," ").split()
            mins = int(new_string[0])*60
            secs = int(new_string[1])
            time = mins + secs
            statistics.append(time)

        else:
            try:
                statistics.append(float(string))
            except:
                statistics.append(string)
    
    # isolate the aggregate data (not per round)
    total_index = statistics.index('        Totals     ')+1
    sig_index = statistics.index('        Significant Strikes      ')+1
    totals_indices = range(total_index,total_index+20)
    sigs_indices = range(sig_index,sig_index+18)
    

    totals = [statistics[x] for x in totals_indices]
    significants = [statistics[x] for x in sigs_indices]
    
    # random space at the end of the fighters' lastnames... it's pissing me so im removing it manually
    totals[0] = totals[0][:-1]
    totals[1] = totals[1][:-1]
    significants[0] = significants[0][:-1]
    significants[1] = significants[1][:-1]
    

    df_totals = pd.DataFrame(columns = total_labels)
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
#
    return df_totals,df_sigs
    
def get_total_fighter_stats(URL,totals_file,sigs_file,return_data = False):
    urls,outcomes = get_fight_URLs(URL)

    df_totals,df_sigs = get_fight_stats(urls[0])
    
    print("Getting fighter stats...")
    for index in tqdm(range(len(urls[1:]))):
        url = urls[1:][index]
        df_totals_temp,df_sigs_temp = get_fight_stats(url)
        df_totals = pd.concat((df_totals,df_totals_temp))
        df_sigs = pd.concat((df_sigs,df_sigs_temp))
    print("Done!")
    
    df_totals.index = np.arange(0,len(df_totals),1)
    df_sigs.index = np.arange(0,len(df_sigs),1)
    
    if return_data == True:
        return df_totals,df_sigs
    else:
        df_totals.to_csv(totals_file,index = False)
        df_sigs.to_csv(sigs_file,index = False)
        return 0,0
        
## The double champ does what the f*ck he wants ##
    
'''testing out get_stats()'''
#URL = "http://www.ufcstats.com/fight-details/ca8f73d038c4d6e7"
#get_fight_stats(URL)
#df_totals,df_sigs = get_fight_stats(URL)
#print(df_totals)
#print(df_sigs)

'''testing out get_fight_URLs()'''
#URL = "http://www.ufcstats.com/fighter-details/e1147d3d2dabe1ce"
#urls,outcomes = get_fight_URLs(URL)
#print(urls)
#print(outcomes)

'''testing out get_total_fighter_stats()'''
URL = "http://www.ufcstats.com/fighter-details/e1147d3d2dabe1ce"
df_totals,df_sigs = get_total_fighter_stats(URL,"Robert-Whittaker-Totals.csv","Robert-Whittaker-Significants.csv",False)
#print(df_totals)
#print(df_sigs)
