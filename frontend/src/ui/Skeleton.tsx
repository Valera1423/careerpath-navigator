interface Props { width?: string; height?: string; radius?: string }

export function Skeleton({ width = '100%', height = '16px', radius = '8px' }: Props) {
  return <div className="skeleton" style={{ width, height, borderRadius: radius }} />;
}

export function SkeletonCard() {
  return (
    <div className="card">
      <Skeleton width="60%" height="20px" />
      <Skeleton width="100%" height="14px" />
      <Skeleton width="80%" height="14px" />
    </div>
  );
}

export function SkeletonList({ rows = 3 }: { rows?: number }) {
  return (
    <div className="screen">
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
