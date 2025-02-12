from fastapi import FastAPI, HTTPException
from mangum import Mangum  # Required for Vercel
import os
import pickle
import asyncio
import numpy as np
import pandas as pd
import onnxruntime as rt
from sklearn.preprocessing import RobustScaler

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load models synchronously (since pickle loading is blocking)
def load_pickle_model(file_name):
    with open(os.path.join(BASE_DIR, file_name), "rb") as file:
        return pickle.load(file)

# Asynchronous wrapper for model loading
async def load_models():
    global rf_health_model, rf_calorie_model, diabetes_model, onx_session

    loop = asyncio.get_event_loop()
    rf_health_model = await loop.run_in_executor(None, load_pickle_model, "food health.pkl")
    rf_calorie_model = await loop.run_in_executor(None, load_pickle_model, "calorie level.pkl")
    diabetes_model = await loop.run_in_executor(None, load_pickle_model, "diabetes modelss.pkl")

    # Load ONNX Model
    onx_model_path = os.path.join(BASE_DIR, 'multi_output_svm_model_pipeline.onnx')
    onx_session = rt.InferenceSession(onx_model_path)

# Load models at startup
@app.on_event("startup")
async def startup_event():
    await load_models()

# Load recommendation dataset asynchronously
async def load_recommendation_data():
    global df
    df = pd.read_csv(os.path.join(BASE_DIR, "recommend_data.csv"))

@app.on_event("startup")
async def load_data():
    await load_recommendation_data()

DIABETES_FEATURES = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
RF_FEATURES = ['calories', 'cal_fat', 'total_fat', 'sat_fat', 'trans_fat', 'cholesterol', 'sodium', 'total_carb', 'fiber', 'sugar', 'protein']

# Functions for recommendation and nutrient calculation
async def recommend(caloric_level, caloric_value, n=10):
    filtered_data = df[df['caloric level'] == caloric_level]
    sorted_diets = filtered_data.sort_values(by=['Energ_Kcal'], ascending=False)
    recommended_diets = sorted_diets[
        (sorted_diets['Energ_Kcal'] >= caloric_value) & 
        (sorted_diets['Energ_Kcal'] <= caloric_value + 100)
    ]
    return recommended_diets.head(n)[['Shrt_Desc', 'Energ_Kcal']].to_dict(orient='records')

async def nutrient(age, height, weight, preg_stage, active):
    activity_levels = {
        'sedentary': 1.2, 'light active': 1.375, 
        'moderately active': 1.55, 'very active': 1.75
    }
    active_factor = activity_levels.get(active.lower(), 1.2)

    bmi = weight / (height * height)
    
    if bmi < 18.5:
        goal = 2 if preg_stage.lower() == "firsttrimester" else 10 if preg_stage.lower() == "secondtrimester" else 18
    elif 18.5 <= bmi <= 25:
        goal = 2 if preg_stage.lower() == "firsttrimester" else 10 if preg_stage.lower() == "secondtrimester" else 16
    else:
        goal = 2 if preg_stage.lower() == "firsttrimester" else 7 if preg_stage.lower() == "secondtrimester" else 11

    # Mifflin-St Jeor BMR equation
    bmr = 10 * weight + 6.25 * height - 5 * age - 161
    caloric_intake = bmr * active_factor + goal * 100

    return caloric_intake

def calorie_classify(caloric_intake):
    return "low" if caloric_intake < 300 else "mid" if 300 <= caloric_intake <= 350 else "high"

@app.get("/")
async def root():
    return {"message": "Hello from FastAPI on Vercel!"}

@app.post("/recommend_diet")
async def diet_recommendation(data: dict):
    try:
        age = data.get("age")
        height = data.get("height")
        weight = data.get("weight")
        preg_stage = data.get("preg_stage")
        active = data.get("active")

        if None in [age, height, weight, preg_stage, active]:
            raise HTTPException(status_code=400, detail="Missing required fields.")

        caloric_intake = await nutrient(age, height, weight, preg_stage, active)
        caloric_classification = calorie_classify(caloric_intake)
        recommended_diets = await recommend(caloric_classification, caloric_intake, n=5)

        return {
            "caloric_intake": caloric_intake,
            "caloric_classification": caloric_classification,
            "recommended_diets": recommended_diets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_diabetes")
async def predict_diabetes(data: dict):
    try:
        input_features = [data.get(feature) for feature in DIABETES_FEATURES]
        if None in input_features:
            missing_features = [DIABETES_FEATURES[i] for i, val in enumerate(input_features) if val is None]
            raise HTTPException(status_code=400, detail=f"Missing required features: {missing_features}")

        input_df = pd.DataFrame([input_features], columns=DIABETES_FEATURES)
        scaler = RobustScaler()
        scaled_input = scaler.fit_transform(input_df)
        
        loop = asyncio.get_event_loop()
        prediction = await loop.run_in_executor(None, diabetes_model.predict, scaled_input)
        prediction_proba = await loop.run_in_executor(None, diabetes_model.predict_proba, scaled_input)

        outcome_map = {0: 'Non-Diabetic', 1: 'Diabetic'}
        result = {
            "outcome": outcome_map.get(prediction[0], "Unknown"),
            "probability": {
                "Non-Diabetic": prediction_proba[0][0],
                "Diabetic": prediction_proba[0][1]
            }
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_calorie_health")
async def predict_rf(data: dict):
    try:
        input_features = [data.get(feature) for feature in RF_FEATURES]
        if None in input_features:
            missing_features = [RF_FEATURES[i] for i, val in enumerate(input_features) if val is None]
            raise HTTPException(status_code=400, detail=f"Missing required features: {missing_features}")

        input_array = np.array(input_features).reshape(1, -1)
        
        loop = asyncio.get_event_loop()
        calorie_prediction = await loop.run_in_executor(None, rf_calorie_model.predict, input_array)
        health_prediction = await loop.run_in_executor(None, rf_health_model.predict, input_array)

        calorie_label = {1: 'Low', 2: 'Normal', 0: 'High'}
        health_label = {1: 'This Food seems Unhealthy', 0: 'This Food is Healthy'}

        return {
            "calorie_level": calorie_label.get(calorie_prediction[0], "Unknown"),
            "health_status": health_label.get(health_prediction[0], "Unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Required for Vercel
handler = Mangum(app)
