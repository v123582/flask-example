from flask import Flask, jsonify, request
from flask import render_template
import requests, json
import pandas as pd
import numpy as np
import datetime
from dateutil.parser import parse

app = Flask(__name__)
 
 
def get_df():
    countries = {
        'tw': ['MQAD2TA/A', 'MQAG2TA/A','MQAC2TA/A','MQAF2TA/A'],
        'cn': ['MQA62CH/A', 'MQA92CH/A','MQA52CH/A','MQA82CH/A'],
    }
 
    Silvers = ['MQAK2', 'MQAR2', 'MQAD2', 'MQAN2', 'MQAV2', 'MQAG2',
               'MQCT2', 'MQCL2', 'MQAY2', 'MQA62',
               'MQCW2', 'MQCP2', 'MQC22', 'MQA92']
 
    Gray = ['MQAJ2', 'MQAQ2', 'MQAC2', 'MQAM2', 'MQAU2', 'MQAF2',
            'MQCR2', 'MQCK2', 'MQAX2', 'MQA52',
            'MQCV2', 'MQCN2', 'MQC12', 'MQA82']
 
    sixfour = ['MQAK2', 'MQAR2', 'MQAD2', 'MQCT2', 'MQCL2', 'MQAY2', 'MQA62', 
               'MQCR2', 'MQCK2', 'MQAX2', 'MQA52', 'MQAJ2', 'MQAQ2', 'MQAC2']
 
    res = []
    for country in countries:
        for type in countries[country]:
            d = {}
            d['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            d['country'] = country
            d['type'] = type
            d['color'] = 'Silvers' if type[0:5] in Silvers else 'Gray'
            d['size'] = '64GB' if type[0:5] in sixfour else '256GB'           
            url = 'https://www.apple.com/%s/shop/delivery-message?parts.0=%s&little=true' % (country, type)
            r = requests.get(url)
            response = json.loads(r.text)
            d['quote'] = response['body']['content']['deliveryMessage'][type]['quote']
            res.append(d)
 
    df = pd.DataFrame(res)
    return df

df = {'data': pd.DataFrame(), 'time': None}


@app.route("/update")
def update():
    global df
    with open('my_csv.csv', 'a') as f:
        get_df().to_csv(f, header=False)
    df['data'] = json.loads(get_df().to_json())
    df['time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify(df)

@app.route("/data")
def data():
    global df
    return jsonify(df)

@app.route("/")
def hello():
 
    country = request.values.get('country', '')
    index = request.values.get('index', 'color')
    column = request.values.get('column', 'size')
     
    # df = get_df()
    df = pd.read_csv('my_csv.csv')
    print(df)
    pivot = pd.pivot_table(df, values='quote', index=[index],
        columns=[column], aggfunc=np.size)
 
    if country:
        return render_template("index.html", df=df[df['country']==country].to_html(), pivot=pivot.to_html(), index=index, column=column)
    return render_template("index.html", df=df.to_html(), pivot=pivot.to_html(), index=index, column=column)
 
if __name__ == "__main__":
    app.run(debug=True)
