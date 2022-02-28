# twitter-weather-stream
https://twitter-weather-stream.herokuapp.com/


Assumptions: Only process tweets with geo tags

Acceptance Criteria:
1. The number of tweets to calculate the sliding average over should be configurable at
    startup time. The input value n should be between 2 and 100.
2. The output of your mini-pipeline should be 2 files, one for the stream of temperatures in
    fahrenheit and 1 file for the stream of the sliding averages.
    a. For this AC. I copied output "Tweet location: Palms - United States of America, temp_f: 73.9, avg of last 5: 73.9"
        which reflects both the stream of temperatures and the sliding average. I understand it was not an example output.
        I used the format for simplicity.

3. Diagram a. I used a simple flask app deployed on heroku. Due to the time constraints of this project, 
I did not further try to resolve the heroku timeout issues.


To use this, 
1. clone the repo.
2. create config.py
3.  populate config vals. 
```
# Twitter API
API_KEY = ''
API_SECRET = ''
BEARER_TOKEN = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
TWITTER_API_URL = 'https://api.twitter.com/2/tweets/sample/stream'

# Weather API
WEATHER_API_KEY = ''
WEATHER_API_URL = 'http://api.weatherapi.com/v1'
```
4. run the flask app with ```flask run``` 
5. navigate to http://localhost:5000
6. start the stream by http://localhost:5000/start?n=
7. wait a few moments and then navigate to http://localhost:5000/stream the text output will begin shortly.
  
Output in browser should look like:
```
Starting stream: 
Tweet location: Santa María de Guía de Gran Canaria, España, temp_f: 62.6, avg of last 6: 62.60 
Tweet location: Ogawa-machi, Saitama, temp_f: 58.1, avg of last 6: 60.35 
Tweet location: Winter Haven, FL, temp_f: 68.0, avg of last 6: 62.90 
Tweet location: Federal Capital Territory, Nigeria, temp_f: 75.4, avg of last 6: 66.03 
Tweet location: Lanús Oeste, Argentina, temp_f: 69.8, avg of last 6: 66.78 
Tweet location: Texas, USA, temp_f: 43.2, avg of last 6: 62.85 
Tweet location: Kashiwa-shi, Chiba, temp_f: 56.1, avg of last 6: 61.77 
Tweet location: Boeun-gun, Republic of Korea, temp_f: 51.8, avg of last 6: 60.72 
Tweet location: Paradise, NV, temp_f: 52.0, avg of last 6: 58.05 
Tweet location: Paradise, NV, temp_f: 52.0, avg of last 6: 54.15 
Tweet location: Krembangan, Indonesia, temp_f: 84.2, avg of last 6: 56.55 
Tweet location: Nagoya-shi Nakamura, Aichi, temp_f: 53.6, avg of last 6: 58.28 
Tweet location: New Delhi, India, temp_f: 69.8, avg of last 6: 60.57 
Tweet location: Plantation, FL, temp_f: 69.1, avg of last 6: 63.45 
Tweet location: İstanbul, Türkiye, temp_f: 44.6, avg of last 6: 62.22 
Tweet location: Brest, France, temp_f: 48.2, avg of last 6: 61.58 
Tweet location: Şanlıurfa Merkez, Şanlıurfa, temp_f: 51.3, avg of last 6: 56.10 
Tweet location: Bulgaria, temp_f: 25.3, avg of last 6: 51.38 
```