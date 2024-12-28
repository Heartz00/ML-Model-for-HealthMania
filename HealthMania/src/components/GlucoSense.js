import React, { useState } from "react";
import styled, { keyframes } from "styled-components";
import diabetes from "../assets/diabetes-cartoon.png";

const GlucoSensePage = () => {
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState({
    Pregnancies: "",
    Glucose: "",
    BloodPressure: "",
    SkinThickness: "",
    Insulin: "",
    BMI: "",
    DiabetesPedigreeFunction: "",
    Age: "",
  });
  const [result, setResult] = useState(null);

  const questions = [
    { key: "Pregnancies", label: "How many times have you been pregnant?" },
    { key: "Glucose", label: "What is your Glucose level?" },
    { key: "BloodPressure", label: "What is your Blood Pressure level?" },
    { key: "SkinThickness", label: "What is your Skin Thickness?" },
    { key: "Insulin", label: "What is your Insulin level?" },
    { key: "BMI", label: "What is your Body Mass Index (BMI)?" },
    {
      key: "DiabetesPedigreeFunction",
      label: "What is your Diabetes Pedigree Function?",
    },
    { key: "Age", label: "What is your Age?" },
  ];

  const handleNext = () => {
    if (step < questions.length - 1) setStep(step + 1);
    else calculateResult();
  };

  const handleChange = (key, value) => {
    setFormData({ ...formData, [key]: value });
  };

  const calculateResult = () => {
    const prediction = Math.random() > 0.5 ? 1 : 0; // Simulate prediction.
    const predictionProba = [0.3, 0.7]; // Example probabilities.
    const outcomeMap = { 0: "Non-Diabetic", 1: "Diabetic" };

    setResult({
      status: outcomeMap[prediction],
      probability: `Non-Diabetic: ${predictionProba[0]}, Diabetic: ${predictionProba[1]}`,
      message:
        prediction === 1
          ? "You may be at risk of diabetes. Please consult a healthcare provider for a detailed assessment."
          : "Your results are normal, but maintaining a healthy lifestyle is crucial.",
    });
  };

  return (
    <PageContainer>
      {step === 0 && !result ? (
        <MainSection>
          <LeftCard>
            <Title>Welcome to GlucoSense</Title>
            <Description>
              Take control of your health. Answer a few questions to assess your
              risk of diabetes.
            </Description>
            <StartButton onClick={() => setStep(1)}>Get Started</StartButton>
          </LeftCard>
          <RightImage src={diabetes} alt="Diabetes Awareness" />
        </MainSection>
      ) : !result ? (
        <FloatingCard>
          <Question>{questions[step - 1].label}</Question>
          <InputField
            type="number"
            value={formData[questions[step - 1].key]}
            onChange={(e) =>
              handleChange(questions[step - 1].key, e.target.value)
            }
            placeholder="Enter value here..."
          />
          <NextButton onClick={handleNext}>
            {step === questions.length ? "Submit" : "Next"}
          </NextButton>
        </FloatingCard>
      ) : (
        <ResultCard>
          <ResultTitle>{result.status}</ResultTitle>
          <ResultProbability>{result.probability}</ResultProbability>
          <ResultMessage>{result.message}</ResultMessage>
          <BackButton onClick={() => window.location.reload()}>
            Start Over
          </BackButton>
        </ResultCard>
      )}
    </PageContainer>
  );
};

export default GlucoSensePage;

// Animations
const fadeIn = keyframes`
  0% { opacity: 0; transform: translateY(-10px); }
  100% { opacity: 1; transform: translateY(0); }
`;

const jumpIn = keyframes`
  0% { transform: scale(0.8); opacity: 0; }
  50% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); }
`;

const glow = keyframes`
  0% { box-shadow: 0 0 15px rgba(0, 72, 255, 0.5); }
  50% { box-shadow: 0 0 25px rgba(0, 255, 255, 1); }
  100% { box-shadow: 0 0 15px rgba(0, 255, 255, 0.5); }
`;

const pulse = keyframes`
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
`;

// Styled Components
const PageContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: linear-gradient(0deg, #001f3d,rgb(0, 3, 5)); /* Blue gradient */
  font-family: "Roboto", sans-serif;
  padding: 20px;
`;

const MainSection = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1200px;
`;

const LeftCard = styled.div`
  text-align: left;
  color: white;
  max-width: 500px;
  animation: ${fadeIn} 1.2s ease-in-out;
`;

const Title = styled.h1`
  font-size: 2.8em;
  font-weight: 600;
  margin-bottom: 15px;
`;

const Description = styled.p`
  font-size: 1.2em;
  margin-bottom: 25px;
  font-weight: 300;
`;

const StartButton = styled.button`
  padding: 15px 30px;
  background: linear-gradient(180deg,rgb(34, 97, 185), rgb(108, 154, 213)); /* Blue Gradient */
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 1.3em;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
  }
`;

const RightImage = styled.img`
  width: 50%;
  max-width: 500px;
  height: auto;
  animation: ${fadeIn} 1.5s ease-in-out;
`;

const FloatingCard = styled.div`
  background: rgba(255, 255, 255, 0.9);
  padding: 40px;
  border-radius: 12px;
  width: 100%;
  max-width: 450px;
  text-align: center;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
  animation: ${fadeIn} 1.2s ease-in-out;
`;

const Question = styled.h2`
  font-size: 1.8em;
  margin-bottom: 25px;
  color:rgb(3, 22, 42);
`;

const InputField = styled.input`
  width: 80%;
  padding: 15px;
  margin-bottom: 30px;
  border: 2px solid rgb(3, 22, 42);
  border-radius: 8px;
  font-size: 1.1em;
  outline: none;
  transition: border-color 0.3s ease;

  &:focus {
    border-color: #1a2a6c;
    box-shadow: 0 0 10px rgb(3, 22, 42);
  }
`;

const NextButton = styled.button`
  padding: 15px 25px;
  position: relative;
  background: linear-gradient(180deg,rgb(34, 97, 185), rgb(108, 154, 213)); /* Blue Gradient */
  color: white;
  border: none;
  border-radius: 30px;
  font-size: 1.2em;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  
  &:hover {
    transform: scale(1.05);
  }
`;
const ResultCard = styled.div`
  background: rgba(255, 255, 255, 0.95);
  padding: 50px;
  border-radius: 25px;
  width: 50%;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  animation: ${jumpIn} 1s ease-in-out;
`;

const ResultTitle = styled.h1`
  font-size: 2.5em;
  font-weight: bold;
  margin-bottom: 10px;
  color: ${(props) => (props.children === "Diabetic" ? "#d32f2f" : "#388e3c")};
`;

const ResultProbability = styled.p`
  font-size: 1em;
  color: #555;
  margin-bottom: 15px;
`;

const ResultMessage = styled.p`
  font-size: 1.2em;
  color: #333;
  margin-bottom: 30px;
`;

const BackButton = styled.button`
  padding: 15px 30px;
  background: linear-gradient(180deg,rgb(34, 97, 185), rgb(108, 154, 213)); /* Blue Gradient */
  color: white;
  border: none;
  border-radius: 50px;
  font-size: 1.2em;
  cursor: pointer;

  &:hover {
    
  }
`;
