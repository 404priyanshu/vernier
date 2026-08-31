export function Mark({ className = "h-7 w-7" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
    >
      <rect width="32" height="32" rx="4" fill="var(--primary)" />
      <path
        d="M9 24V8h5.2c3.4 0 5.4 1.8 5.4 4.6 0 2.1-1.1 3.6-3 4.3L22 24h-3.4l-5.1-6.6H12.4V24H9Zm3.4-9.3h1.6c1.8 0 2.8-.9 2.8-2.3s-1-2.2-2.8-2.2h-1.6v4.5Z"
        fill="white"
      />
      <rect x="6" y="27" width="10" height="2" rx="1" fill="var(--accent)" />
    </svg>
  );
}
