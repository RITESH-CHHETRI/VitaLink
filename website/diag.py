from flask import Blueprint, render_template, request, flash, jsonify,redirect, url_for,send_file
from flask_login import login_required, current_user
from .models import User, Post, Notification, Message
from . import db
import json
from werkzeug.utils import secure_filename
import os
import hashlib
import json
import joblib
import numpy as np
import pandas as pd
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
import torch
import torchvision
from .bot import chat
from twilio.twiml.messaging_response import MessagingResponse
import requests
from .diagnosis import malaria_pred, predict_liver_disease, predictpneumonia, predict_disease, fetch_disease_info, predict_early_diabetes, get_precautions

diag = Blueprint('diag', __name__)


def doctor_search(doctor_type):
    base_url = "https://www.google.com/search?q="
    query = doctor_type.split(" ")
    query = "+".join(query)
    query = f"{query}+near+me"
    final_url = base_url + query

    return final_url

def med_search(medicine):
    split_med = medicine.split(" ")
    if len(split_med) > 1:
        medicine = "+".join(split_med)
        url = f"https://www.drugs.com/search.php?searchterm={medicine}"

    url = f"https://www.drugs.com/search.php?searchterm={medicine}"

    return url



@diag.route('/diagnosis',methods=['GET'])
def diagnosis():
    return render_template('diagnosis.html')

@diag.route('/disease',methods=['GET','POST'])
def disease():
    if request.method == 'POST':
        symptoms = request.form.getlist('symptoms')
        print(symptoms)
        prediction = predict_disease(symptoms)
        disease_info = fetch_disease_info(disease=prediction)
        return render_template('disease.html', symptoms=symptoms, prediction=prediction, disease_info=disease_info)
    else:
        return render_template('index.html')



@diag.route('/diabetes',methods=['GET','POST'])
def diabetes():
    if request.method == 'POST':
        age = request.form.get('age')
        status = request.form.get('status')
        polyuria = request.form.get('polyuria')
        polydipsia = request.form.get('polydipsia')
        weight = request.form.get('weight')
        weakness = request.form.get('weakness')
        polyphagia = request.form.get('polyphagia')
        genital_thrush = request.form.get('genital_thrush')
        visual_blurring = request.form.get('visual_blurring')
        itching = request.form.get('itching')
        irritability = request.form.get('irritability')
        delayed_healing = request.form.get('delayed_healing')
        partial_paresis = request.form.get('partial_paresis')
        muscle_stiffness = request.form.get('muscle_stiffness')
        alopecia = request.form.get('alopecia')
        obesity = request.form.get('obesity')

        prediction = predict_early_diabetes(age, status, polyuria, polydipsia, weight, weakness,
                                            polyphagia, genital_thrush, visual_blurring, itching,
                                            irritability, delayed_healing, partial_paresis,
                                            muscle_stiffness, alopecia, obesity)

        return render_template('diabetes.html', prediction=prediction)
    else:
        return render_template('diabindex.html')


@diag.route('/liver',methods=['GET','POST'])
def liver():
    if request.method == 'POST':
        age = request.form.get('age')
        gender = request.form.get('gender')
        total_bilirubin = request.form.get('total_bilirubin')
        direct_bilirubin = request.form.get('direct_bilirubin')
        alk_phosphate = request.form.get('alk_phosphate')
        alamine_aminotransferase = request.form.get('alamine_aminotransferase')
        aspartate_aminotransferase = request.form.get('aspartate_aminotransferase')
        total_proteins = request.form.get('total_proteins')
        albumin = request.form.get('albumin')
        ratio = request.form.get('ratio')
        print(age, gender, total_bilirubin, direct_bilirubin, alk_phosphate, alamine_aminotransferase,
              aspartate_aminotransferase, total_proteins, albumin, ratio)
        print("test")
        liver_disease_prob = predict_liver_disease(age, gender, total_bilirubin, direct_bilirubin,
                                                   alk_phosphate, alamine_aminotransferase,
                                                   aspartate_aminotransferase, total_proteins,
                                                   albumin, ratio)

        return render_template('liver.html', liver_disease_prob=liver_disease_prob)
    else:
        return render_template('livindex.html')


