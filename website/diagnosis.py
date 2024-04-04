import json
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


TRAINED_MODEL_RF = "models/randomforest_disease_pred.pkl"
DIABETES_MODEL = "models/diabetes_early_stage.pkl"
LIVER_MODEL = "models/liver.pkl"
MALARIA_MODEL = "models/malaria_detection.pt"
PNEUMONIA_MODEL = "models/pneumonia_resnet50_model.pth"

DISEASE_DATA = "data/disease.json"
PRECAUTIONS_DATA = "data/precautions.csv"

symptoms = [
    "itching",
    "skin_rash",
    "nodal_skin_eruptions",
    "continuous_sneezing",
    "shivering",
    "chills",
    "joint_pain",
    "stomach_pain",
    "acidity",
    "ulcers_on_tongue",
    "muscle_wasting",
    "vomiting",
    "burning_micturition",
    "spotting_ urination",
    "fatigue",
    "weight_gain",
    "anxiety",
    "cold_hands_and_feets",
    "mood_swings",
    "weight_loss",
    "restlessness",
    "lethargy",
    "patches_in_throat",
    "irregular_sugar_level",
    "cough",
    "high_fever",
    "sunken_eyes",
    "breathlessness",
    "sweating",
    "dehydration",
    "indigestion",
    "headache",
    "yellowish_skin",
    "dark_urine",
    "nausea",
    "loss_of_appetite",
    "pain_behind_the_eyes",
    "back_pain",
    "constipation",
    "abdominal_pain",
    "diarrhoea",
    "mild_fever",
    "yellow_urine",
    "yellowing_of_eyes",
    "acute_liver_failure",
    "fluid_overload",
    "swelling_of_stomach",
    "swelled_lymph_nodes",
    "malaise",
    "blurred_and_distorted_vision",
    "phlegm",
    "throat_irritation",
    "redness_of_eyes",
    "sinus_pressure",
    "runny_nose",
    "congestion",
    "chest_pain",
    "weakness_in_limbs",
    "fast_heart_rate",
    "pain_during_bowel_movements",
    "pain_in_anal_region",
    "bloody_stool",
    "irritation_in_anus",
    "neck_pain",
    "dizziness",
    "cramps",
    "bruising",
    "obesity",
    "swollen_legs",
    "swollen_blood_vessels",
    "puffy_face_and_eyes",
    "enlarged_thyroid",
    "brittle_nails",
    "swollen_extremeties",
    "excessive_hunger",
    "extra_marital_contacts",
    "drying_and_tingling_lips",
    "slurred_speech",
    "knee_pain",
    "hip_joint_pain",
    "muscle_weakness",
    "stiff_neck",
    "swelling_joints",
    "movement_stiffness",
    "spinning_movements",
    "loss_of_balance",
    "unsteadiness",
    "weakness_of_one_body_side",
    "loss_of_smell",
    "bladder_discomfort",
    "foul_smell_of urine",
    "continuous_feel_of_urine",
    "passage_of_gases",
    "internal_itching",
    "toxic_look_(typhos)",
    "depression",
    "irritability",
    "muscle_pain",
    "altered_sensorium",
    "red_spots_over_body",
    "belly_pain",
    "abnormal_menstruation",
    "dischromic _patches",
    "watering_from_eyes",
    "increased_appetite",
    "polyuria",
    "family_history",
    "mucoid_sputum",
    "rusty_sputum",
    "lack_of_concentration",
    "visual_disturbances",
    "receiving_blood_transfusion",
    "receiving_unsterile_injections",
    "coma",
    "stomach_bleeding",
    "distention_of_abdomen",
    "history_of_alcohol_consumption",
    "fluid_overload.1",
    "blood_in_sputum",
    "prominent_veins_on_calf",
    "palpitations",
    "painful_walking",
    "pus_filled_pimples",
    "blackheads",
    "scurring",
    "skin_peeling",
    "silver_like_dusting",
    "small_dents_in_nails",
    "inflammatory_nails",
    "blister",
    "red_sore_around_nose",
    "yellow_crust_ooze",
]

