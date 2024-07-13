import React from "react";
import "./style.scss";

interface CheckboxProps {
  className?: string;
  title: string;
  onChange: React.ChangeEventHandler<HTMLInputElement>;
  checked: boolean;
}

const Checkbox: React.FC<CheckboxProps> = (props) => {
  return (
    <label
      className={
        "checkbox-container " + (props.className || "")
      }>
      <span className="checkbox-title">{props.title}</span>
      <input
        onChange={props.onChange}
        checked={props.checked}
        type="checkbox"
      />
      <span className="checkbox-checkmark" />
    </label>
  );
};

export default Checkbox;
