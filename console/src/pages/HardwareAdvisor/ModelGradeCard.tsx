import React from "react";
import { Button, Tag, Tooltip } from "antd";
import { GradeBadge } from "./GradeBadge";

interface ModelGrade {
  model_id: string;
  name: string;
  grade: string;
  label: string;
  score: number;
  best_quant: string | null;
  required_gb: number;
  tok_per_sec: number;
  capability_tags: string[];
  is_moe: boolean;
  cpu_offload_possible: boolean;
  ollama_tag: string | null;
}

interface Props {
  model: ModelGrade;
  onInstall: (ollamaTag: string) => void;
  installing: boolean;
  installed?: boolean;
  downloadStatus?: string;
}

export const ModelGradeCard: React.FC<Props> = ({
  model,
  onInstall,
  installing,
  installed = false,
  downloadStatus,
}) => {
  const canInstall = model.grade !== "F" && model.ollama_tag && !installed;
  const showProgress =
    installing && (downloadStatus === "downloading" || downloadStatus === "DOWNLOADING" || downloadStatus === "Starting…");

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 16,
        padding: "12px 16px",
        borderBottom: "1px solid #f0f0f0",
        opacity: model.grade === "F" ? 0.5 : 1,
        transition: "opacity 0.15s",
      }}
    >
      <GradeBadge grade={model.grade} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          <span style={{ fontWeight: 600 }}>{model.name}</span>
          {model.is_moe && (
            <Tooltip title="Mixture of Experts — memory efficient">
              <Tag color="purple">MoE</Tag>
            </Tooltip>
          )}
          {model.capability_tags.map((tag) => (
            <Tag key={tag} color="blue">{tag}</Tag>
          ))}
        </div>
        <div style={{ fontSize: 12, color: "#8c8c8c", marginTop: 2 }}>
          {model.label}
          {model.best_quant && ` · ${model.best_quant}`}
          {model.required_gb > 0 && ` · ${model.required_gb.toFixed(1)} GB`}
          {model.tok_per_sec > 0 && ` · ~${model.tok_per_sec.toFixed(0)} tok/s`}
          {model.cpu_offload_possible && " · CPU offload"}
        </div>
      </div>
      {installed ? (
        <Tag color="success">Installed</Tag>
      ) : canInstall ? (
        <Button
          size="small"
          type="primary"
          loading={installing && !downloadStatus}
          onClick={() => model.ollama_tag && onInstall(model.ollama_tag)}
        >
          {showProgress ? downloadStatus || "Installing…" : "Install"}
        </Button>
      ) : (
        <Button size="small" type="link">
          Requirements →
        </Button>
      )}
    </div>
  );
};
