import { ReactNode } from "react";
import "./style.scss";

interface CardProps {
  onKeyUp?: (
    event: React.KeyboardEvent<HTMLDivElement>
  ) => void;
  onClick?: (
    event: React.MouseEvent<HTMLDivElement>
  ) => void;
  className?: string;
  children?: ReactNode;
}

const Card: React.FC<CardProps> = (props) => {
  return (
    <div
      onKeyUp={props.onKeyUp}
      onClick={props.onClick}
      className={"card-container " + props.className}>
      {props.children}
    </div>
  );
};

export default Card;
