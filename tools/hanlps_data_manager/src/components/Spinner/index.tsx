import React from "react";
import Modal from "../Modal/index";
import { usePromiseTracker } from "react-promise-tracker";
import "./style.scss";

const Spinner: React.FC = () => {
  const { promiseInProgress } = usePromiseTracker();

  return (
    promiseInProgress && (
      <Modal
        clicked={() => {}}
        bgClassName="dark-bg-color"
        className="spinner-container"
        toggle={true}>
        <div className="spinner-wrapper">Loading...</div>
      </Modal>
    )
  );
};

export default Spinner;
