import json
from collections import deque
from time import sleep
import requests
from flask import Flask, request, render_template
import config
import os

app = Flask(__name__)

last_n_temps = deque()
n_temps = 0


@app.route("/")
def welcome():
    if os.path.exists("tweet_temperature_stream.txt"):
        os.remove("tweet_temperature_stream.txt")
    else:
        print("The file does not exist")
    global n_temps
    # Application is gated on when n_temps == 0
    n_temps = 0
    return render_template('index.html')


@app.route("/start")
def start():
    """
        Assumptions: Only process tweets with geo tags

        Acceptance Criteria:
        1. The number of tweets to calculate the sliding average over should be configurable at
            startup time. The input value n should be between 2 and 100.
        2. The output of your mini-pipeline should be 2 files, one for the stream of temperatures in
            fahrenheit and 1 file for the stream of the sliding averages.
            a. For this AC. I copied output "Tweet location: Palms - United States of America, temp_f: 73.9, avg of last 5: 73.9"
                which reflects both the stream of temperatures and the sliding average. I understand it was not an example output.
                I used the format for simplicity.

        3. Diagram
            a. I used a simple flask app deployed on heroku.
    """

    global n_temps
    n = request.args.get('n')
    if n is None:
        return "Please enter an integer value for n in the form of localhost:5000/start?n="
    n_temps = int(n)

    if 2 <= n_temps <= 100:
        return main()
    else:
        return "Please enter an integer value between 2-100."


def create_url():
    return config.TWITTER_API_URL


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    bearer_token = config.BEARER_TOKEN
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampledStreamPython"
    return r


def connect_to_endpoint(url):
    params = {
        "tweet.fields": "geo,source",
        "expansions": "geo.place_id",
        "place.fields": "full_name,geo,id,place_type",
        "user.fields": "location"
    }
    response = requests.request("GET", url, auth=bearer_oauth, stream=True, params=params)
    print(response.status_code)
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            if json_response is None:
                return "Json Response is None"
            if 'geo' in json_response['data']:
                geo = json_response['data']['geo']
                for _ in geo:
                    process_tweet(json_response)
                # print(json.dumps(json_response, indent=4, sort_keys=True))
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


def process_tweet(tweet):
    # tweet = json.dumps(tweet, indent=4, sort_keys=True)
    # print(tweet)
    place_id = tweet['data']['geo']['place_id']
    full_name = tweet['includes']['places'][0]['full_name']
    bbox = tweet['includes']['places'][0]['geo']['bbox']
    geo_type = tweet['includes']['places'][0]['geo']['type']
    place_type = tweet['includes']['places'][0]['place_type']

    temp_f = ''
    if 'coordinates' in tweet['data']['geo']:
        coordinates = tweet['data']['geo']['coordinates']['coordinates']
        coordinates_type = tweet['data']['geo']['coordinates']['type']
        # print("Coordinates found {} {}".format(coordinates, coordinates_type))
        if coordinates_type == 'polygon':
            print("Polygon found, print the tweet! {}".format(tweet))
        latitude = "{:.4f}".format(coordinates[1])
        longitude = "{:.4f}".format(coordinates[0])
        point = "{},{}".format(latitude, longitude)
        temp_f = weather_for_coordinates(point)
        add_temp_to_list(temp_f)
    else:
        # print("finding coordinates for bbox: {}".format(bbox))
        coordinates = find_centroid(bbox)
        # print("coordinates for centroid are: {}".format(coordinates))
        temp_f = weather_for_coordinates(coordinates)
        # print("adding temp_f: {}, to list".format(temp_f))
        add_temp_to_list(temp_f)

    avg = avg_last_n_tweet_avgs()

    # print("Tweet location name: {}, type: {}, id: {}, bbox: {}, place_type: {}, temp_f: {}, avg: {}".format(full_name,
    #                                                                                                         geo_type,
    #                                                                                                         place_id,
    #                                                                                                         bbox,
    #                                                                                                         place_type,
    #                                                                                                         temp_f,
    #                                                                                                         avg))
    with open("tweet_temperature_stream.txt", "a") as fo:
        fo.write("Tweet location: {}, temp_f: {}, avg of last {}: {} \n".format(full_name, temp_f, n_temps, avg))


# returns temp_f
def weather_for_coordinates(coordinates):
    url = config.WEATHER_API_URL + "/current.json"
    api_key = config.WEATHER_API_KEY
    params = {
        "key": api_key,
        "q": coordinates
    }

    response = requests.request("GET", url, params=params)
    print(response.status_code)

    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            if 'temp_f' in json_response['current']:
                temp_f = json_response['current']['temp_f']
                country = json_response['location']['country']
                name = json_response['location']['name']
                region = json_response['location']['region']
                print("temp: {}, country: {}, name: {}, region: {}".format(temp_f, country, name, region))
                return temp_f
            # print(json.dumps(json_response, indent=4, sort_keys=True))
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )


# adds temp to queue and ensures list does not exceed len of 5.
def add_temp_to_list(temp):
    last_n_temps.append(temp)
    while len(last_n_temps) > n_temps:
        last_n_temps.popleft()


# returns avg of list
def avg_last_n_tweet_avgs():
    if len(last_n_temps) == 0:
        return 0.00
    avg = sum(last_n_temps) / len(last_n_temps)
    return "{:.2f}".format(avg)


# find centroid of bbox
def find_centroid(bbox):
    """
    "bbox": [
           -74.026675,
           40.683935,
           -73.910408,
           40.877483
      ]
    """

    latitude = (bbox[1] + bbox[3]) / 2.0
    longitude = (bbox[0] + bbox[2]) / 2.0
    latitude = "{:.4f}".format(latitude)
    longitude = "{:.4f}".format(longitude)
    centroid = "{},{}".format(latitude, longitude)
    return centroid


@app.route('/stream')
def stream():
    def generate():
        with open('tweet_temperature_stream.txt') as f:
            while True:
                yield f.read()
                sleep(1)

    return app.response_class(generate(), mimetype='text/plain')


def main():
    url = create_url()
    timeout = 0
    while n_temps != 0:
        connect_to_endpoint(url)
        timeout += 1


if __name__ == "__main__":
    main()
