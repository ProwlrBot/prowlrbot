import { Button, Rate, Tag } from "antd";
import { Download, Package } from "lucide-react";
import styles from "../index.module.less";

export interface MarketplaceListing {
  id: string;
  name: string;
  author: string;
  description: string;
  category: string;
  rating: number;
  ratingCount: number;
  downloads: number;
  price: number;
  tags: string[];
  imageUrl?: string;
  installed?: boolean;
}

interface ListingCardProps {
  listing: MarketplaceListing;
  onInstall: (listing: MarketplaceListing) => void;
}

const CATEGORY_COLORS: Record<string, string> = {
  skills: "cyan",
  agents: "purple",
  tools: "blue",
  integrations: "geekblue",
  templates: "orange",
  workflows: "magenta",
  channels: "green",
  monitors: "volcano",
};

function formatDownloads(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}K`;
  return String(count);
}

export default function ListingCard({ listing, onInstall }: ListingCardProps) {
  const categoryColor = CATEGORY_COLORS[listing.category] || "default";

  return (
    <div className={styles.card}>
      <div className={styles.cardImage}>
        {listing.imageUrl ? (
          <img src={listing.imageUrl} alt={listing.name} />
        ) : (
          <Package size={40} strokeWidth={1.2} />
        )}
      </div>

      <div className={styles.cardInfo}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
          }}
        >
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3 className={styles.cardTitle}>{listing.name}</h3>
            <p className={styles.cardAuthor}>by {listing.author}</p>
          </div>
          <Tag color={categoryColor} className={styles.categoryBadge}>
            {listing.category}
          </Tag>
        </div>

        <p className={styles.cardDescription}>{listing.description}</p>

        <div className={styles.cardStats}>
          <span className={styles.rating}>
            <Rate disabled defaultValue={listing.rating} allowHalf />
            <span className={styles.ratingCount}>({listing.ratingCount})</span>
          </span>
          <span className={styles.downloads}>
            <Download size={12} />
            {formatDownloads(listing.downloads)}
          </span>
          <span
            className={`${styles.price} ${listing.price === 0 ? styles.priceFree : ""}`}
          >
            {listing.price === 0 ? "Free" : `$${listing.price.toFixed(2)}`}
          </span>
        </div>
      </div>

      <div className={styles.cardFooter}>
        <div className={styles.tags}>
          {listing.tags.slice(0, 3).map((tag) => (
            <span key={tag} className={styles.tag}>
              {tag}
            </span>
          ))}
          {listing.tags.length > 3 && (
            <span className={styles.tag}>+{listing.tags.length - 3}</span>
          )}
        </div>
        <Button
          type={listing.installed ? "default" : "primary"}
          size="small"
          className={`${styles.installButton} ${listing.installed ? styles.installed : ""}`}
          onClick={(e) => {
            e.stopPropagation();
            if (!listing.installed) {
              onInstall(listing);
            }
          }}
          disabled={listing.installed}
          style={
            !listing.installed
              ? { background: "#00e5ff", borderColor: "#00e5ff" }
              : undefined
          }
        >
          {listing.installed ? "Installed" : "Install"}
        </Button>
      </div>
    </div>
  );
}
