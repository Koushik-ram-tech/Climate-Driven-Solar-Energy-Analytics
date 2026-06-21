/**
 * src/components/ui/Tag.tsx
 */

import type { HTMLAttributes } from "react";
import { cn } from "@lib/utils/cn";

export interface TagProps extends HTMLAttributes<HTMLSpanElement> {}

export function Tag({ className, children, ...rest }: TagProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center border border-ink px-3 py-1 font-mono text-caption text-ink transition-colors hover:bg-ink hover:text-cream",
        className,
      )}
      {...rest}
    >
      {children}
    </span>
  );
}
