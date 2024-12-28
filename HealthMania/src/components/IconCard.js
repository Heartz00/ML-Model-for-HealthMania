import React from "react";
import styled from "styled-components";

const IconCard = ({ title, description, icon }) => {
  return (
    <Card>
      <Icon src={icon} alt={title} />
      <TextContainer>
        <Title>{title}</Title>
        <Description>{description}</Description>
      </TextContainer>
    </Card>
  );
};

export default IconCard;

// Styled Components
const Card = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 10px 20px;
  background: #f8f9fa; /* Light background */
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2);
  }
`;

const Icon = styled.img`
  width: 45px;
  height: 45px;
`;

const TextContainer = styled.div`
  display: flex;
  flex-direction: column;
`;

const Title = styled.h3`
  margin: 0;
  color: #001f3d; /* Deep blue */
  font-size: 1.2rem;
`;

const Description = styled.p`
  margin: 0;
  color:rgb(46, 48, 49); /* Gray for text */
  font-size: 0.9rem;
`;
