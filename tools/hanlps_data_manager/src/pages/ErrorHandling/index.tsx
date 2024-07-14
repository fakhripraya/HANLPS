import { ReactNode, CSSProperties } from "react";
import "./style.scss";

interface IErrorHandling {
  className?: string;
  errorMessage?: string;
  children?: ReactNode;
  containerStyle?: CSSProperties;
  wrapperStyle?: CSSProperties;
}

export default function ErrorHandling({
  className = "",
  errorMessage,
  children,
  containerStyle,
  wrapperStyle,
}: IErrorHandling) {
  return (
    <div
      style={containerStyle}
      className={`error-handling-container ${className}`}>
      <div
        style={wrapperStyle}
        className="error-handling-wrapper">
        {errorMessage}
        {children}
      </div>
    </div>
  );
}
