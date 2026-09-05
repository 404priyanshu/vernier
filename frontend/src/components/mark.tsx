export function Mark({ className = "h-7 w-7" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
    >
      <rect width="32" height="32" rx="3" fill="var(--ink)" />
      <path
        d="M7 8h4l5 13 5-13h4l-7.2 17h-3.6L7 8Z"
        fill="white"
      />
    </svg>
  );
}
