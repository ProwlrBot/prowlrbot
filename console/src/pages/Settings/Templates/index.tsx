import { useState, useEffect, useCallback, useMemo } from "react";
import { Button, Input, Select, Tag, message } from "antd";
import {
  SearchOutlined,
  DownloadOutlined,
  AppstoreOutlined,
} from "@ant-design/icons";
import { request } from "../../../api";
import styles from "./index.module.less";

/* ------------------------------------------------------------------ */
/* Types                                                               */
/* ------------------------------------------------------------------ */

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  avatar?: string;
  skills: string[];
  downloads: number;
  builtin: boolean;
  author?: string;
}

/* ------------------------------------------------------------------ */
/* Categories                                                          */
/* ------------------------------------------------------------------ */

const ALL_CATEGORIES = [
  { value: "", label: "All Categories" },
  { value: "assistant", label: "Assistant" },
  { value: "automation", label: "Automation" },
  { value: "coding", label: "Coding" },
  { value: "communication", label: "Communication" },
  { value: "creative", label: "Creative" },
  { value: "data", label: "Data & Analytics" },
  { value: "devops", label: "DevOps" },
  { value: "education", label: "Education" },
  { value: "monitoring", label: "Monitoring" },
  { value: "productivity", label: "Productivity" },
  { value: "research", label: "Research" },
  { value: "security", label: "Security" },
];

/* ------------------------------------------------------------------ */
/* Default Templates                                                   */
/* ------------------------------------------------------------------ */

const defaultTemplates: Template[] = [
  {
    id: "general-assistant",
    name: "General Assistant",
    description:
      "A versatile AI assistant ready for everyday tasks including Q&A, writing, research, and general problem-solving.",
    category: "assistant",
    skills: ["file_reader", "browser_visible", "news"],
    downloads: 1250,
    builtin: true,
  },
  {
    id: "code-reviewer",
    name: "Code Reviewer",
    description:
      "Specialized agent for reviewing code, finding bugs, suggesting improvements, and enforcing coding standards.",
    category: "coding",
    skills: ["file_reader", "browser_visible"],
    downloads: 890,
    builtin: true,
  },
  {
    id: "document-processor",
    name: "Document Processor",
    description:
      "Handles PDF, DOCX, PPTX, and XLSX files — extract text, fill forms, generate reports, and convert formats.",
    category: "productivity",
    skills: ["pdf", "docx", "pptx", "xlsx", "file_reader"],
    downloads: 720,
    builtin: true,
  },
  {
    id: "web-monitor",
    name: "Web Monitor",
    description:
      "Monitors websites for changes, tracks API endpoints, and sends notifications when updates are detected.",
    category: "monitoring",
    skills: ["browser_visible", "cron", "news"],
    downloads: 540,
    builtin: true,
  },
  {
    id: "research-analyst",
    name: "Research Analyst",
    description:
      "Gathers information from multiple sources, summarizes findings, and produces structured research reports.",
    category: "research",
    skills: ["browser_visible", "news", "file_reader", "pdf"],
    downloads: 430,
    builtin: true,
  },
  {
    id: "devops-assistant",
    name: "DevOps Assistant",
    description:
      "Helps with infrastructure tasks, deployment scripts, container management, and CI/CD pipeline configuration.",
    category: "devops",
    skills: ["file_reader"],
    downloads: 310,
    builtin: true,
  },
];

/* ------------------------------------------------------------------ */
/* Main Page                                                           */
/* ------------------------------------------------------------------ */

function TemplatesPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [templates, setTemplates] = useState<Template[]>(defaultTemplates);
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");

  const fetchTemplates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await request<Template[]>("/templates").catch(() => null);
      if (Array.isArray(data) && data.length > 0) {
        setTemplates(data);
      } else {
        setTemplates(defaultTemplates);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load templates",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  /* ---- Filtering ---- */

  const filtered = useMemo(() => {
    let result = templates;
    if (categoryFilter) {
      result = result.filter((t) => t.category === categoryFilter);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (t) =>
          t.name.toLowerCase().includes(q) ||
          t.description.toLowerCase().includes(q) ||
          t.skills.some((s) => s.toLowerCase().includes(q)),
      );
    }
    return result;
  }, [templates, categoryFilter, searchQuery]);

  /* ---- Use Template ---- */

  const handleUseTemplate = async (template: Template) => {
    try {
      await request(`/templates/${template.id}/download`, { method: "POST" });
      message.success(`Template "${template.name}" applied successfully`);
    } catch {
      message.info(
        `Template "${template.name}" selected — the endpoint may not be available yet`,
      );
    }
  };

  /* ---- Avatar helper ---- */

  const renderAvatar = (template: Template) => {
    if (template.avatar) {
      return (
        <img
          src={template.avatar}
          alt={template.name}
          className={styles.templateAvatarImg}
        />
      );
    }
    return (
      <div className={styles.templateAvatar}>
        {template.name.charAt(0).toUpperCase()}
      </div>
    );
  };

  /* ---- render ---- */

  return (
    <div className={styles.page}>
      {/* ---- Page header ---- */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Agent Templates</h2>
        <p className={styles.sectionDesc}>
          Browse pre-configured agent templates to quickly set up specialized
          agents with the right skills and personality.
        </p>
      </div>

      {loading ? (
        <div className={styles.centerState}>
          <span className={styles.stateText}>Loading templates...</span>
        </div>
      ) : error ? (
        <div className={styles.centerState}>
          <span className={styles.stateTextError}>{error}</span>
          <Button
            size="small"
            onClick={fetchTemplates}
            style={{ marginTop: 12 }}
          >
            Retry
          </Button>
        </div>
      ) : (
        <>
          {/* ---- Filter Bar ---- */}
          <div className={styles.filterBar}>
            <Input
              className={styles.searchInput}
              placeholder="Search templates..."
              prefix={<SearchOutlined />}
              allowClear
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <Select
              className={styles.categoryFilter}
              value={categoryFilter}
              onChange={setCategoryFilter}
              options={ALL_CATEGORIES}
            />
          </div>

          {/* ---- Template Grid ---- */}
          {filtered.length === 0 ? (
            <div className={styles.emptyState}>
              <AppstoreOutlined className={styles.emptyIcon} />
              <span>No templates match your search</span>
            </div>
          ) : (
            <div className={styles.templateGrid}>
              {filtered.map((template) => (
                <div key={template.id} className={styles.templateCard}>
                  {/* Card Top */}
                  <div className={styles.cardTop}>
                    {renderAvatar(template)}
                    <div className={styles.cardMeta}>
                      <div className={styles.templateName}>
                        {template.name}
                        {template.builtin && (
                          <span className={styles.builtinBadge}>Built-in</span>
                        )}
                      </div>
                      <div className={styles.templateCategory}>
                        {template.category}
                      </div>
                    </div>
                  </div>

                  {/* Card Body */}
                  <div className={styles.cardBody}>
                    <div className={styles.templateDesc}>
                      {template.description}
                    </div>
                  </div>

                  {/* Skills Tags */}
                  {template.skills.length > 0 && (
                    <div className={styles.cardSkills}>
                      {template.skills.map((skill) => (
                        <Tag key={skill} color="blue">
                          {skill}
                        </Tag>
                      ))}
                    </div>
                  )}

                  {/* Card Footer */}
                  <div className={styles.cardFooter}>
                    <span className={styles.downloadCount}>
                      <DownloadOutlined />
                      {template.downloads.toLocaleString()}
                    </span>
                    <Button
                      type="primary"
                      size="small"
                      onClick={() => handleUseTemplate(template)}
                    >
                      Use Template
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default TemplatesPage;
