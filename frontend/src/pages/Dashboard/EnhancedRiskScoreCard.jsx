import { motion } from "framer-motion";

export default function EnhancedRiskScoreCard({ risk }) {
  const score = risk?.score || 0;
  const level = risk?.level || "LOW";
  const explanation = risk?.explanation || "";

  const getRiskColor = (score) => {
    if (score >= 70) return "#ef4444"; // Critical - Red
    if (score >= 50) return "#f97316"; // High - Orange  
    if (score >= 30) return "#eab308"; // Medium - Yellow
    return "#22c55e"; // Low - Green
  };

  const getRiskGradient = (score) => {
    if (score >= 70) return "linear-gradient(135deg, #ef4444, #dc2626)";
    if (score >= 50) return "linear-gradient(135deg, #f97316, #ea580c)";
    if (score >= 30) return "linear-gradient(135deg, #eab308, #ca8a04)";
    return "linear-gradient(135deg, #22c55e, #16a34a)";
  };

  const getRiskIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      default: return '✅';
    }
  };

  const color = getRiskColor(score);
  const gradient = getRiskGradient(score);
  const icon = getRiskIcon(level);

  return (
    <div style={{ 
      textAlign: "center",
      position: "relative"
    }}>
      <h3 style={{ 
        marginBottom: "15px", 
        fontSize: "1.2rem",
        fontWeight: "600",
        color: "#fff"
      }}>
        {icon} Risk Assessment
      </h3>

      {/* Circular Progress */}
      <div style={{ 
        position: "relative", 
        width: "120px", 
        height: "120px", 
        margin: "0 auto 15px"
      }}>
        <svg width="120" height="120" style={{ transform: "rotate(-90deg)" }}>
          {/* Background circle */}
          <circle
            cx="60"
            cy="60"
            r="50"
            stroke="#334155"
            strokeWidth="10"
            fill="none"
          />
          {/* Progress circle */}
          <motion.circle
            cx="60"
            cy="60"
            r="50"
            stroke={color}
            strokeWidth="10"
            fill="none"
            strokeLinecap="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: score / 100 }}
            transition={{ duration: 1.5, ease: "easeInOut" }}
            style={{
              strokeDasharray: "314",
              strokeDashoffset: "314",
            }}
          />
        </svg>
        
        {/* Center text */}
        <div style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center"
        }}>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, delay: 0.5 }}
            style={{ 
              fontSize: "28px", 
              fontWeight: "bold", 
              color: color,
              lineHeight: 1
            }}
          >
            {score}
          </motion.div>
          <div style={{ 
            fontSize: "10px", 
            color: "#94a3b8",
            marginTop: "2px"
          }}>
            /100
          </div>
        </div>
      </div>

      {/* Risk Level Badge */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        style={{
          display: "inline-block",
          padding: "6px 16px",
          borderRadius: "20px",
          background: gradient,
          color: "#fff",
          fontWeight: "bold",
          fontSize: "14px",
          marginBottom: "10px",
          boxShadow: `0 4px 12px ${color}40`
        }}
      >
        {level}
      </motion.div>

      {/* Explanation */}
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        style={{ 
          fontSize: "12px", 
          color: "#94a3b8", 
          margin: "10px 0",
          lineHeight: 1.4
        }}
      >
        {explanation}
      </motion.p>

      {/* Risk Indicators */}
      <div style={{ 
        display: "flex", 
        justifyContent: "center", 
        gap: "8px",
        marginTop: "10px"
      }}>
        {[20, 40, 60, 80].map((threshold) => (
          <div
            key={threshold}
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              background: score >= threshold ? color : "#334155",
              transition: "all 0.3s ease"
            }}
          />
        ))}
      </div>
    </div>
  );
}
