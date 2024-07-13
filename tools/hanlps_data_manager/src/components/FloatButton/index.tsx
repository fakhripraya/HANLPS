import React, {
  CSSProperties,
  ReactNode,
  MouseEventHandler,
} from "react";
import "./style.scss";

interface FloatButtonProps {
  style?: CSSProperties;
  onClick?: MouseEventHandler<HTMLDivElement>;
  className?: string;
  children?: ReactNode;
}

const FloatButton: React.FC<FloatButtonProps> = ({
  style,
  onClick,
  className = "",
  children,
}: FloatButtonProps) => {
  return (
    <div
      style={style}
      onClick={onClick}
      className={`floatbutton-container ${className}`}>
      {children}
    </div>
  );
};

export default FloatButton;
