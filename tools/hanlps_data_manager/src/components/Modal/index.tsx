import "./style.scss";
import React, {
  Fragment,
  ReactNode,
  useEffect,
} from "react";

interface ModalProps {
  className?: string;
  bgClassName?: string;
  toggle: boolean;
  clicked?: () => void;
  children?: ReactNode;
}

const Modal: React.FC<ModalProps> = ({
  className,
  bgClassName,
  children,
  toggle,
  clicked,
}) => {
  if (!clicked) clicked = () => null;

  const handleOnClick = () => {
    clicked();
  };

  useEffect(() => {
    // useEffect logic can be added here if needed
  }, []);

  return (
    <Fragment>
      <div
        onClick={handleOnClick}
        className={
          toggle ? `modal-background ${bgClassName}` : ""
        }
      />
      <div
        style={{
          display: toggle ? "block" : "none",
        }}
        className={"modal-container " + (className || "")}>
        {children}
      </div>
    </Fragment>
  );
};

export default Modal;
