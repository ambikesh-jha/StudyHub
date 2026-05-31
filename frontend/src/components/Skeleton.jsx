export default function Skeleton({ rows = 1, className = "" }) {
  return (
    <div className={`skeleton-stack ${className}`}>
      {Array.from({ length: rows }).map((_, index) => (
        <div className="skeleton-line" key={index} />
      ))}
    </div>
  );
}
