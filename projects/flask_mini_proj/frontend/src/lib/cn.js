import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** shadcn/ui-compatible className merge */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
