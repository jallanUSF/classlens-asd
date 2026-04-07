export function EmptyClassroom({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 200 160"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      {/* Desk */}
      <rect x="40" y="100" width="120" height="8" rx="4" fill="#E2E8F0" />
      <rect x="50" y="108" width="8" height="24" rx="2" fill="#CBD5E1" />
      <rect x="142" y="108" width="8" height="24" rx="2" fill="#CBD5E1" />

      {/* Chair */}
      <rect x="80" y="112" width="40" height="6" rx="3" fill="#D4E6F1" />
      <rect x="82" y="88" width="36" height="24" rx="4" fill="#D4E6F1" />
      <rect x="84" y="118" width="6" height="16" rx="2" fill="#B8D4E8" />
      <rect x="110" y="118" width="6" height="16" rx="2" fill="#B8D4E8" />

      {/* Book on desk */}
      <rect x="55" y="92" width="24" height="8" rx="2" fill="#4A7FA5" opacity="0.6" />
      <rect x="57" y="93" width="20" height="6" rx="1" fill="#5B8FB9" opacity="0.8" />

      {/* Pencil on desk */}
      <rect x="130" y="94" width="20" height="3" rx="1" fill="#E8A838" opacity="0.7" />
      <polygon points="150,95.5 155,95.5 152.5,93" fill="#E8A838" opacity="0.5" />

      {/* Star decoration */}
      <path
        d="M100 20 L103 30 L113 30 L105 36 L108 46 L100 40 L92 46 L95 36 L87 30 L97 30 Z"
        fill="#4ECDC4"
        opacity="0.3"
      />

      {/* Small stars */}
      <circle cx="60" cy="35" r="3" fill="#E8A838" opacity="0.25" />
      <circle cx="145" cy="28" r="2.5" fill="#8B7EC8" opacity="0.25" />
      <circle cx="155" cy="50" r="2" fill="#4ECDC4" opacity="0.2" />
      <circle cx="50" cy="55" r="2" fill="#5B8FB9" opacity="0.2" />

      {/* Apple on desk */}
      <circle cx="120" cy="92" r="6" fill="#D4726A" opacity="0.5" />
      <path d="M120 86 L121 83" stroke="#4ECDC4" strokeWidth="1.5" opacity="0.5" />
    </svg>
  );
}
