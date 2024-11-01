from flask import Flask, request, jsonify
import numpy as np
import onnxruntime as rt

app = Flask(__name__)

# Load the ONNX pipeline (scaler + model in one pipeline)
onnx_model_path = 'multi_output_svm_model_pipeline.onnx'
onnx_session = rt.InferenceSession(onnx_model_path)

# Root endpoint to confirm the API is running
@app.route('/', methods=['GET'])
def home():
    return "API working successfully", 200

# Endpoint for prediction
@app.route('/predict', methods=['POST'])
def predict():
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
    input_name = onnx_session.get_inputs()[0].name
    result = onnx_session.run(None, {input_name: input_array.astype(np.float32)})

    # Extract predictions for stress level and sleep disorder
    prediction = result[0]  # Assuming the first output is the prediction array

    # Map predictions back to meaningful labels
    stress_level = 'Low' if prediction[0][0] < 5 else 'High'
    sleep_disorder = 'No Disorder' if prediction[0][1] == 0 else 'Insomnia' if prediction[0][1] == 1 else 'Sleep Apnea'

    return jsonify({'Your Stress Level is': stress_level, 'Your Sleep Disorder is': sleep_disorder})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