@diag.route('/malaria',methods=['GET','POST'])
def malaria():
    if request.method == 'POST':
        uploaded_image = request.files['image']
        if uploaded_image.filename != '':
            result = malaria_pred(uploaded_image)
            return render_template('malaria.html', result=result)
    return render_template('malindex.html')




@diag.route('/pneumonia',methods=['GET','POST'])
def pneumonia():
    if request.method == 'POST':
        uploaded_image = request.files['image']
        prediction, confidence = predictpneumonia(uploaded_image)

        if prediction == "safe":
            result_message = f"The patient is not suffering from Pneumonia with Confidence: {confidence*100:.2f}%"
        else:
            result_message = f"The patient is suffering from {prediction} with Confidence: {confidence*100:.2f}%"

        if prediction != "safe":
            error_message = "If you are a patient, consult with one of the following doctors immediately"
            specialists = [
                ("Primary Care Doctor", doctor_search("Primary Care Doctor")),
                ("Lung Specialist", doctor_search("Lung Specialist")),
            ]
        else:
            error_message = ""
            specialists = []

        return render_template('pneumonia.html', result_message=result_message,
                               error_message=error_message, specialists=specialists)

    return render_template('pneumonia.html')


@diag.route('/firstaid', methods=['GET','POST'])
def test2():
    if request.method == 'POST':
        data = request.form.get('data')
        if data:
            data=chat(data)
            return f'{data}'
        else:
            return f'empty data'
    return render_template('firstaid.html')


@diag.route('/api',methods=['GET','POST'])
def api():
    if request.method == 'GET':
        modes = ["diseasepred", "malariapred", "pneumoniapred", "diabetespred", "liverpred", "firstaid"]
        return jsonify({'message': 'Parameters needed:mode', 'modes': modes})
    elif request.method == 'POST':
        mode = request.form.get('mode')
        print(mode)
        if mode == "diseasepred":
            symptoms = request.form.getlist('symptoms')
            prediction = predict_disease(symptoms)
            disease_info = fetch_disease_info(disease=prediction)
            response_data = {
                'symptoms': symptoms,
                'prediction': prediction,
                'disease_info': disease_info
            }
            return jsonify(response_data)
        elif mode == "malariapred":
            uploaded_image = request.files['image']
            result = malaria_pred(uploaded_image)
            response_data = {
                'result': result
            }
            return jsonify(response_data)
        elif mode == "pneumoniapred":
            uploaded_image = request.files['image']
            prediction, confidence = predictpneumonia(uploaded_image)
            if prediction == "safe":
                result_message = f"The patient is not suffering from Pneumonia with Confidence: {confidence*100:.2f}%"
            else:
                result_message = f"The patient is suffering from {prediction} with Confidence: {confidence*100:.2f}%"

            response_data = {
                'result_message': result_message,
            }
            return jsonify(response_data)
        elif mode == "diabetespred":
            age = request.form.get('age')
            status = request.form.get('status')
            polyuria = request.form.get('polyuria')
            polydipsia = request.form.get('polydipsia')
            weight = request.form.get('weight')
            weakness = request.form.get('weakness')
            polyphagia = request.form.get('polyphagia')
            genital_thrush = request.form.get('genital_thrush')
            visual_blurring = request.form.get('visual_blurring')
            itching = request.form.get('itching')
            irritability = request.form.get('irritability')
            delayed_healing = request.form.get('delayed_healing')
            partial_paresis = request.form.get('partial_paresis')
            muscle_stiffness = request.form.get('muscle_stiffness')
            alopecia = request.form.get('alopecia')
            obesity = request.form.get('obesity')

            prediction = predict_early_diabetes(age, status, polyuria, polydipsia, weight, weakness,
                                                polyphagia, genital_thrush, visual_blurring, itching,
                                                irritability, delayed_healing, partial_paresis,
                                                muscle_stiffness, alopecia, obesity)

            response_data = {
                'prediction': str(prediction[0])
            }
            return jsonify(response_data)
        elif mode == "liverpred":
            age = request.form.get('age')
            gender = request.form.get('gender')
            total_bilirubin = request.form.get('total_bilirubin')
            direct_bilirubin = request.form.get('direct_bilirubin')
            alk_phosphate = request.form.get('alk_phosphate')
            alamine_aminotransferase = request.form.get('alamine_aminotransferase')
            aspartate_aminotransferase = request.form.get('aspartate_aminotransferase')
            total_proteins = request.form.get('total_proteins')
            albumin = request.form.get('albumin')
            ratio = request.form.get('ratio')
            liver_disease_prob = predict_liver_disease(age, gender, total_bilirubin, direct_bilirubin,
                                                    alk_phosphate, alamine_aminotransferase,
                                                    aspartate_aminotransferase, total_proteins,
                                                    albumin, ratio)
            return jsonify({'liver_disease_prob': str(liver_disease_prob)})
        elif mode=="firstaid":
            quest = request.form.get('quest')
            print(quest)
            tag, data=chat(quest)
            return jsonify({'tag':tag,'data': data})
    else:
        return 'Method not allowed'

