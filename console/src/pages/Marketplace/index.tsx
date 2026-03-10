import { useState, useEffect, useCallback, useRef } from "react";
import { Input, Tabs, Spin, message } from "antd";
import { Store, Search, TrendingUp, Star, Package } from "lucide-react";
import { request } from "../../api/request";
import ListingCard from "./components/ListingCard";
import type { MarketplaceListing } from "./components/ListingCard";
import styles from "./index.module.less";

interface Category {
  key: string;
  label: string;
  count: number;
}

function MarketplacePage() {
  const [listings, setListings] = useState<MarketplaceListing[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("popular");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchListings = useCallback(
    async (tab: string, category?: string, query?: string) => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (tab) params.set("sort", tab);
        if (category) params.set("category", category);
        if (query) params.set("q", query);
        const data = await request<MarketplaceListing[]>(
          `/marketplace/listings?${params.toString()}`,
        );
        setListings(Array.isArray(data) ? data : []);
      } catch {
        setListings([]);
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const fetchCategories = useCallback(async () => {
    try {
      const data = await request<Category[]>("/marketplace/categories");
      setCategories(Array.isArray(data) ? data : []);
    } catch {
      setCategories([]);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
    fetchListings("popular");
  }, [fetchCategories, fetchListings]);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    setSelectedCategory("");
    setSearchQuery("");
    if (tab === "category") {
      // Don't fetch — user picks a category first
      setListings([]);
    } else {
      fetchListings(tab);
    }
  };

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    fetchListings("all", category);
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      fetchListings(activeTab, selectedCategory || undefined, value || undefined);
    }, 400);
  };

  const handleInstall = async (listing: MarketplaceListing) => {
    try {
      await request(`/marketplace/listings/${listing.id}/install`, {
        method: "POST",
      });
      message.success(`Installed "${listing.name}" successfully`);
      setListings((prev) =>
        prev.map((l) => (l.id === listing.id ? { ...l, installed: true } : l)),
      );
    } catch {
      message.error(`Failed to install "${listing.name}"`);
    }
  };

  const tabItems = [
    {
      key: "popular",
      label: (
        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <TrendingUp size={14} /> Popular
        </span>
      ),
    },
    {
      key: "top-rated",
      label: (
        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Star size={14} /> Top Rated
        </span>
      ),
    },
    {
      key: "all",
      label: (
        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Package size={14} /> All
        </span>
      ),
    },
    {
      key: "category",
      label: (
        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
          By Category
        </span>
      ),
    },
  ];

  return (
    <div className={styles.marketplace}>
      <div className={styles.header}>
        <div className={styles.headerInfo}>
          <div className={styles.headerIcon}>
            <Store size={22} />
          </div>
          <div className={styles.headerText}>
            <h1 className={styles.title}>Marketplace</h1>
            <p className={styles.subtitle}>
              Browse skills, agents, and tools
            </p>
          </div>
        </div>
      </div>

      <div className={styles.searchBar}>
        <Input.Search
          placeholder="Search marketplace..."
          allowClear
          size="large"
          prefix={<Search size={16} color="#bfbfbf" />}
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          onSearch={(value) => {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            fetchListings(
              activeTab,
              selectedCategory || undefined,
              value || undefined,
            );
          }}
        />
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={handleTabChange}
        className={styles.categoryTabs}
        items={tabItems}
      />

      {activeTab === "category" && categories.length > 0 && (
        <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
          {categories.map((cat) => (
            <button
              key={cat.key}
              onClick={() => handleCategorySelect(cat.key)}
              style={{
                padding: "6px 14px",
                borderRadius: 8,
                border:
                  selectedCategory === cat.key
                    ? "2px solid #00e5ff"
                    : "1px solid #e8e8e8",
                background:
                  selectedCategory === cat.key ? "#f0fdff" : "#fff",
                cursor: "pointer",
                fontSize: 13,
                color: selectedCategory === cat.key ? "#00b8d4" : "#666",
                fontWeight: selectedCategory === cat.key ? 600 : 400,
                transition: "all 0.2s",
              }}
            >
              {cat.label} ({cat.count})
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <div className={styles.loadingContainer}>
          <Spin size="large" />
        </div>
      ) : listings.length > 0 ? (
        <div className={styles.grid}>
          {listings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              onInstall={handleInstall}
            />
          ))}
        </div>
      ) : (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>
            <Package size={48} strokeWidth={1} />
          </div>
          <div className={styles.emptyText}>
            {searchQuery
              ? `No results for "${searchQuery}"`
              : activeTab === "category" && !selectedCategory
                ? "Select a category to browse listings"
                : "No listings available yet"}
          </div>
        </div>
      )}
    </div>
  );
}

export default MarketplacePage;