disease = [
    "Fungal infection",
    "Allergy",
    "GERD",
    "Chronic cholestasis",
    "Drug Reaction",
    "Peptic ulcer diseae",
    "AIDS",
    "Diabetes",
    "Gastroenteritis",
    "Bronchial Asthma",
    "Hypertension",
    " Migraine",
    "Cervical spondylosis",
    "Paralysis (brain hemorrhage)",
    "Jaundice",
    "Malaria",
    "Chicken pox",
    "Dengue",
    "Typhoid",
    "hepatitis A",
    "Hepatitis B",
    "Hepatitis C",
    "Hepatitis D",
    "Hepatitis E",
    "Alcoholic hepatitis",
    "Tuberculosis",
    "Common Cold",
    "Pneumonia",
    "Dimorphic hemmorhoids(piles)",
    "Heartattack",
    "Varicoseveins",
    "Hypothyroidism",
    "Hyperthyroidism",
    "Hypoglycemia",
    "Osteoarthristis",
    "Arthritis",
    "(vertigo) Paroymsal  Positional Vertigo",
    "Acne",
    "Urinary tract infection",
    "Psoriasis",
    "Impetigo",
]

disease_encode_dict = {
    "Fungal infection": 0,
    "Allergy": 1,
    "GERD": 2,
    "Chronic cholestasis": 3,
    "Drug Reaction": 4,
    "Peptic ulcer diseae": 5,
    "AIDS": 6,
    "Diabetes ": 7,
    "Gastroenteritis": 8,
    "Bronchial Asthma": 9,
    "Hypertension ": 10,
    "Migraine": 11,
    "Cervical spondylosis": 12,
    "Paralysis (brain hemorrhage)": 13,
    "Jaundice": 14,
    "Malaria": 15,
    "Chicken pox": 16,
    "Dengue": 17,
    "Typhoid": 18,
    "hepatitis A": 19,
    "Hepatitis B": 20,
    "Hepatitis C": 21,
    "Hepatitis D": 22,
    "Hepatitis E": 23,
    "Alcoholic hepatitis": 24,
    "Tuberculosis": 25,
    "Common Cold": 26,
    "Pneumonia": 27,
    "Dimorphic hemmorhoids(piles)": 28,
    "Heart attack": 29,
    "Varicose veins": 30,
    "Hypothyroidism": 31,
    "Hyperthyroidism": 32,
    "Hypoglycemia": 33,
    "Osteoarthristis": 34,
    "Arthritis": 35,
    "(vertigo) Paroymsal  Positional Vertigo": 36,
    "Acne": 37,
    "Urinary tract infection": 38,
    "Psoriasis": 39,
    "Impetigo": 40,
}

def doctor_search(doctor_type):
    base_url = "https://www.google.com/search?q="
    query = doctor_type.split(" ")
    query = "+".join(query)
    query = f"{query}+near+me"
    final_url = base_url + query

    return final_url

def get_disease(val):
    for key, value in disease_encode_dict.items():
        if val == value:
            return key


def predict_disease(inp_symptoms):
    test_lst = np.zeros(len(symptoms))
    for k in range(0, len(symptoms)):
        for s in inp_symptoms:
            if s == symptoms[k]:
                test_lst[k] = 1

    model = joblib.load(TRAINED_MODEL_RF)
    prediction = model.predict([test_lst])
    prediction = get_disease(prediction[0])
    return prediction


def split_by_pipe(value):

    value_lst = value.split("|")

    return value_lst


def med_search(medicine):
    split_med = medicine.split(" ")
    if len(split_med) > 1:
        medicine = "+".join(split_med)
        url = f"https://www.drugs.com/search.php?searchterm={medicine}"

    url = f"https://www.drugs.com/search.php?searchterm={medicine}"

    return url


def get_precautions(disease):
    prec = pd.read_csv(PRECAUTIONS_DATA)

    precautions = prec.loc[prec["Disease"] == disease].values.tolist()[0][1:]

    return precautions


def fetch_disease_info(disease=None):
    global types
    with open(DISEASE_DATA) as f:
        disease_data = json.load(f)

    common_name = disease_data[disease]["common name"]
    gen_overview = disease_data[disease]["Disease overview"][0].get("general_overview")
    frequency = disease_data[disease]["Disease overview"][1].get("frequency")
    gen_info = disease_data[disease]["Disease overview"][2].get("general_info")
    causes = disease_data[disease]["Disease overview"][2].get("cause")

    disease_type = None

    gen_info_lst = split_by_pipe(gen_info)
    symptoms = disease_data[disease]["symptoms"].replace("|", ", ")
    causes = split_by_pipe(causes)
    precautions = get_precautions(disease)
    treatment = split_by_pipe(disease_data[disease]["treatment"])
    medications = split_by_pipe(disease_data[disease]["medications"])
    specialists = split_by_pipe(disease_data[disease]["specialists"])
    more_info_link = disease_data[disease]["more info"]
    return (
        common_name,
        gen_overview,
        frequency,
        gen_info_lst,
        symptoms,
        causes,
        precautions,
        treatment,
        medications,
        specialists,
        disease_type,
        more_info_link,
    )


