interface RukmaniAvatarProps {
  size?: "sm" | "lg";
}

/** Rukmani's avatar: her Sinhala initial on Kapruka purple, ringed in the logo's yellow. */
export function RukmaniAvatar({ size = "sm" }: RukmaniAvatarProps) {
  const sizes = size === "lg" ? "size-20 text-3xl ring-4" : "size-9 text-base ring-2";
  return (
    <div
      aria-hidden
      className={`${sizes} flex shrink-0 items-center justify-center rounded-full bg-brand font-bold text-sun ring-sun`}
    >
      රු
    </div>
  );
}
