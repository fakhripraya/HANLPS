import React, { CSSProperties, ReactNode, MouseEventHandler } from "react";
import "./style.scss";

interface ButtonProps {
  style?: CSSProperties;
  onClick?: MouseEventHandler<HTMLDivElement>;
  className?: string;
  children?: ReactNode;
}

const Button: React.FC<ButtonProps> = ({
  style,
  onClick,
  className = "",
  children,
}: ButtonProps) => {
  return (
    <div
      style={style}
      onClick={onClick}
      className={`button-container main-bg-color ${className}`}
    >
      {children}
    </div>
  );
};

export default Button;
