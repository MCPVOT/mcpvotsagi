
import { FC } from "react";

interface IconProps {
  name: string;
  size?: number;
  className?: string;
}

export const Icon: FC<IconProps> = ({ name, size = 24, className = "" }) => {
  return (
    <img
      src={`/icons/${name}.svg`}
      alt={name}
      width={size}
      height={size}
      className={className}
    />
  );
};

export default Icon;
