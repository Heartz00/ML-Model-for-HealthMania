from flask import Flask, request, jsonify
import numpy as np
import onnxruntime as rt
import logging

app = Flask(__name__)

# Initialize logging for data and predictions
logging.basicConfig(filename='health_app.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Load the ONNX model
onnx_model_path = 'multi_output_svm_model_pipeline.onnx'
onnx_session = rt.InferenceSession(onnx_model_path)

# Define mappings for categorical values
GENDER_MAP = {'Female': 0, 'Male': 1}
OCCUPATION_MAP = {
    'Accountant': 1, 'Doctor': 2, 'Engineer': 3, 'Lawyer': 4, 'Manager': 5,
    'Nurse': 6, 'Salesperson': 7, 'Sales Representative': 8, 'Scientist': 9,
    'Software Engineer': 10, 'Teacher': 11
}
BMI_MAP = {'Underweight': 0, 'Normal Weight': 1, 'Normal': 1, 'Overweight': 2, 'Obese': 3}

# Define the expected fields
REQUIRED_FIELDS = [
    'gender', 'age', 'occupation', 'sleepDuration', 'qualityOfSleep', 
    'physicalActivity', 'bmiCategory', 'heartRate', 'dailySteps', 
    'systolicBP', 'diastolicBP'
]

# Root endpoint to confirm the API is running
@app.route('/', methods=['GET'])
def home():
    return "Health Prediction API is running successfully", 200

# Helper function to validate and prepare input data
def prepare_input_data(input_data):
    missing_fields = [field for field in REQUIRED_FIELDS if field not in input_data]
    if missing_fields:
        return None, {
            'error': 'Missing required fields.',
            'missing_fields': missing_fields
        }
    
    try:
        input_data['gender'] = GENDER_MAP[input_data['gender']]
        input_data['occupation'] = OCCUPATION_MAP[input_data['occupation']]
        input_data['bmiCategory'] = BMI_MAP[input_data['bmiCategory']]
        
        input_array = np.array([[ 
            input_data['gender'], input_data['age'], input_data['occupation'],
            input_data['sleepDuration'], input_data['qualityOfSleep'], input_data['physicalActivity'],
            input_data['bmiCategory'], input_data['heartRate'], input_data['dailySteps'],
            input_data['systolicBP'], input_data['diastolicBP']
        ]], dtype=np.float32)
        
        return input_array, None
    except KeyError as e:
        return None, {'error': f"Invalid input for field: {e.args[0]}"}

# Endpoint for prediction
@app.route('/predict', methods=['POST'])
def predict():
    input_data = request.json
    input_array, error = prepare_input_data(input_data)
    
    if error:
        return jsonify(error), 400

    # Make prediction with ONNX model
    input_name = onnx_session.get_inputs()[0].name
    result = onnx_session.run(None, {input_name: input_array})

    # Extract predictions for stress level and sleep disorder
    prediction = result[0]  # Assuming first output is the prediction array
    stress_level = 'Low' if prediction[0][0] < 5 else 'High'
    sleep_disorder = 'No Disorder' if prediction[0][1] == 0 else 'Insomnia' if prediction[0][1] == 1 else 'Sleep Apnea'

    # Log the prediction data
    logging.info(f"Input: {input_data}, Prediction: {{'stress_level': stress_level, 'sleep_disorder': sleep_disorder}}")

    return jsonify({
        'stress_level': stress_level,
        'sleep_disorder': sleep_disorder,
        'recommendations': generate_recommendations(stress_level, sleep_disorder)
    })

# Generate personalized recommendations based on predictions
def generate_recommendations(stress_level, sleep_disorder):
    recommendations = []
    if stress_level == 'High':
        recommendations.append("Consider daily relaxation exercises or meditation.")
        recommendations.append("Monitor physical activity and get adequate sleep.")
    else:
        recommendations.append("Maintain regular exercise and sleep routines.")

    if sleep_disorder == 'Insomnia':
        recommendations.append("Avoid caffeine in the evening and create a sleep-friendly environment.")
    elif sleep_disorder == 'Sleep Apnea':
        recommendations.append("Consider consulting a healthcare provider about sleep studies or CPAP therapy.")

    return recommendations

# Endpoint for health insights and analytics
@app.route('/health-insights', methods=['POST'])
def health_insights():
    input_data = request.json
    input_array, error = prepare_input_data(input_data)
    
    if error:
        return jsonify(error), 400

    # Provide insights based on individual health metrics
    insights = []
    if input_data['bmiCategory'] == BMI_MAP['Overweight'] or input_data['bmiCategory'] == BMI_MAP['Obese']:
        insights.append("Consider adopting a balanced diet and increasing physical activity.")
    if input_data['heartRate'] > 100:
        insights.append("Your heart rate is above average; consider consulting a physician.")
    if input_data['systolicBP'] > 120 or input_data['diastolicBP'] > 80:
        insights.append("Your blood pressure is elevated; monitor regularly and consult a healthcare provider if persistent.")
    
    # Log insights
    logging.info(f"Input: {input_data}, Insights: {insights}")
    
    return jsonify({'insights': insights})

# Endpoint for data logging and feedback (for analytics or improving model performance)
@app.route('/log-data', methods=['POST'])
def log_data():
    input_data = request.json
    logging.info(f"User Data Log: {input_data}")
    return jsonify({'message': 'Data logged successfully'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
