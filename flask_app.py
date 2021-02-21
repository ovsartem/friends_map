from flask import Flask, render_template, request
import tweepy
import pandas as pd
import folium
from geopy import Nominatim
import json

consumer_key = "4P07djysf7I5pgHq1TvGrKIaT"
consumer_secret = "CYbnjGM9Hpt0MdlV2V5i4oYbWYOh2dX7HXBsXSKrecjMRIpLyi"
access_token = "864557136378032129-jMEkKoXfgQoM9xHaNV45auITAyYQvBr"
access_token_secret = "HmUczjCElpkgb2e55j6f2DJ3THaPTEg238qFbhumZOoh2"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


def get_coordinate(coordinate):
    """
    Gets the coordinates of the place
    """
    try:
        geolocator = Nominatim(user_agent='artmanlike').geocode(coordinate)
        location = (geolocator.latitude, geolocator.longitude)
        return location
    except AttributeError:
        return None


def data(screen_name):
    """
    Generates data for creating the map
    """
    friend_nicknames1 = []
    friend_ids = []
    friend_location = []
    friend_screenames = []
    for friend in api.friends(screen_name):
        friend_nicknames1.append(friend.screen_name)
    friend_nicknames = friend_nicknames1[:30]
    for friend in friend_nicknames:
        user = api.get_user(screen_name=friend)
        friend_ids.append(user.id)
        friend_location.append(user.location)
        friend_screenames.append(user.name)
    df = pd.DataFrame(data={"nickname": friend_nicknames, "screenames": friend_screenames,
                            "location": friend_location}, columns=["nickname", "screenames", "location"])
    df["coordinates"] = df["location"].apply(lambda x: get_coordinate(x))
    df = df.dropna(how="any")
    return df


def map_creator(df, screen_name):
    """
    Generates the map of users you follow
    """
    you = api.get_user(screen_name=screen_name)
    loc = you.location
    if len(loc) > 0:
        your_location = get_coordinate(loc)
    else:
        your_location = get_coordinate("Украина, Львов")
    friend_map = folium.Map(
        location=your_location, tiles='cartodbpositron', zoom_start=9)
    folium.TileLayer('stamenterrain').add_to(friend_map)
    friend_map.add_child(folium.Marker(location=[
        your_location[0], your_location[1]], popup="your location", icon=folium.Icon(color='darkblue', icon_color='white', icon='male', angle=0, prefix='fa')))
    for i in range(len(df)):
        market = df.iloc[i]
        data = list(market.iloc())
        friend_map.add_child(folium.Marker(
            location=[data[3][0], data[3][1]], popup=data[1], icon=folium.Icon()))
    return friend_map


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():
    nick = request.form.get("nickname")
    friends_map = map_creator(data(nick), nick)
    return friends_map.get_root().render()


if __name__ == "__main__":
    app.run(debug=False, port=5636)
