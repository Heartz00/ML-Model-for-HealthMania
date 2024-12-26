import React from 'react';
import styled, { keyframes, createGlobalStyle } from 'styled-components';
import '@google/model-viewer';
import IconCard from './IconCard';

// Import icons
import glucoIcon from '../assets/glucoIcon.png';
import stressIcon from '../assets/stressIcon.png';
import calorieIcon from '../assets/calorieIcon.png';
import nutriIcon from '../assets/nutriIcon.png';
import dreamIcon from '../assets/dreamIcon.png';
import bumpIcon from '../assets/bumpIcon.png';

import logo from '../assets/logo.png'; // Replace this with your logo file


// Global styles
const GlobalStyle = createGlobalStyle`
  :root {
    --gradient-shadow: linear-gradient(
      45deg,
rgb(23, 68, 151),   /* Dark Blue */
      #1e3c72,
      rgba(177, 95, 13, 0.94),   /* Light Blue */
#001f3d,
rgb(16, 64, 111)
    );
  }
  body {
    margin: 0;
    padding: 0;
    background: #000; /* Dark Blue background */
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    font-family: 'Arial', sans-serif;
  }
`;

// Animations
const animate = keyframes`
  0% { background-position: 0 0; }
  50% { background-position: 300% 0; }
  100% { background-position: 0 0; }
`;

const pulse = keyframes`
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
`;

// Navigation Bar Styles
const Navbar = styled.nav`
  position: fixed;
  top: 0;
  left: 50;
  right: 0;
  width: 100%;
  background: #fff; 
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: -5px 5px;
  z-index: 1000;
`;

const Logo = styled.div`
  font-size: 1.5em;
  font-weight: bold;
  color: #001f3d; 
  
  img {
    width: 35px; /* Adjust the size as needed */
    height: 35px;
    left: 50%;
  }
`;
const NavLinks = styled.div`
  display: flex;
  gap: 20px;
`;

const NavLink = styled.a`
  color: #001f3d;
  text-decoration: none;
  font-size: 1em;
  font-weight: 20;
  &:hover {
    color: rgba(177, 95, 13, 0.94)); 
  }
`;

// Home Page Styles
const ShadowContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  color: #fff;
  text-align: center;
  width: 1900px;
  height: 500px;
  background: linear-gradient(0deg, #001f3d,rgb(0, 3, 5)); /* Blue gradient */
  
  &:before,
  &:after {
    content: "";
    position: absolute;
    top: -2px;
    left: -2px;
    background: var(--gradient-shadow);
    background-size: 400%;
    width: calc(100% + 4px);
    height: calc(100% + 4px);
    z-index: -1;
    animation: ${animate} 20s linear infinite;
  }
  
  &:after {
    filter: blur(20px);
  }
`;

const HomeContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 80%;
  height: 90%;
  padding: 0 30px;
`;

const ContentSection = styled.div`
  flex: 1;
  text-align: left;
  padding-right: 100px;
`;

const Title = styled.h1`
  font-size: 3em;
  margin-bottom: 20px;
  color: #3a7bd5; /* Light Blue */
  font-weight: bold;
`;

const Subtitle = styled.h2`
  font-size: 1.5em;
  margin-bottom: 30px;
  color: #fff;
  opacity: 0.9;
`;

const CTAButton = styled.button`
  padding: 15px 25px;
  font-size: 1.2em;
  background: linear-gradient(180deg,rgb(34, 97, 185), rgba(240, 163, 87, 0.94)); /* Blue Gradient */
  border: none;
  border-radius: 25px;
  color: white;
  cursor: pointer;
  transition: transform 0.3s ease, background 0.3s ease;
  
  &:hover {
    transform: scale(1.1);
    background: linear-gradient(45deg, #1e3c72, #3a7bd5); /* Reverse the gradient on hover */
  }
`;

const ModelSection = styled.div`
  flex: 1;
  position: relative;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const IconsContainer = styled.div`
  position: absolute;
  width: 90%;
  height: 100%;
`;

const IconPosition = styled.div`
  position: absolute;
  transition: all 0.8s ease-in-out;
  
  &:hover {
    transform: scale(1.1);
    z-index: 2;
    animation: ${pulse} 1.5s infinite;
  }
`;

// Icon Components Position
const IconLeftTop = styled(IconPosition)` left: 80; top: 80px; `;
const IconLeftMiddle = styled(IconPosition)` left: -10px; top: 50%; `;
const IconLeftBottom = styled(IconPosition)` left: 0; bottom: 20px; `;
const IconRightTop = styled(IconPosition)` right: 0; top: 80px; `;
const IconRightMiddle = styled(IconPosition)` right: -30px; top: 50%; `;
const IconRightBottom = styled(IconPosition)` right: 0; bottom: 20px; `;

const HomePage = () => {
  return (
    <>
      <GlobalStyle />
      <Navbar>
      <Logo>
          <img src={logo} alt="HealthMania Logo" />
        </Logo>
        <NavLinks>
          <NavLink href="#home">Home</NavLink>
          <NavLink href="#signup">Sign Up</NavLink>
          <NavLink href="#signin">Sign In</NavLink>
          <NavLink href="#logout">Logout</NavLink>
        </NavLinks>
      </Navbar>

      <ShadowContainer>
        <HomeContainer>
          <ContentSection>
            <Title>Empower Your Health</Title>
            <Subtitle>
              Revolutionizing health monitoring with cutting-edge AI solutions for a healthier future.
            </Subtitle>
            <CTAButton>Discover more about your Health</CTAButton>
          </ContentSection>
          
          <ModelSection>
            <model-viewer
              src="/humann.glb"
              alt="3D human model"
              auto-rotate
              rotation-per-second="70"
              style={{ width: '1000px', height: '1000px' }}
            ></model-viewer>
            
            <IconsContainer>
              <IconLeftTop>
                <IconCard 
                  title="CalorieCount" 
                  description="Smart Nutrition Tracking" 
                  icon={calorieIcon} 
                />
              </IconLeftTop>
              <IconLeftMiddle>
                <IconCard 
                  title="StressCheck" 
                  description="Real-time Stress Monitoring" 
                  icon={stressIcon}
                  
                />
              </IconLeftMiddle>
              <IconLeftBottom>
                <IconCard 
                 
                  title="GlucoSense" 
                  description="AI-Powered Diabetes Management" 
                  icon={glucoIcon} 
                />
              </IconLeftBottom>
              
              <IconRightTop>
                <IconCard 
                  title="NutriScan" 
                  description="Instant Food Analysis" 
                  icon={nutriIcon} 
                />
              </IconRightTop>
              <IconRightMiddle>
                <IconCard 
                  title="DreamGuard" 
                  description="Sleep Quality Optimization" 
                  icon={dreamIcon} 
                />
              </IconRightMiddle>
              <IconRightBottom>
                <IconCard 
                  title="BumpBalance" 
                  description="Pregnancy Wellness Guide" 
                  icon={bumpIcon} 
                />
              </IconRightBottom>
            </IconsContainer>
          </ModelSection>
        </HomeContainer>
      </ShadowContainer>
    </>
  );
};

export default HomePage;
