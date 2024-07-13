import React, {
  CSSProperties,
  KeyboardEventHandler,
  ChangeEventHandler,
  Ref,
} from "react";
import "./style.scss";

interface TextInputProps {
  value?: string;
  defaultValue?: string;
  readOnly?: boolean;
  placeholder?: string;
  style?: CSSProperties;
  onEnter?: () => void;
  onKeyUp?: KeyboardEventHandler<HTMLInputElement>;
  onInput?: ChangeEventHandler<HTMLInputElement>;
  onFocus?: React.FocusEventHandler<HTMLInputElement>;
  onChange?: ChangeEventHandler<HTMLInputElement>;
  maxLength?: number;
  type?: string;
  autoFocus?: boolean;
  autoComplete?: string;
  className?: string;
}

const TextInput = React.forwardRef<
  HTMLInputElement,
  TextInputProps
>((props, ref: Ref<HTMLInputElement>) => (
  <input
    ref={ref}
    value={props.value}
    defaultValue={props.defaultValue}
    readOnly={props.readOnly}
    placeholder={props.placeholder}
    style={props.style}
    onKeyUp={(e) => {
      if (
        (e.key === "Enter" || e.keyCode === 13) &&
        typeof props.onEnter !== "undefined"
      ) {
        props.onEnter();
      }
      if (typeof props.onKeyUp !== "undefined") {
        props.onKeyUp(e);
      }
    }}
    onInput={props.onInput}
    onFocus={props.onFocus}
    onChange={props.onChange}
    maxLength={props.maxLength}
    type={props.type}
    autoFocus={props.autoFocus}
    autoComplete={props.autoComplete}
    className={`input-text ${props.className}`}
  />
));

export default TextInput;
