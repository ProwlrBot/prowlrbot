import React from "react";

const GRADE_COLORS: Record<string, { bg: string; text: string }> = {
  S: { bg: "#00C853", text: "#fff" },
  A: { bg: "#69F0AE", text: "#000" },
  B: { bg: "#FFD740", text: "#000" },
  C: { bg: "#FF9100", text: "#fff" },
  D: { bg: "#FF5252", text: "#fff" },
  F: { bg: "#424242", text: "#aaa" },
};

export const GradeBadge: React.FC<{ grade: string }> = ({ grade }) => {
  const colors = GRADE_COLORS[grade] ?? GRADE_COLORS.F;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        width: 32,
        height: 32,
        borderRadius: 4,
        fontWeight: 700,
        fontSize: 16,
        backgroundColor: colors.bg,
        color: colors.text,
        flexShrink: 0,
      }}
    >
      {grade}
    </span>
  );
};
