from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
import onnxruntime as rt
from sklearn.preprocessing import RobustScaler
import pickle

# Initialize the Flask app
app = Flask(__name__)

# Load the models from pickle files
with open("food health.pkl", 'rb') as file:
    rf_health_model = pickle.load(file)

with open("calorie level.pkl", 'rb') as file:
    rf_calorie_model = pickle.load(file)

with open("diabetes modelss.pkl", 'rb') as file:
    diabetes_model = pickle.load(file)

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
@app.route('/predict_calorie_health', methods=['POST'])
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
        health_label = {1: 'This Food seems Unhealthy', 0: 'This Food is Healthy'}  # Example mapping

        # Return the predictions
        response = {
            "calorie_level": calorie_label.get(calorie_prediction, "Unknown"),
            "health_status": health_label.get(health_prediction, "Unknown")
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint for ONNX model predictions
@app.route('/predict_sleep_stress', methods=['POST'])
def predict_onnx():
    try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