def predict_early_diabetes(
    age,
    status,
    polyuria,
    polydipsia,
    weight,
    weakness,
    polyphagia,
    genital_thrush,
    visual_blurring,
    itching,
    irritability,
    delayed_healing,
    partial_paresis,
    muscle_stiffness,
    alopecia,
    obesity,
):
    model = joblib.load(DIABETES_MODEL)
    prediction = model.predict(
        np.array(
            [
                [
                    int(age),
                    int(status),
                    int(polyuria),
                    int(polydipsia),
                    int(weight),
                    int(weakness),
                    int(polyphagia),
                    int(genital_thrush),
                    int(visual_blurring),
                    int(itching),
                    int(irritability),
                    int(delayed_healing),
                    int(partial_paresis),
                    int(muscle_stiffness),
                    int(alopecia),
                    int(obesity),
                ]
            ]
        )
    )
    return prediction
    

def predict_liver_disease(age, gender, total_bilirubin, direct_bilirubin, alk_phosphate,
                            alamine_aminotransferase, aspartate_aminotransferase, total_proteins,
                            albumin, ratio):
    model = joblib.load(LIVER_MODEL)
    inp_array = np.array(
        [
            [
                int(age),
                int(gender),
                float(total_bilirubin),
                float(direct_bilirubin),
                int(alk_phosphate),
                int(alamine_aminotransferase),
                int(aspartate_aminotransferase),
                float(total_proteins),
                float(albumin),
                float(ratio),
            ]
        ]
    )
    liver_disease_prob = model.predict(inp_array)
    return liver_disease_prob


class mosqutest(nn.Module):
    def __init__(self):
        super(mosqutest, self).__init__()

        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, stride=1, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.layer3 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.fc1 = nn.Linear(64 * 15 * 15, 512)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, 2)
        self.drop = nn.Dropout2d(0.2)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = self.layer3(out)
        out = out.view(out.size(0), -1)
        out = self.fc1(out)
        out = F.relu(out)
        out = self.drop(out)
        out = self.fc2(out)
        out = F.relu(out)
        out = self.drop(out)
        out = self.fc3(out)

        return out

def malaria_pred(uploaded_image):
    malaria_model = mosqutest()
    malaria_model.load_state_dict(
        torch.load(MALARIA_MODEL, map_location=torch.device("cpu"))
    )

    malaria_model.eval()

    if uploaded_image:
        image = Image.open(uploaded_image).convert("RGB")

        prediction_transform = transforms.Compose(
            [
                transforms.Resize((120, 120)),
                transforms.ToTensor(),
                transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
            ]
        )

        image = prediction_transform(image).unsqueeze(0)

        output = malaria_model(image)
        predicted = torch.max(output, 1)[1]
        return predicted.item()
    


def preprocess_image(image):
    transform = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.Grayscale(num_output_channels=1),
            transforms.ToTensor(),
        ]
    )
    image = Image.open(image)
    image = transform(image).float()
    return image


class PneumoniaModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.network = torchvision.models.resnet50(pretrained=False)
        self.network.conv1 = nn.Conv2d(
            1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False
        )
        for param in self.network.fc.parameters():
            param.require_grad = False

        num_features = (
            self.network.fc.in_features
        ) 
        self.network.fc = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 3),
        )

    def forward(self, x):
        return self.network(x)

model = PneumoniaModel()
model.load_state_dict(torch.load(PNEUMONIA_MODEL, map_location="cpu"))
model.eval()

def predictpneumonia(image):
    with torch.no_grad():

        image = preprocess_image(image)
        image = image.unsqueeze(0)
        output = model(image)
        softmax = nn.Softmax(dim=1)
        output = softmax(output)
        pred = torch.argmax(output)
        confidence = torch.max(output).numpy()
        print(confidence * 100)
    if pred==0:
        return "safe", confidence
    elif pred==1:
        return "bacterial pneumonia", confidence
    elif pred==2:
        return "viral pneumonia", confidence
    return pred, confidence
