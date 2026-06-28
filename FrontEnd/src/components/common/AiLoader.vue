<template>
  <div class="action-btn btn-green micro-scanner-button-fit">
    <div class="laser-sweep"></div>
    
    <svg version="1.2" viewBox="0 0 200 40" class="micro-wave">
      <path 
        id="vascular-pulse" 
        stroke="#ffffff" 
        fill="none" 
        stroke-width="2.5" 
        stroke-linejoin="round"
        stroke-linecap="round"
        d="M0,20 L70,20 Q75,5 80,20 T85,28 T90,20 L110,20 Q115,2 120,38 T125,20 L200,20" 
      />
      <circle cx="120" cy="38" r="3.5" fill="#ffffff" class="pulse-node" />
    </svg>
    
    <i class="fa fa-spinner fa-spin visual-placeholder"></i>
    <span class="processing-text">Analyzing...</span>
  </div>
</template>

<style scoped>
.micro-scanner-button-fit {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-sizing: border-box;
  
  /* Enforces absolute structural identity matching the button */
  width: 153.5px;
  height: 37px;
  padding: 8px 16px;
  border-radius: 8px;
  
  text-align: center;
  gap: 6px;
  cursor: not-allowed;
}

.visual-placeholder {
  position: relative;
  z-index: 10;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.processing-text {
  position: relative;
  z-index: 10;
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
  letter-spacing: 0.3px;
  line-height: 1;
}

.micro-wave {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0.35; 
}

#vascular-pulse {
  stroke-dasharray: 300;
  stroke-dashoffset: 300;
  animation: microDash 1.2s infinite linear;
}

@keyframes microDash {
  from { stroke-dashoffset: 300; }
  to { stroke-dashoffset: -300; }
}

.laser-sweep {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: rgba(255, 255, 255, 0.75);
  box-shadow: 0 0 8px #ffffff;
  animation: laserSweep 1.8s infinite ease-in-out;
}

@keyframes laserSweep {
  0% { left: 0%; opacity: 0; }
  15% { opacity: 1; }
  85% { opacity: 1; }
  100% { left: 100%; opacity: 0; }
}

.pulse-node {
  animation: pulseFlash 0.6s infinite alternate;
}

@keyframes pulseFlash {
  from { opacity: 0.4; r: 2.5px; }
  to { opacity: 1; r: 4.5px; }
}
</style>