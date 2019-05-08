from flask import Flask, flash, redirect, render_template, request, url_for
import numpy as np
import pandas as pd
from string import punctuation
import psycopg2
from sqlalchemy import create_engine
import unidecode
import re
import os

app = Flask(__name__)


host = 'vevoanalytics.cvw5tscfxqol.us-east-1.redshift.amazonaws.com'
port = '5439'
user = 'edward_kim'
password = 'VivalaVevo!1'
dbname = 'looker1'
engine = create_engine(''.join(['postgresql://', user, ':', password, '@', host, ':', port, '/', dbname]))
conn = None

print(f'redshift user: {user}')
print(f'redshift password: {password}')

def connect_db():
    global conn
    if conn is None:
        conn = psycopg2.connect(f"host='{host}' port={port} dbname='{dbname}' user={user} password={password}")
    return conn

'''
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if conn is not None:
        conn.close()
'''



@app.route('/')
def index():
    print('Inside index function')
    return render_template(
        'selection.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    print('Inside results function')
    conn = connect_db()
    print('Connected to db')
    
    searchtype=request.form.get('searchtype')
    searchquery = request.form.get('searchquery')

    query = f'''
    SELECT v.isrc, v.ytid, v.title, art.name, v.genre
    FROM cs.video v
      INNER JOIN cs.video_artist va on va.isrc = v.isrc
      INNER JOIN cs.artist art on va.url_safe_name = art.url_safe_name
    WHERE v.{searchtype} = '{searchquery}'
    LIMIT 100;
    '''
    query = query.replace('\n', ' ')
    df = pd.read_sql_query(query, conn)

    if df.empty:
        final_tags_list = ['Please enter vailid isrc or ytid']
        hashtags = ['Please enter vailid isrc or ytid']
    else:
        permanent_keywords = ['Vevo', 'music video', 'music']
        artist_list = df['name']
        title = df.iloc[0]['title']
        genre = df.iloc[0]['genre']

        final_tags_list = []
        charcount = 0

        # Format title
        title = re \
        .sub('\(.*?\)', '', title) \
        .strip() \
        .strip(punctuation) \
        .lower() 

        # Add permanent keys
        for keyword in permanent_keywords:
            final_tags_list.append(keyword)
            charcount += len(keyword)

        #Add title
        final_tags_list.append(title)
        charcount += len(title)

        # Add artists
        for artist in artist_list:
            final_tags_list.append(artist)
            charcount += len(artist)

        # Format genre
        genre = genre.replace('-',' ')

        # Add genre
        final_tags_list.append(genre)
        charcount += len(genre)

        # Add genre + music
        genremusic = genre + ' music'
        final_tags_list.append(genremusic)
        charcount += len(genremusic)

        # -----HASHTAG SECTION-----
        hashtags = ['#vevo']

        # Hashtag artists
        for artist in artist_list:
            currentart = artist.lower() \
                                .replace(" ",'') \
                                .replace("'",'') \
                                .replace(',','')
            currentart = unidecode.unidecode(currentart)
            hashtags.append(f'#{currentart}')

        # Hashtag title
        hashtitle = title.lower() \
                    .replace(" ",'') \
                    .replace("'",'') \
                    .replace(',','')
        hashtitle = unidecode.unidecode(hashtitle)
        hashtags.append(f'#{hashtitle}')
    
        hashtags.append('#musicvideo')

    return render_template(
        'results.html',
        final_tags_list = final_tags_list,
        hashtags = hashtags)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)


