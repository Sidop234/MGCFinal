from flask import Flask,render_template,request,redirect
import pickle
import numpy as np
import pandas as pd
import xgboost
import librosa
import joblib

app = Flask(__name__)

model = xgboost.XGBClassifier()
model.load_model('model.json')
scaler_filename = "scaler.save"
sc = joblib.load(scaler_filename)
genre_map = {0:'BLUES',
             1:'CLASSICAL',
            2:'COUNTRY',
            3:'DISCO',
            4:'HIPHOP',
            5:'JAZZ',
            6:'METAL',
            7:'POP',
            8:'REGGAE',
            9:'ROCK'}


#dataframe generator function
def getdataf(filename):
    y, sr = librosa.load(filename)
    # fetching tempo

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)

    # fetching beats

    y_harmonic, y_percussive = librosa.effects.hpss(y)
    tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr)

    # chroma_stft

    chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)

    # rmse

    rmse = librosa.feature.rms(y=y)

    # fetching spectral centroid

    spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    # spectral bandwidth

    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)

    # fetching spectral rolloff

    spec_rolloff = librosa.feature.spectral_rolloff(y=y + 0.01, sr=sr)[0]

    # zero crossing rate

    zero_crossing = librosa.feature.zero_crossing_rate(y)


    mfcc = librosa.feature.mfcc(y=y, sr=sr)

    # metadata dictionary

    metadata_dict = {'chroma_stft_mean': np.mean(chroma_stft), 'chroma_stft_var': np.var(chroma_stft),
                     'rms_mean': np.mean(rmse), 'rms_var': np.var(rmse),
                     'spectral_centroid_mean': np.mean(spec_centroid), 'spectral_centroid_var': np.var(spec_centroid),
                     'spectral_bandwidth_mean': np.mean(spec_bw), 'spectral_bandwidth_var': np.var(spec_bw),
                     'rolloff_mean': np.mean(spec_rolloff), 'rolloff_var': np.var(spec_rolloff),
                     'zero_crossing_rate_mean': np.mean(zero_crossing), 'zero_crossing_rate_var': np.var(zero_crossing),
                     # 'harmony_mean':np.mean(t_harmonics),'harmony_var':np.var(t_harmonics),
                     # 'perceptr_mean':np.mean(perceptual_CQT),'perceptr_var':np.var(perceptual_CQT),
                     'tempo': tempo}

    for i in range(1, 21):
        metadata_dict.update({'mfcc' + str(i) + '_mean': np.mean(mfcc[i - 1])})
        metadata_dict.update({'mfcc' + str(i) + '_var': np.var(mfcc[i - 1])})
    df_meta = pd.DataFrame(metadata_dict, index=[0])
    return df_meta



@app.route('/', methods = ['GET', "POST"])
def hello_world():
    if request.method == "POST":
        f = request.files['file']



    return render_template('index.html')

@app.route('/genre',methods = ["POST"])
def genre():
    if request.method == "POST":
        f = request.files['file']
        m_df = getdataf(f)
        m_df = sc.transform(m_df)

        output = model.predict(m_df)
        predict = genre_map[output[0]]
        return render_template('genre.html',predict = predict, file =f)



    # return render_template('genre.html')

@app.route('/about_us')
def about_us():
    return render_template('Abouts.html')

if __name__ ==  "__main__":
    app.run(debug= True)