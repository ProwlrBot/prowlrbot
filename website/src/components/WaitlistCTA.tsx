import { motion } from "motion/react";
import { Check } from "lucide-react";
import { EarlyAccessForm } from "./EarlyAccessForm";

interface WaitlistCTAProps {
  webhookUrl?: string;
}

const trustSignals = [
  "No credit card required",
  "Free during beta",
  "Cancel anytime",
];

export function WaitlistCTA({ webhookUrl }: WaitlistCTAProps) {
  return (
    <section
      className="waitlist-cta-section"
      style={{
        position: "relative",
        overflow: "hidden",
        padding: "var(--space-7) var(--space-4)",
      }}
    >
      {/* Gradient background */}
      <div
        aria-hidden
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse 80% 50% at 50% 50%, rgba(0,229,255,0.06) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      {/* Top border glow */}
      <div
        aria-hidden
        style={{
          position: "absolute",
          top: 0,
          left: "10%",
          right: "10%",
          height: 1,
          background:
            "linear-gradient(90deg, transparent, var(--accent), transparent)",
          opacity: 0.3,
        }}
      />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.6 }}
        style={{
          position: "relative",
          maxWidth: "36rem",
          margin: "0 auto",
          textAlign: "center",
        }}
      >
        <h2
          style={{
            margin: "0 0 var(--space-2)",
            fontSize: "clamp(1.75rem, 4vw, 2.5rem)",
            fontWeight: 800,
            lineHeight: 1.1,
            letterSpacing: "-0.03em",
            color: "var(--text)",
          }}
        >
          Stop watching.{" "}
          <span style={{ color: "var(--accent)" }}>Start building.</span>
        </h2>

        <p
          style={{
            margin: "0 0 var(--space-4)",
            fontSize: "1rem",
            color: "var(--text-muted)",
            lineHeight: 1.6,
            maxWidth: "28rem",
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          Join the next wave of autonomous AI. Free during beta — limited spots
          available.
        </p>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            marginBottom: "var(--space-4)",
          }}
        >
          <EarlyAccessForm variant="section" webhookUrl={webhookUrl} />
        </div>

        {/* Trust signals */}
        <div
          className="waitlist-trust-signals"
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "var(--space-3)",
            flexWrap: "wrap",
          }}
        >
          {trustSignals.map((signal) => (
            <div
              key={signal}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.375rem",
                fontSize: "0.8125rem",
                color: "var(--text-muted)",
              }}
            >
              <Check
                size={14}
                strokeWidth={2.5}
                style={{ color: "var(--accent)", flexShrink: 0 }}
              />
              {signal}
            </div>
          ))}
        </div>
      </motion.div>

      <style>{`
        @media (max-width: 480px) {
          .waitlist-trust-signals {
            flex-direction: column !important;
            align-items: center !important;
            gap: var(--space-1) !important;
          }
        }
      `}</style>
    </section>
  );
}
