from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
import requests




app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nbadata.db'

#app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

db = SQLAlchemy(app)



class Players(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(50), nullable = False)
    last_name = db.Column(db.String(50), nullable = False)


def get_player_data(first_name, last_name):
    url = f'https://www.thesportsdb.com/api/v1/json/1/searchplayers.php?p={ first_name } { "" + last_name }'


    r = requests.get(url).json()
    return r

def get_player_data_stats(first_name, last_name):
    url = f'https://www.balldontlie.io/api/v1/players?search={ first_name } { "" + last_name }'


    r = requests.get(url).json()

    player_id = r['data'][0]['id']

    url1 = f'https://www.balldontlie.io/api/v1/season_averages?season=2020&player_ids[]={ player_id }'

    r1 = requests.get(url1).json()

    
    return r1

def get_player_wiki(first_name, last_name):
    url = f'https://en.wikipedia.org/w/api.php?action=query&titles={ first_name } { "" + last_name }&prop=extracts&format=json&indexpageids'

    r = requests.get(url).json()

    return r
def get_player_wiki_text(first_name, last_name):
    r = get_player_wiki(first_name, last_name)
    soup = BeautifulSoup(r['query']['pages'][get_player_wiki_id(first_name, last_name)]['extract'])
    return soup.get_text()

def get_player_wiki_id(first_name, last_name):
    url = f'https://en.wikipedia.org/w/api.php?action=query&titles={ first_name } { "" + last_name }&prop=extracts&format=json&indexpageids'

    r = requests.get(url).json()


    return r['query']['pageids'][0]

@app.route('/', methods=['GET'])
def index():
    # we will now query all of the information in the cities database and store it in a variable
    players = Players.query.all()



    player_data = []
    for player in players:
        r = get_player_data(player.first_name, player.last_name)
        r1 = get_player_data_stats(player.first_name, player.last_name)

        play = {
            'player_first_name':r['player'][0]['strPlayer'].split(" ")[0],
            'player_last_name':r['player'][0]['strPlayer'].split(" ")[1],
            'player_name' : r['player'][0]['strPlayer'],
            'team_name' : r['player'][0]['strTeam'],
            'position' : r['player'][0]['strPosition'],
            'player_img' : r['player'][0]['strCutout'],
            'player_height' : r['player'][0]['strHeight'],
            'player_ppg' : r1['data'][0]['pts'],
            'player_rpg' : r1['data'][0]['reb'],
            'player_apg': r1['data'][0]['ast'],
            'player_mpg': r1['data'][0]['min'],
            'player_info_img':r['player'][0]['strThumb'],

        }

        player_data.append(play)





    return render_template('index.html', player_data=player_data)

@app.route('/', methods=['POST'])
def index_post():


    new_first_name = request.form.get('fname')
    new_last_name = request.form.get('lname')

    db.session.add(Players(first_name=new_first_name, last_name = new_last_name))
    db.session.commit()



    return redirect(url_for('index'))

@app.route('/delete/<first_name>/<last_name>')
def delete_player(first_name, last_name):

    if(first_name == 'LeBron'):
        first_name = 'Lebron'
    if(last_name=='Dončić'):
        last_name = "Doncic"

    player = Players.query.filter_by(first_name=first_name, last_name=last_name).first()
    db.session.delete(player)
    db.session.commit()

    #flash(f'Successfully deleted { city.name }')

    return redirect(url_for('index'))


@app.route('/player_info/<first_name>/<last_name>')
def player_info(first_name, last_name):

   return render_template('player_info.html', first_name=first_name, last_name=last_name, get_player_data=get_player_data, get_player_wiki_text=get_player_wiki_text)
