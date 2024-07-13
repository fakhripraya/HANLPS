import React, { useEffect, useState } from "react";

interface DynamicDropdownProps {
  values: string[];
  value?: string;
  toggle: boolean;
  className?: string;
  style?: React.CSSProperties;
  showTitle?: boolean;
  title?: string;
  onChange: (value: string) => void;
}

export default function DynamicDropdown(
  props: DynamicDropdownProps
) {
  const [value, setValue] = useState<string>(
    props.value
      ? props.value
      : props.values.length > 0
      ? props.values[0]
      : ""
  );
  const [toggle, setToggle] = useState<boolean>(
    props.toggle
  );

  function handleOpenFilter(values: string[]) {
    if (values.length === 0) return;
    setToggle(!toggle);
  }

  function handleChangeValue(val: string) {
    if (val === "No Data") return;
    setValue(val);
    props.onChange(val);
    handleOpenFilter(props.values);
  }

  useEffect(() => {
    setValue(
      props.value ||
        (props.values.length > 0 ? props.values[0] : "")
    );
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
        {props.title || "Sort by : "}
      </span>
      <div
        style={props.style}
        className="dropdown-button-container">
        <button
          onClick={() => handleOpenFilter(props.values)}
          className="dropdown-button-wrapper">
          <label className="dropdown-value dropdown-button-label">
            <span className="light-color">
              {props.values.length === 0
                ? "loading..."
                : value}
            </span>
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
