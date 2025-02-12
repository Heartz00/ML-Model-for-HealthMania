from fastapi import FastAPI, HTTPException
import joblib
import numpy as np
import pandas as pd
import onnxruntime as rt
from sklearn.preprocessing import RobustScaler
import pickle

app = FastAPI()

# Load models
with open("food health.pkl", 'rb') as file:
    rf_health_model = pickle.load(file)

with open("calorie level.pkl", 'rb') as file:
    rf_calorie_model = pickle.load(file)

with open("diabetes modelss.pkl", 'rb') as file:
    diabetes_model = pickle.load(file)

onx_model_path = 'multi_output_svm_model_pipeline.onnx'
onx_session = rt.InferenceSession(onx_model_path)

DIABETES_FEATURES = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
RF_FEATURES = [
    'calories', 'cal_fat', 'total_fat', 'sat_fat', 'trans_fat',
    'cholesterol', 'sodium', 'total_carb', 'fiber', 'sugar', 'protein'
]

# Load the recommendation dataframe
df = pd.read_csv('recommend_data.csv')

def recommend(caloric_level, caloric_value, n=10):
    filtered_data = df[df['caloric level'] == caloric_level]
    sorted_diets = filtered_data.sort_values(by=['Energ_Kcal'], ascending=False)
    recommended_diets = sorted_diets[
        (sorted_diets['Energ_Kcal'] >= caloric_value) & 
        (sorted_diets['Energ_Kcal'] <= caloric_value + 100)
    ]
    return recommended_diets.head(n)[['Shrt_Desc', 'Energ_Kcal']].to_dict(orient='records')

def nutrient(age, height, weight, preg_stage, active):
    activity_levels = {
        'sedentary': 1.2, 'light active': 1.375, 
        'moderately active': 1.55, 'very active': 1.75
    }
    active_factor = activity_levels.get(active.lower(), 1.2)

    bmi = weight / (height * height)
    
    if bmi < 18.5:
        if preg_stage.lower() == "firsttrimester":
            goal = 2
        elif preg_stage.lower() == "secondtrimester":
            goal = 10
        else:
            goal = 18
    elif 18.5 <= bmi <= 25:
        if preg_stage.lower() == "firsttrimester":
            goal = 2
        elif preg_stage.lower() == "secondtrimester":
            goal = 10
        else:
            goal = 16
    else:
        if preg_stage.lower() == "firsttrimester":
            goal = 2
        elif preg_stage.lower() == "secondtrimester":
            goal = 7
        else:
            goal = 11

    # Mifflin-St Jeor BMR equation
    bmr = 10 * weight + 6.25 * height - 5 * age - 161
    caloric_intake = bmr * active_factor + goal * 100

    return caloric_intake

def calorie_classify(caloric_intake):
    if caloric_intake < 300:
        return "low"
    elif 300 <= caloric_intake <= 350:
        return "mid"
    return "high"

@app.post("/recommend_diet")
def diet_recommendation(data: dict):
    try:
        age = data.get("age")
        height = data.get("height")
        weight = data.get("weight")
        preg_stage = data.get("preg_stage")
        active = data.get("active")

        if None in [age, height, weight, preg_stage, active]:
            raise HTTPException(status_code=400, detail="Missing required fields.")

        caloric_intake = nutrient(age, height, weight, preg_stage, active)
        caloric_classification = calorie_classify(caloric_intake)
        recommended_diets = recommend(caloric_classification, caloric_intake, n=5)

        return {
            "caloric_intake": caloric_intake,
            "caloric_classification": caloric_classification,
            "recommended_diets": recommended_diets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "API working successfully"}

@app.post("/predict_diabetes")
def predict_diabetes(data: dict):
    try:
        input_features = [data.get(feature) for feature in DIABETES_FEATURES]
        if None in input_features:
            missing_features = [DIABETES_FEATURES[i] for i, val in enumerate(input_features) if val is None]
            raise HTTPException(status_code=400, detail=f"Missing required features: {missing_features}")

        input_df = pd.DataFrame([input_features], columns=DIABETES_FEATURES)
        scaler = RobustScaler()
        scaled_input = scaler.fit_transform(input_df)
        
        prediction = diabetes_model.predict(scaled_input)[0]
        prediction_proba = diabetes_model.predict_proba(scaled_input)[0]

        outcome_map = {0: 'Non-Diabetic', 1: 'Diabetic'}
        result = {
            "outcome": outcome_map.get(prediction, "Unknown"),
            "probability": {
                "Non-Diabetic": prediction_proba[0],
                "Diabetic": prediction_proba[1]
            }
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_calorie_health")
def predict_rf(data: dict):
    try:
        input_features = [data.get(feature) for feature in RF_FEATURES]
        if None in input_features:
            missing_features = [RF_FEATURES[i] for i, val in enumerate(input_features) if val is None]
            raise HTTPException(status_code=400, detail=f"Missing required features: {missing_features}")

        input_array = np.array(input_features).reshape(1, -1)
        calorie_prediction = rf_calorie_model.predict(input_array)[0]
        health_prediction = rf_health_model.predict(input_array)[0]

        calorie_label = {1: 'Low', 2: 'Normal', 0: 'High'}
        health_label = {1: 'This Food seems Unhealthy', 0: 'This Food is Healthy'}

        return {
            "calorie_level": calorie_label.get(calorie_prediction, "Unknown"),
            "health_status": health_label.get(health_prediction, "Unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
