from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
import onnxruntime as rt
from sklearn.preprocessing import RobustScaler

# Initialize the Flask app
app = Flask(__name__)

# Load the trained Random Forest models
rf_health_model = joblib.load("food health.joblib")
rf_calorie_model = joblib.load("calorie level.joblib")

# Load the trained diabetes model
diabetes_model = joblib.load("diabetes model.joblib")

# Load the ONNX pipeline (scaler + model in one pipeline)
onx_model_path = 'multi_output_svm_model_pipeline.onnx'
onx_session = rt.InferenceSession(onx_model_path)

# Define the input feature order for diabetes and Random Forest models
DIABETES_FEATURES = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
RF_FEATURES = [
    'calories', 'cal_fat', 'total_fat', 'sat_fat', 'trans_fat',
    'cholesterol', 'sodium', 'total_carb', 'fiber', 'sugar', 'protein'
]

# Root endpoint to confirm the API is running
@app.route('/', methods=['GET'])
def home():
    return "API working successfully", 200

# Endpoint for diabetes prediction
@app.route('/predict_diabetes', methods=['POST'])
def predict_diabetes():
    try:
        # Get JSON input
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input, JSON data is required"}), 400

        # Extract features from the input
        input_features = [data.get(feature, None) for feature in DIABETES_FEATURES]
        if None in input_features:
            missing_features = [DIABETES_FEATURES[i] for i, val in enumerate(input_features) if val is None]
            return jsonify({"error": f"Missing required features: {missing_features}"}), 400

        # Convert input to a DataFrame for preprocessing
        input_df = pd.DataFrame([input_features], columns=DIABETES_FEATURES)

        # Scale the input data
        scaler = RobustScaler()
        scaled_input = scaler.fit_transform(input_df)  # Assuming RobustScaler was used during training

        # Make a prediction
        prediction = diabetes_model.predict(scaled_input)[0]
        prediction_proba = diabetes_model.predict_proba(scaled_input)[0]

        # Map the prediction to a readable label
        outcome_map = {0: 'Non-Diabetic', 1: 'Diabetic'}
        result = {
            "outcome": outcome_map.get(prediction, "Unknown"),
            "probability": {
                "Non-Diabetic": prediction_proba[0],
                "Diabetic": prediction_proba[1]
            }
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint for Random Forest model predictions
@app.route('/predict_rf', methods=['POST'])
def predict_rf():
    try:
        # Get JSON input
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input, JSON data is required"}), 400

        # Extract features from the input
        input_features = [data.get(feature, None) for feature in RF_FEATURES]
        if None in input_features:
            missing_features = [RF_FEATURES[i] for i, val in enumerate(input_features) if val is None]
            return jsonify({"error": f"Missing required features: {missing_features}"}), 400

        # Convert input to a NumPy array for prediction
        input_array = np.array(input_features).reshape(1, -1)

        # Make predictions using the loaded models
        calorie_prediction = rf_calorie_model.predict(input_array)[0]
        health_prediction = rf_health_model.predict(input_array)[0]

        # Map predictions back to readable labels (if encoded)
        calorie_label = {1: 'Low', 2: 'Normal', 0: 'High'}  # Example mapping
        health_label = {1: 'Unhealthy', 0: 'Healthy'}  # Example mapping

        # Return the predictions
        response = {
            "calorie_level": calorie_label.get(calorie_prediction, "Unknown"),
            "health_status": health_label.get(health_prediction, "Unknown")
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint for ONNX model predictions
@app.route('/predict_onnx', methods=['POST'])
def predict_onnx():
    input_data = request.json

    required_fields = ['gender', 'age', 'occupation', 'sleepDuration', 'qualityOfSleep', 
        'physicalActivity', 'bmiCategory', 'heartRate', 'dailySteps', 
        'systolicBP', 'diastolicBP']
    
    missing_fields = [field for field in required_fields if field not in input_data]
    if missing_fields:
        return jsonify({
            'error': 'You need to fill in the following fields',
            'missing_fields': missing_fields
        }), 400
    
    # Mappings for categorical values
    gender_map = {'Female': 0, 'Male': 1}
    occupation_map = {
        'Accountant': 1, 'Doctor': 2, 'Engineer': 3, 'Lawyer': 4, 'Manager': 5,
        'Nurse': 6, 'Salesperson': 7, 'Sales Representative': 8, 'Scientist': 9,
        'Software Engineer': 10, 'Teacher': 11
    }
    bmi_map = {'Underweight': 0, 'Normal Weight': 1, 'Normal': 1, 'Overweight': 2, 'Obese': 3}

    # Convert input data into numerical form
    input_data['gender'] = gender_map[input_data['gender']]
    input_data['occupation'] = occupation_map[input_data['occupation']]
    input_data['bmiCategory'] = bmi_map[input_data['bmiCategory']]

    # Prepare the input data as a NumPy array
    input_array = np.array([[ 
        input_data['gender'], input_data['age'], input_data['occupation'],
        input_data['sleepDuration'], input_data['qualityOfSleep'], input_data['physicalActivity'],
        input_data['bmiCategory'], input_data['heartRate'], input_data['dailySteps'],
        input_data['systolicBP'], input_data['diastolicBP']
    ]])

    # ONNX pipeline input processing
    input_name = onx_session.get_inputs()[0].name
    result = onx_session.run(None, {input_name: input_array.astype(np.float32)})

    # Extract predictions for stress level and sleep disorder
    prediction = result[0]  # Assuming the first output is the prediction array

    # Map predictions back to meaningful labels
    stress_level = 'Low' if prediction[0][0] < 5 else 'High'
    sleep_disorder = 'No Disorder' if prediction[0][1] == 0 else 'Insomnia' if prediction[0][1] == 1 else 'Sleep Apnea'

    return jsonify({'Your Stress Level is': stress_level, 'Your Sleep Disorder is': sleep_disorder})

# Endpoint for Pregnant Women Diet Recommendation
@app.route('/recommend_diet', methods=['POST'])
def recommend_diet():
    try:
        # Load recommendation data
        df = pd.read_csv('recommend_data.csv')
        
        # Helper functions
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
                "sedentary": 1.2,
                "light active": 1.375,
                "moderately active": 1.55,
                "very active": 1.75
            }
            active_multiplier = activity_levels.get(active.lower(), 1.2)
            bmi = weight / (height ** 2)
            
            weight_goals = {
                "underweight": {"firsttrimester": 2, "secondtrimester": 10, "thirdtrimester": 18},
                "healthyweight": {"firsttrimester": 2, "secondtrimester": 10, "thirdtrimester": 16},
                "overweight": {"firsttrimester": 2, "secondtrimester": 7, "thirdtrimester": 11},
            }
            bmi_category = "underweight" if bmi < 18.5 else "healthyweight" if bmi <= 25 else "overweight"
            goal = weight_goals[bmi_category][preg_stage.lower()]

            bmr = 10 * weight + 6.25 * height * 100 - 5 * age - 161
            caloric_intake = bmr * active_multiplier + goal * 100
            return caloric_intake

        def calorie_classify(caloric_intake):
            if caloric_intake < 300:
                return "low"
            elif 300 <= caloric_intake <= 350:
                return "mid"
            return "high"

        # Get user input from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input, JSON data is required"}), 400
        
        # Extract and validate user inputs
        age = data.get("age")
        height = data.get("height")
        weight = data.get("weight")
        preg_stage = data.get("preg_stage")
        active = data.get("active")

        if None in [age, height, weight, preg_stage, active]:
            return jsonify({"error": "Missing required fields"}), 400

        # Calculate caloric intake and classify
        caloric_intake = nutrient(age, height, weight, preg_stage, active)
        caloric_classification = calorie_classify(caloric_intake)

        # Generate recommendations
        recommendations = recommend(caloric_classification, caloric_intake, n=5)

        # Return the results
        response = {
            "caloric_intake": caloric_intake,
            "caloric_classification": caloric_classification,
            "diet_recommendations": recommendations
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

def handler(event, context):
    from flask import Flask
    return app(event, context)