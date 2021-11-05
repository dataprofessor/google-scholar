import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests, lxml, os

# Functions for retrieving Google Scholar data
# Source: https://dev.to/dimitryzub/scrape-google-scholar-with-python-32oh

headers = {
    'User-agent':
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
}

proxies = {
  'http': os.getenv('HTTP_PROXY')
}

def get_profile_1(ORGID):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}', headers=headers, proxies=proxies).text

  soup = BeautifulSoup(html, 'lxml')

  entry_list = {'Name':[],'ID':[],'Affiliation':[], 'Interests':[], 'Citations':[]}

  for result in soup.select('.gs_ai_chpr'):
    name = result.select_one('.gs_ai_name a').text
    gsID = result.select_one('.gs_ai_name a')['href'].strip('/citations?hl=en&user=')
    affiliations = result.select_one('.gs_ai_aff').text

    try:
      interests = result.select_one('.gs_ai_one_int').text
    except:
      interests = None
    citations = result.select_one('.gs_ai_cby').text.split(' ')[2]
    
    entry_list['Name'].append(name)
    entry_list['ID'].append(gsID)
    entry_list['Affiliation'].append(affiliations)
    entry_list['Interests'].append(interests)
    entry_list['Citations'].append(citations)

  df = pd.DataFrame(entry_list)
  
  return df

def get_profile_2(ORGID, next_link, page_index):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}&after_author={next_link}&astart={page_index}', headers=headers, proxies=proxies).text
  soup = BeautifulSoup(html, 'lxml')

  entry_list = {'Name':[],'ID':[],'Affiliation':[], 'Interests':[], 'Citations':[]}

  for result in soup.select('.gs_ai_chpr'):
    name = result.select_one('.gs_ai_name a').text
    gsID = result.select_one('.gs_ai_name a')['href'].strip('/citations?hl=en&user=')
    affiliations = result.select_one('.gs_ai_aff').text

    try:
      interests = result.select_one('.gs_ai_one_int').text
    except:
      interests = None
    citations = result.select_one('.gs_ai_cby').text.split(' ')[2]
    
    entry_list['Name'].append(name)
    entry_list['ID'].append(gsID)
    entry_list['Affiliation'].append(affiliations)
    entry_list['Interests'].append(interests)
    entry_list['Citations'].append(citations)

  df = pd.DataFrame(entry_list)
  
  return df

# Retrieves the next link from the Google Scholar Profile page

def get_next_link_1(ORGID):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}', headers=headers, proxies=proxies).text
  soup = BeautifulSoup(html, 'lxml')
  btn = soup.find('button', {'aria-label': 'Next'})
  btn_onclick = btn['onclick']
  next_link = btn_onclick.split('\\')[-3].lstrip('x3d')
  return next_link

# Retrieves the next link from the Google Scholar Profile page
def get_next_link_2(ORGID, next_link, page_index):
  html = requests.get(f'https://scholar.google.com/citations?view_op=view_org&hl=en&org={ORGID}&after_author={next_link}&astart={page_index}', headers=headers, proxies=proxies).text
  soup = BeautifulSoup(html, 'lxml')
  btn = soup.find('button', {'aria-label': 'Next'})
  btn_onclick = btn['onclick']
  #next_link = btn_onclick.split('\\')[-3].lstrip('x3d')
  next_link = btn_onclick.split('\\')[-3][3:]
  return next_link

############################
# Display app content

st.set_page_config(layout='wide')

st.markdown('''
# Scholar App
This App retrieves researcher citation data from ***Google Scholar***.
''')

st.sidebar.header('Scholar App Settings')

org_list = {'Mahidol University':'5426792000072695308',
            'Chulalongkorn University':'10884788013512991188',
            'Thammasat University':'10241031385301082500',
            'Kasetsart University':'18390568157380693597',
            'Khon Kaen University':'4903137502637677605',
            'Chiang Mai University':'14261461339511303947',
            'Prince of Songkla University':'7941550691896662469',
            'Suranaree University of Technology':'14596385902361520767',
            "King Mongkut's Institute of Technology Ladkrabang":"13187086001343916751"}

orgid = st.sidebar.selectbox('Select a University', 
                              ('Mahidol University', 
                              'Chulalongkorn University', 
                              'Thammasat University',
                              'Kasetsart University',
                              'Khon Kaen University',
                              'Chiang Mai University',
                              'Prince of Songkla University',
                              'Suranaree University of Technology',
                              "King Mongkut's Institute of Technology Ladkrabang") )
orgid = org_list[orgid]

query_size = st.sidebar.slider('Query size', 10, 50, 10, 10)
query_size = int(query_size/10)

p_index = 10
df_list = []

for i in range(query_size):
  if i == 0:
    df1 = get_profile_1(orgid)
    df_list.append(df1)
    nxt_link_1 = get_next_link_1(orgid)
    #p_index += 10
    print(nxt_link_1, p_index)
  if i == 1:
    df2 = get_profile_2(orgid, nxt_link_1, p_index)
    nxt_link_2 = get_next_link_2(orgid, nxt_link_1, p_index)
    df_list.append(df2)
    p_index += 10
    print(nxt_link_2, p_index)
  if i > 1:
    df3 = get_profile_2(orgid, nxt_link_2, p_index)
    nxt_link_2 = get_next_link_2(orgid, nxt_link_2, p_index)
    df_list.append(df3)
    p_index += 10
    print(nxt_link_2, p_index)

df = pd.concat(df_list)
df.reset_index(drop=True, inplace=True)

df