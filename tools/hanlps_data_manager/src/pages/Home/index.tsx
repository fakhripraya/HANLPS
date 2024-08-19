/* eslint-disable react-hooks/exhaustive-deps */
/* eslint-disable @typescript-eslint/no-explicit-any */
import "./style.scss";
import {
  Fragment,
  useEffect,
  useRef,
  useState,
} from "react";
import Button from "../../components/Button";
import {
  EditedBuildingModel,
  MasterData,
} from "../../interfaces/building";
import TextArea from "../../components/TextArea";
import TextInput from "../../components/TextInput";
import { saveAs } from "file-saver";
import { ShowGrabableStoreCardCarousel } from "./modular/ShowCarousels";
import _ from "lodash";
import Modal from "../../components/Modal";
import { formattedNumber } from "../../utils/functions/global";

const HomeDefaultValue:
  | EditedBuildingModel
  | undefined
  | null = {
  building_title: "",
  building_address: "",
  building_proximity_string: "",
  building_proximity: [],
  building_facility_string: "",
  building_facility: [],
  building_description: "",
  housing_price: "0",
  owner_email: "",
  owner_name: "",
  owner_phone_number: "",
  owner_whatsapp: "",
  image_urls: [],
  isEdited: false,
};

export default function Home() {
  // REFS //
  const chatBodyContainerRef =
    useRef<HTMLInputElement>(null);

  const [data, setData] = useState<MasterData | null>(null);
  const [isLoading, setIsLoading] =
    useState<boolean>(false);
  const [selected, setSelected] = useState<
    EditedBuildingModel | undefined | null
  >(null);

  console.log(selected);
  function handleTextChange(
    field: keyof EditedBuildingModel,
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement
    >
  ) {
    const temp = _.cloneDeep(selected);
    if (temp && field in temp) {
      temp[field] = event.target.value as any;
      setSelected(temp);
    }
  }

  function handleAlterArray(
    handle: string,
    field: keyof EditedBuildingModel,
    incoming: any,
    index: number = 0
  ) {
    const temp = _.cloneDeep(selected);
    if (!temp?.[field]) return;
    switch (field) {
      case "building_proximity":
        if (handle === "change")
          temp[field][index] = incoming;
        else if (handle === "push")
          temp[field].push(incoming);
        break;
      case "building_facility":
        if (handle === "change")
          temp[field][index] = incoming;
        else if (handle === "push")
          temp[field].push(incoming);
        break;
      default:
        break;
    }

    setSelected(temp);
  }

  function handleNumberChange(
    field: keyof EditedBuildingModel,
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    if (event.target.value === "") event.target.value = "0";

    const temp = _.cloneDeep(selected);
    if (temp && field in temp) {
      event.target.value = event.target.value
        .split(".")
        .join("");

      temp[field] = event.target.value as any;
      setSelected(temp);
    }
  }

  const handleNextItem = () => {
    const dataCount = data?.data.length ?? -1;
    if (dataCount <= 0) return;
    if (typeof selected?.index === "undefined") return;
    if (selected?.index >= dataCount) return;
    handleSaveData();
    handleSelectedItem(selected?.index + 1);
  };

  const handlePrevItem = () => {
    if (typeof selected?.index === "undefined") return;
    if (selected?.index <= 0) return;
    handleSaveData();
    handleSelectedItem(selected?.index - 1);
  };

  const handleSaveData = () => {
    const temp = _.cloneDeep(data);
    if (!selected) return;
    if (typeof selected?.index === "undefined") return;
    if (!temp) return;

    temp.data[selected?.index] = {
      ...selected,
    };

    setData(temp);
  };

  const handleDeleteData = (index: number | undefined) => {
    if (!index) return;
    const temp = _.cloneDeep(data);
    temp?.data.splice(index, 1);
    setData(temp);
    handleSelectedItem(index, true);
  };

  const handleSelectedItem = (
    index: number,
    fromDelete: boolean = false
  ) => {
    try {
      const defaultValue = {
        ...HomeDefaultValue,
      };
      const temp: EditedBuildingModel | undefined | null =
        _.cloneDeep(
          data?.data[fromDelete ? index + 1 : index]
        );

      setSelected({
        ...defaultValue,
        ...temp,
        index: index,
      });
    } catch (error) {
      console.log(error);
    }
  };

  const handleFileUpload = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setIsLoading(true);
    try {
      const file = event.target.files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const result = e.target?.result as string;
          setData(JSON.parse(result));
          setIsLoading(false);
        };
        reader.readAsText(file);
      }
    } catch (error) {
      alert(error as string);
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    saveAs(blob, "modifiedData.json");
  };

  const handleKeyPress = (event: KeyboardEvent) => {
    // Check if the Enter key is pressed and the target is not an input, textarea, or select element
    const target = event.target as Element;
    const targetTag = target.tagName.toLowerCase();
    if (
      event.key === "Enter" &&
      targetTag !== "input" &&
      targetTag !== "textarea" &&
      targetTag !== "select"
    ) {
      handleSaveData();
    }
  };

  useEffect(() => {
    // Add event listener when component mounts
    window.addEventListener("keydown", handleKeyPress);

    // Clean up the event listener when component unmounts
    return () => {
      window.removeEventListener("keydown", handleKeyPress);
    };
  }, [selected]);

  return (
    <Fragment>
      <Modal toggle={isLoading}>...Loading bentar</Modal>
      <div className="home-page">
        <div className="visible home-page-container">
          <div className="home-page-wrapper home-page-left">
            <div className="home-page-flex-container">
              <div className="home-page-body-container">
                <div className="home-page-body-header-container">
                  <div className="home-page-body-header-left">
                    <h4>
                      Edit File - Masukkan file dengan
                      extensi .json
                    </h4>
                  </div>
                  <div className="home-page-body-header-right">
                    <input
                      placeholder="Upload"
                      title="Upload"
                      type="file"
                      accept=".json"
                      onChange={handleFileUpload}
                    />
                  </div>
                </div>
                <div
                  ref={chatBodyContainerRef}
                  className="home-page-mainbody-container home-page-chatbody-container dark-bg-color">
                  <div className="home-page-mainbody-wrapper">
                    <div className="home-page-chat-cards-container">
                      <ShowGrabableStoreCardCarousel
                        uniqueKey={"building-card"}
                        values={data}
                        selectedIndex={selected?.index}
                        handleSelectedItem={
                          handleSelectedItem
                        }
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="home-page-wrapper home-page-right">
            <div className="home-page-flex-container">
              <div className="home-page-body-container">
                <div className="home-page-body-header-container">
                  <div className="home-page-body-header-left">
                    <h4>
                      {typeof selected?.index !==
                      "undefined"
                        ? `Property No. ${
                            selected?.index + 1
                          }`
                        : "No Selected"}
                    </h4>
                  </div>
                  <div
                    onClick={() =>
                      handleDeleteData(selected?.index)
                    }
                    className="home-page-body-header-right cursor-pointer">
                    <span className="red-color">
                      Delete
                    </span>
                  </div>
                </div>
                <div
                  ref={chatBodyContainerRef}
                  className="home-page-mainbody-container home-page-chatbody-container dark-bg-color">
                  <div className="home-page-mainbody-wrapper">
                    <label className="margin-top-16">
                      Title
                    </label>
                    <div className="home-page-textinput-box">
                      <TextInput
                        onChange={(e) =>
                          handleTextChange(
                            "building_title",
                            e
                          )
                        }
                        value={selected?.building_title}
                        type="text"
                        className="home-page-textinput darker-bg-color"
                      />
                    </div>
                    <label className="margin-top-16">
                      Alamat
                    </label>
                    <div className="home-page-textinput-box">
                      <TextInput
                        onChange={(e) =>
                          handleTextChange(
                            "building_address",
                            e
                          )
                        }
                        value={selected?.building_address}
                        type="text"
                        className="home-page-textinput darker-bg-color"
                      />
                    </div>
                    <label className="margin-top-16">
                      Harga (Rp.)
                    </label>
                    <div className="home-page-textinput-box">
                      <TextInput
                        onChange={(e) =>
                          handleNumberChange(
                            "housing_price",
                            e
                          )
                        }
                        value={formattedNumber(
                          selected?.housing_price ?? "0"
                        )}
                        type="text"
                        className="home-page-textinput darker-bg-color"
                      />
                    </div>
                    <label className="margin-top-16">
                      Pemilik
                    </label>
                    <div className="home-page-textinput-box">
                      <TextInput
                        onChange={(e) =>
                          handleTextChange("owner_name", e)
                        }
                        value={selected?.owner_name}
                        type="text"
                        className="home-page-textinput darker-bg-color"
                      />
                    </div>
                    <label className="margin-top-16">
                      Whatsapp Pemilik
                    </label>
                    <div className="home-page-textinput-box">
                      <TextInput
                        onChange={(e) =>
                          handleTextChange(
                            "owner_whatsapp",
                            e
                          )
                        }
                        value={selected?.owner_whatsapp}
                        type="text"
                        className="home-page-textinput darker-bg-color"
                      />
                    </div>
                    <label className="margin-top-16">
                      Nomor Telepon Pemilik
                    </label>
                    <div className="home-page-textinput-box">
                      <TextInput
                        onChange={(e) =>
                          handleTextChange(
                            "owner_phone_number",
                            e
                          )
                        }
                        value={selected?.owner_phone_number}
                        type="text"
                        className="home-page-textinput darker-bg-color"
                      />
                    </div>
                    <label className="margin-top-16">
                      Email Pemilik
                    </label>
                    <div className="home-page-textinput-box">
                      <TextInput
                        onChange={(e) =>
                          handleTextChange("owner_email", e)
                        }
                        value={selected?.owner_email}
                        type="text"
                        className="home-page-textinput darker-bg-color"
                      />
                    </div>
                    <div className="home-page-textinput-box">
                      <label className="home-page-input-title">
                        Lingkungan Sekitar
                      </label>
                      <TextArea
                        onChange={(e) =>
                          handleTextChange(
                            "building_proximity_string",
                            e
                          )
                        }
                        className="home-page-longtext-area darker-bg-color"
                        value={
                          selected?.building_proximity_string
                        }
                      />
                    </div>
                    <div className="home-page-textinput-box">
                      <label className="home-page-input-title">
                        Fasilitas
                      </label>
                      <TextArea
                        onChange={(e) =>
                          handleTextChange(
                            "building_facility_string",
                            e
                          )
                        }
                        className="home-page-longtext-area darker-bg-color"
                        value={
                          selected?.building_facility_string
                        }
                      />
                    </div>
                    <div className="home-page-textinput-box home-page-flex-column margin-top-0">
                      {selected?.building_proximity?.map(
                        (value, index) => (
                          <div
                            key={`home-page-building-proximity-${index}`}
                            className="home-page-textinput-box">
                            <label className="home-page-input-title">
                              Proximity Chunk {index + 1}
                            </label>
                            <TextInput
                              onChange={(e) =>
                                handleAlterArray(
                                  "change",
                                  "building_proximity",
                                  index,
                                  e.target.value as any
                                )
                              }
                              value={value}
                              type="text"
                              className="home-page-textinput margin-top-bottom-8 darker-bg-color"
                            />
                          </div>
                        )
                      )}
                      <Button
                        onClick={() =>
                          handleAlterArray(
                            "push",
                            "building_proximity",
                            "New input"
                          )
                        }
                        className="margin-top-16 align-self-start home-page-button main-bg-color">
                        <label className="home-page-button-text">
                          {selected?.building_proximity &&
                          selected?.building_proximity
                            .length > 0
                            ? "+"
                            : "Add proximity chunks"}
                        </label>
                      </Button>
                    </div>
                    <div className="home-page-textinput-box home-page-flex-column margin-top-0">
                      {selected?.building_facility?.map(
                        (value, index) => (
                          <div
                            key={`home-page-building-facility-${index}`}
                            className="home-page-textinput-box">
                            <label className="home-page-input-title">
                              Facility Chunk {index + 1}
                            </label>
                            <TextInput
                              onChange={(e) =>
                                handleAlterArray(
                                  "change",
                                  "building_facility",
                                  index,
                                  e.target.value as any
                                )
                              }
                              value={value}
                              type="text"
                              className="home-page-textinput margin-top-bottom-8 darker-bg-color"
                            />
                          </div>
                        )
                      )}
                      <Button
                        onClick={() =>
                          handleAlterArray(
                            "push",
                            "building_facility",
                            "New input"
                          )
                        }
                        className="margin-top-16 align-self-start home-page-button main-bg-color">
                        <label className="home-page-button-text">
                          {selected?.building_facility &&
                          selected?.building_facility
                            .length > 0
                            ? "+"
                            : "Add facility chunks"}
                        </label>
                      </Button>
                    </div>
                    <div className="home-page-textinput-box">
                      <label className="home-page-input-title">
                        Deskripsi
                      </label>
                      <TextArea
                        onChange={(e) =>
                          handleTextChange(
                            "building_description",
                            e
                          )
                        }
                        className="home-page-longtext-area darker-bg-color"
                        value={
                          selected?.building_description
                        }
                      />
                    </div>
                  </div>
                </div>
                <div className="home-page-chat-container dark-bg-color">
                  <div className="home-page-chat-container-left">
                    <Button
                      className="margin-top-16 transparent-bg-color"
                      onClick={handlePrevItem}>
                      prev
                    </Button>
                    <Button
                      className="margin-top-16 transparent-bg-color"
                      onClick={handleNextItem}>
                      next
                    </Button>
                  </div>
                  <Button
                    className="margin-top-16"
                    onClick={handleSaveData}>
                    save
                  </Button>
                </div>
                <div className="home-page-footer-container transparent-bg-color">
                  <Button
                    className="margin-top-16"
                    onClick={handleDownload}>
                    download
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Fragment>
  );
}
