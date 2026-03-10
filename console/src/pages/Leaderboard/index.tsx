import { useEffect, useState } from "react";
import { Card, Table, Tabs, Tag, Button, Empty, Tooltip } from "antd";
import {
  Medal,
  Crown,
  Award,
  TrendingUp,
  DollarSign,
  Play,
} from "lucide-react";
import {
  getModelRankings,
  getModelHistory,
  getLeaderboardCategories,
} from "../../api/modules/leaderboard";
import styles from "./index.module.less";

// ── Types ──
interface ModelRanking {
  rank: number;
  model_name: string;
  score: number;
  cost_per_1k: number;
  category?: string;
  provider?: string;
  last_updated?: string;
}

interface ModelHistoryPoint {
  date: string;
  score: number;
}

// ── Constants ──
const RANK_MEDALS: Record<number, { icon: React.ReactNode; color: string }> = {
  1: { icon: <Crown size={18} />, color: "#FFD700" },
  2: { icon: <Medal size={18} />, color: "#C0C0C0" },
  3: { icon: <Award size={18} />, color: "#CD7F32" },
};

const PODIUM_CLASS: Record<number, string> = {
  0: "firstPlace",
  1: "secondPlace",
  2: "thirdPlace",
};

export default function Leaderboard() {
  const [rankings, setRankings] = useState<ModelRanking[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [modelHistory, setModelHistory] = useState<ModelHistoryPoint[]>([]);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);

  // ── Fetch Data ──
  useEffect(() => {
    getLeaderboardCategories()
      .then((data: any) => {
        if (Array.isArray(data)) setCategories(data);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const cat = selectedCategory === "all" ? undefined : selectedCategory;
    getModelRankings(cat)
      .then((data: any) => {
        if (Array.isArray(data)) setRankings(data);
      })
      .catch(() => {});
  }, [selectedCategory]);

  function handleModelClick(model: string) {
    setSelectedModel(model);
    getModelHistory(model)
      .then((data: any) => {
        if (Array.isArray(data)) setModelHistory(data);
      })
      .catch(() => setModelHistory([]));
  }

  // ── Top 3 Models ──
  const topThree = rankings.slice(0, 3);
  const remaining = rankings.slice(3);

  // ── Table Columns ──
  const columns = [
    {
      title: "Rank",
      dataIndex: "rank",
      key: "rank",
      width: 80,
      render: (rank: number) => {
        const medal = RANK_MEDALS[rank];
        if (medal) {
          return (
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 4,
                color: medal.color,
                fontWeight: 700,
              }}
            >
              {medal.icon} {rank}
            </span>
          );
        }
        return <span style={{ fontWeight: 600, color: "#595959" }}>{rank}</span>;
      },
    },
    {
      title: "Model",
      dataIndex: "model_name",
      key: "model_name",
      render: (name: string, record: ModelRanking) => (
        <span
          style={{ fontWeight: 600, cursor: "pointer", color: "#1a1a2e" }}
          onClick={() => handleModelClick(name)}
        >
          {name}
          {record.provider && (
            <Tag
              color="default"
              style={{ marginLeft: 8, borderRadius: 6, fontSize: 11 }}
            >
              {record.provider}
            </Tag>
          )}
        </span>
      ),
    },
    {
      title: "Score",
      dataIndex: "score",
      key: "score",
      width: 200,
      render: (score: number) => (
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div className={styles.scoreBar}>
            <div style={{ width: `${Math.min(100, score)}%` }} />
          </div>
          <span style={{ fontWeight: 700, fontSize: 14, minWidth: 42 }}>
            {score.toFixed(1)}
          </span>
        </div>
      ),
    },
    {
      title: "Cost / 1K tokens",
      dataIndex: "cost_per_1k",
      key: "cost_per_1k",
      width: 140,
      render: (cost: number) => (
        <span className={styles.costBadge}>
          <DollarSign size={12} />
          {cost != null ? `$${cost.toFixed(4)}` : "N/A"}
        </span>
      ),
    },
  ];

  // ── Category tabs ──
  const tabItems = [
    { key: "all", label: "All" },
    ...categories.map((cat) => ({ key: cat, label: cat })),
  ];

  return (
    <div className={styles.leaderboard}>
      {/* ── Header ── */}
      <div className={styles.header}>
        <h1>
          <Medal size={22} color="#6B5CE7" />
          Model Leaderboard
        </h1>
        <Tooltip title="Run a benchmark across configured providers (coming soon)">
          <Button icon={<Play size={14} />} disabled>
            Run Benchmark
          </Button>
        </Tooltip>
      </div>

      {/* ── Category Tabs ── */}
      <div className={styles.categoryTabs}>
        <Tabs
          activeKey={selectedCategory}
          onChange={setSelectedCategory}
          items={tabItems}
        />
      </div>

      {rankings.length === 0 ? (
        <Empty
          description="No model rankings available yet"
          style={{ padding: 60 }}
        />
      ) : (
        <>
          {/* ── Podium: Top 3 ── */}
          {topThree.length > 0 && (
            <div className={styles.topThree}>
              {topThree.map((model, idx) => {
                const cls =
                  styles[PODIUM_CLASS[idx] as keyof typeof styles] || "";
                return (
                  <div
                    key={model.model_name}
                    className={cls}
                    onClick={() => handleModelClick(model.model_name)}
                    style={{ cursor: "pointer" }}
                  >
                    <div className="podiumRank">
                      {idx === 0 && <Crown size={28} />}
                      {idx === 1 && <Medal size={28} />}
                      {idx === 2 && <Award size={28} />}
                    </div>
                    <div className="podiumModel">{model.model_name}</div>
                    <div className="podiumScore">{model.score.toFixed(1)}</div>
                    <div className="podiumMeta">
                      <DollarSign size={12} />
                      {model.cost_per_1k != null
                        ? `$${model.cost_per_1k.toFixed(4)} / 1K`
                        : "N/A"}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* ── Full Rankings Table ── */}
          <div className={styles.table}>
            <Table
              dataSource={remaining.length > 0 ? remaining : rankings}
              columns={columns}
              rowKey="model_name"
              pagination={false}
              size="middle"
            />
          </div>
        </>
      )}

      {/* ── Model History Detail ── */}
      {selectedModel && (
        <Card
          title={
            <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <TrendingUp size={16} />
              Score History: {selectedModel}
            </span>
          }
          extra={
            <Button type="text" size="small" onClick={() => setSelectedModel(null)}>
              Close
            </Button>
          }
          className={styles.modelCard}
        >
          {modelHistory.length === 0 ? (
            <Empty description="No historical data available" />
          ) : (
            <Table
              dataSource={modelHistory}
              columns={[
                {
                  title: "Date",
                  dataIndex: "date",
                  key: "date",
                  render: (d: string) => {
                    const dt = new Date(d);
                    return dt.toLocaleDateString(undefined, {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    });
                  },
                },
                {
                  title: "Score",
                  dataIndex: "score",
                  key: "score",
                  render: (s: number) => (
                    <span style={{ fontWeight: 600 }}>{s.toFixed(1)}</span>
                  ),
                },
              ]}
              rowKey="date"
              pagination={false}
              size="small"
            />
          )}
        </Card>
      )}
    </div>
  );
}