botstat=0

@diag.route('/bot', methods=['POST'])
def bot():
    global botstat
    print("response")
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    if botstat=="symptoms":
        print("entered sym")
        symptoms = incoming_msg.split(",")
        prediction = predict_disease(symptoms)
        disease_info = fetch_disease_info(disease=prediction)
        reply = f"Based on the symptoms you have entered, I predict that you have {prediction}\n{disease_info[1]}"
        botstat=0
        msg.body(reply)
    elif botstat=="malaria":
        media_url = request.form.get('MediaUrl0')
        if media_url:
            response = requests.get(media_url)
            path = 'uploads/bot.jpg' 
            with open(path, 'wb') as temp_file:
                temp_file.write(response.content)
        result = malaria_pred(path)
        if result==0:
            result="Negative"
        else:
            result="Positive"
        reply = f"The result of the test is {result}"
        botstat=0
        msg.body(reply)
    elif botstat=="pneumonia":
        botstat=0
        media_url = request.form.get('MediaUrl0')
        if media_url:
            response = requests.get(media_url)
            path = 'uploads/bot.jpg'
            with open(path, 'wb') as temp_file:
                temp_file.write(response.content)
        prediction, confidence = predictpneumonia(path)
        if prediction == "safe":
            result_message = f"The patient is not suffering from Pneumonia with Confidence: {confidence*100:.2f}%"
        else:
            result_message = f"The patient is suffering from {prediction} with Confidence: {confidence*100:.2f}%"
        msg.body(result_message)
        
    elif botstat=="firstaid":
        tag, data=chat(incoming_msg)
        reply=f"*{tag}*\n{data}"
        botstat=0
        msg.body(reply)
    elif 'symptoms' in incoming_msg:
        botstat="symptoms"
        reply="Please enter the symptoms you are experiencing separated by commas"
        msg.body(reply)
    elif 'malaria' in incoming_msg:
        botstat="malaria"
        reply="Please send an image of the cell sample"
        msg.body(reply)
    elif 'pneumonia' in incoming_msg:
        botstat="pneumonia"
        reply="Please send an image of the chest x-ray"
        msg.body(reply)
    elif 'first aid' in incoming_msg:
        botstat="firstaid"
        reply="Please enter the problem"
        msg.body(reply)
    else:
        reply="Hi Please type 'Symptoms' to predict disease based on symptoms, 'Malaria' to predict malaria, 'Pneumonia' to predict pneumonia or 'First Aid' to get first aid information"
        msg.body(reply)
    return str(resp)

