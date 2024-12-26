import React from "react";
import { useGLTF } from "@react-three/drei";

const HumanModel = () => {
  const { scene } = useGLTF("../assets/humann.glb"); // Update with your 3D model path
  return <primitive object={scene} scale={2.5} />;
};

export default HumanModel;
