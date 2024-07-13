import React, {
  CSSProperties,
  ChangeEventHandler,
} from "react";
import "./style.scss";

interface TextAreaProps {
  placeholder?: string;
  readOnly?: boolean;
  value: string | undefined;
  style?: CSSProperties;
  onChange?: ChangeEventHandler<HTMLTextAreaElement>;
  maxLength?: number;
  className?: string;
}

const TextArea: React.FC<TextAreaProps> = ({
  placeholder,
  readOnly = false,
  value,
  style,
  onChange,
  maxLength,
  className = "",
}: TextAreaProps) => {
  return (
    <textarea
      placeholder={placeholder}
      readOnly={readOnly}
      value={value}
      style={style}
      onChange={onChange}
      maxLength={maxLength}
      className={`text-area ${className}`}></textarea>
  );
};

export default TextArea;
