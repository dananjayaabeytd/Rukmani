import { LoaderCircle } from "lucide-react";

/** Shows what Rukmani is doing right now, e.g. "Searching Kapruka for gifts…". */
export function StatusPill({ label }: { label: string }) {
  return (
    <div
      role="status"
      className="flex w-fit items-center gap-2 rounded-full bg-brand-mist px-3 py-1.5 text-sm text-brand"
    >
      <LoaderCircle className="size-4 animate-spin" aria-hidden />
      {label}…
    </div>
  );
}
