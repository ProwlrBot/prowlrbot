import { useState, useEffect, useCallback } from "react";
import { Steps, Button, Tag, Modal, message } from "antd";
import {
  CheckCircleOutlined,
  MinusCircleOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { request } from "../../../api";
import styles from "./index.module.less";

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  status: "completed" | "skipped" | "pending";
  completed_at?: string;
}

interface OnboardingProgress {
  user_id: string;
  steps: OnboardingStep[];
  completed_count: number;
  total_steps: number;
  started_at?: string;
  completed_at?: string;
}

/* ------------------------------------------------------------------ */
/* Default Steps (shown when API is not yet available)                  */
/* ------------------------------------------------------------------ */

const defaultSteps: OnboardingStep[] = [
  {
    id: "welcome",
    title: "Welcome",
    description: "Introduction to ProwlrBot and its capabilities",
    status: "pending",
  },
  {
    id: "provider_setup",
    title: "Configure AI Provider",
    description:
      "Set up your preferred LLM provider (OpenAI, Anthropic, Groq, etc.)",
    status: "pending",
  },
  {
    id: "agent_personality",
    title: "Agent Personality",
    description:
      "Customize your agent's name, avatar, soul, and communication style",
    status: "pending",
  },
  {
    id: "first_chat",
    title: "First Conversation",
    description: "Have your first chat with ProwlrBot to test the setup",
    status: "pending",
  },
  {
    id: "channel_setup",
    title: "Connect a Channel",
    description:
      "Connect a messaging channel (Discord, Telegram, DingTalk, etc.)",
    status: "pending",
  },
  {
    id: "skills_tour",
    title: "Explore Skills",
    description:
      "Browse and activate built-in skills like PDF, DOCX, browser, and more",
    status: "pending",
  },
  {
    id: "mcp_setup",
    title: "MCP Clients",
    description:
      "Optionally configure Model Context Protocol clients for extended capabilities",
    status: "pending",
  },
  {
    id: "monitoring",
    title: "Set Up Monitoring",
    description:
      "Configure cron jobs, heartbeat checks, or web monitoring tasks",
    status: "pending",
  },
];

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

function stepStatusIcon(status: string) {
  switch (status) {
    case "completed":
      return <CheckCircleOutlined style={{ color: "#52c41a" }} />;
    case "skipped":
      return <MinusCircleOutlined style={{ color: "#faad14" }} />;
    default:
      return <ClockCircleOutlined style={{ color: "#d9d9d9" }} />;
  }
}

function stepAntdStatus(
  status: string,
): "finish" | "process" | "wait" | "error" {
  switch (status) {
    case "completed":
      return "finish";
    case "skipped":
      return "wait";
    default:
      return "wait";
  }
}

/* ------------------------------------------------------------------ */
/* Main Page                                                           */
/* ------------------------------------------------------------------ */

function OnboardingPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<OnboardingStep[]>(defaultSteps);
  const [completedCount, setCompletedCount] = useState(0);
  const [totalSteps, setTotalSteps] = useState(defaultSteps.length);

  const fetchProgress = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await request<OnboardingProgress>(
        "/onboarding/progress/default",
      ).catch(() => null);
      if (data && Array.isArray(data.steps)) {
        setSteps(data.steps);
        setCompletedCount(data.completed_count);
        setTotalSteps(data.total_steps);
      } else {
        // Use defaults if endpoint not available
        setSteps(defaultSteps);
        setCompletedCount(0);
        setTotalSteps(defaultSteps.length);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load onboarding progress",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProgress();
  }, [fetchProgress]);

  /* ---- Reset Onboarding ---- */

  const handleReset = () => {
    Modal.confirm({
      title: "Reset Onboarding",
      content:
        "This will reset all onboarding progress and allow you to replay the setup wizard from the beginning.",
      okText: "Reset",
      cancelText: "Cancel",
      onOk: async () => {
        try {
          await request("/onboarding/progress/default/reset", {
            method: "POST",
          });
          message.success("Onboarding progress reset");
          fetchProgress();
        } catch {
          message.error(
            "Reset failed — the endpoint may not be available yet",
          );
        }
      },
    });
  };

  const skippedCount = steps.filter((s) => s.status === "skipped").length;
  const pendingCount = totalSteps - completedCount - skippedCount;

  /* ---- render ---- */

  return (
    <div className={styles.page}>
      {/* ---- Page header ---- */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Onboarding</h2>
        <p className={styles.sectionDesc}>
          Track your setup progress and replay the onboarding wizard.
        </p>
      </div>

      {loading ? (
        <div className={styles.centerState}>
          <span className={styles.stateText}>
            Loading onboarding progress...
          </span>
        </div>
      ) : error ? (
        <div className={styles.centerState}>
          <span className={styles.stateTextError}>{error}</span>
          <Button
            size="small"
            onClick={fetchProgress}
            style={{ marginTop: 12 }}
          >
            Retry
          </Button>
        </div>
      ) : (
        <>
          {/* ---- Progress Summary ---- */}
          <div className={styles.cardSection}>
            <div className={styles.cardSectionTitle}>Progress</div>
            <div className={styles.progressSummary}>
              <div className={styles.progressStat}>
                <span className={styles.progressNumber}>{completedCount}</span>
                <span className={styles.progressLabel}>Completed</span>
              </div>
              <div className={styles.progressStat}>
                <span className={styles.progressNumber}>{skippedCount}</span>
                <span className={styles.progressLabel}>Skipped</span>
              </div>
              <div className={styles.progressStat}>
                <span className={styles.progressNumber}>{pendingCount}</span>
                <span className={styles.progressLabel}>Pending</span>
              </div>
              <div className={styles.progressStat}>
                <span className={styles.progressNumber}>{totalSteps}</span>
                <span className={styles.progressLabel}>Total</span>
              </div>
            </div>
          </div>

          {/* ---- Steps ---- */}
          <div className={styles.cardSection}>
            <div className={styles.cardSectionTitle}>Setup Steps</div>
            <div className={styles.stepsContainer}>
              <Steps
                direction="vertical"
                current={-1}
                items={steps.map((step) => ({
                  title: (
                    <span>
                      {step.title}{" "}
                      {step.status === "completed" && (
                        <Tag color="success" style={{ marginLeft: 8 }}>
                          Completed
                        </Tag>
                      )}
                      {step.status === "skipped" && (
                        <Tag color="warning" style={{ marginLeft: 8 }}>
                          Skipped
                        </Tag>
                      )}
                    </span>
                  ),
                  description: (
                    <span>
                      {step.description}
                      {step.completed_at && (
                        <span
                          style={{
                            color: "#999",
                            fontSize: 12,
                            marginLeft: 8,
                          }}
                        >
                          ({new Date(step.completed_at).toLocaleDateString()})
                        </span>
                      )}
                    </span>
                  ),
                  status: stepAntdStatus(step.status),
                  icon: stepStatusIcon(step.status),
                }))}
              />
            </div>

            {/* ---- Actions ---- */}
            <div className={styles.resetActions}>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
              >
                Reset Onboarding
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default OnboardingPage;
