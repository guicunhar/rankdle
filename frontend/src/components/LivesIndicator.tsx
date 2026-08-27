import { Heart } from "lucide-react";

export default function LivesIndicator({ total, remaining }: { total: number; remaining: number }) {
  return (
    <div className="flex items-center gap-1" aria-label={`${remaining} de ${total} vidas restantes`}>
      {Array.from({ length: total }, (_, i) => (
        <Heart
          key={i}
          size={18}
          strokeWidth={2}
          className={i < remaining ? "fill-accent-500 text-accent-500" : "fill-transparent text-ink-700"}
        />
      ))}
    </div>
  );
}
