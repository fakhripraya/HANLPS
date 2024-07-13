import React, { CSSProperties } from "react";
import "./style.scss";
import WGLogo from "../../assets/svg/LIVEJB_V1_LOGO.svg";

interface PageLoadingProps {
  containerStyle?: CSSProperties;
  wrapperStyle?: CSSProperties;
  className?: string;
  loadingMessage: string;
  noLogo?: boolean;
}

const PageLoading: React.FC<PageLoadingProps> = ({
  containerStyle,
  wrapperStyle,
  className = "",
  loadingMessage,
  noLogo = false,
}: PageLoadingProps) => {
  return (
    <div style={containerStyle} className={`page-loading-container ${className}`}>
      <div style={wrapperStyle} className="page-loading-wrapper">
        {!noLogo && (
          <img
            className="spinner-logo-img page-loading-logo-img"
            src={WGLogo}
            alt="WG_LOGO_SPINNER_PAGE_LOADING"
          />
        )}
        <label className="page-loading-text">{loadingMessage}</label>
      </div>
    </div>
  );
};

export default PageLoading;
