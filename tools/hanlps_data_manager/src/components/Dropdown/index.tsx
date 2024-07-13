import React, { useEffect, useState } from "react";
import "./styles.scss";

interface DropdownProps {
  values: string[];
  value?: string;
  toggle: boolean;
  className?: string;
  style?: React.CSSProperties;
  showTitle?: boolean;
  onChange: (value: string) => void;
}

export default function Dropdown(props: DropdownProps) {
  const [value, setValue] = useState<string>(
    props.value ? props.value : props.values[0]
  );
  const [toggle, setToggle] = useState<boolean>(
    props.toggle
  );

  function handleOpenFilter() {
    setToggle(!toggle);
  }

  function handleChangeValue(val: string) {
    setValue(val);
    props.onChange(val);
    handleOpenFilter();
  }

  useEffect(() => {
    setValue(props.value || props.values[0]);
  }, [props.value, props.values]);

  return (
    <div
      className={
        "dropdown-container " + (props.className || "")
      }>
      <span
        style={{
          display:
            props.showTitle === false ? "none" : undefined,
        }}
        className="dropdown-title">
        Sort by :{" "}
      </span>
      <div
        style={props.style}
        className="dropdown-button-container">
        <button
          onClick={handleOpenFilter}
          className="dropdown-button-wrapper">
          <label className="dropdown-value dropdown-button-label">
            <span className="light-color">{value}</span>
          </label>
          <span
            style={{
              transform: toggle
                ? "rotate(0deg)"
                : "rotate(180deg)",
            }}
            className="dropdown-button-label-after"
          />
        </button>
        <div
          className={
            toggle
              ? "filter-dropdown-items-container"
              : "filter-dropdown-items-container filter-dropdown-hide"
          }>
          <ul className="filter-dropdown-items-unordered-list">
            {props.values.map((val, index) => (
              <li
                key={`${val}-${index}`}
                className="filter-dropdown-items-list">
                <button
                  onClick={() => {
                    handleChangeValue(val);
                  }}
                  className="filter-dropdow-list-button">
                  <span>{val}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
