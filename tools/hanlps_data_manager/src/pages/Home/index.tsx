/* eslint-disable @typescript-eslint/no-explicit-any */
import "./style.scss";
import { useRef, useState } from "react";
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

export default function Home() {
  // REFS //
  const chatBodyContainerRef =
    useRef<HTMLInputElement>(null);

  const [data, setData] = useState<MasterData | null>(null);
  const [page, setPage] = useState<number>(0);
  const [selected, setSelected] = useState<
    EditedBuildingModel | undefined | null
  >(null);

  function handleTextChange(
    field: keyof EditedBuildingModel,
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement
    >
  ) {
    const temp: EditedBuildingModel = { ...selected };
    if (field in temp) {
      temp[field] = event.target.value as any;
      setSelected(temp);
    }
  }

  const handleSaveData = () => {
    return;
  };

  const handleDeleteData = (index: number | undefined) => {
    if (!index) return;
    const temp = _.cloneDeep(data);
    temp?.data.splice(index, 1);
    setData(temp);
    handleSelectedItem(index + 1);
  };

  const handleSelectedItem = (index: number) => {
    const temp: EditedBuildingModel | undefined | null =
      data?.data[index];
    setSelected({
      index: index,
      ...temp,
    });
  };

  const handleFileUpload = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setData(JSON.parse(result));
      };
      reader.readAsText(file);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    saveAs(blob, "modifiedData.json");
  };

  return (
    <div className="home-page">
      <div className="visible home-page-container">
        <div className="home-page-wrapper home-page-left">
          <div className="home-page-flex-container">
            <div className="home-page-body-container">
              <div className="home-page-body-header-container">
                <div className="home-page-body-header-left">
                  <h4>
                    Edit File - Masukkan file dengan extensi
                    .json
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
                    Property No.{" "}
                    {selected?.index
                      ? selected?.index + 1
                      : 0}
                  </h4>
                </div>
                <div
                  onClick={() =>
                    handleDeleteData(selected?.index)
                  }
                  className="home-page-body-header-right cursor-pointer">
                  <span className="red-color">Delete</span>
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
                    Harga
                  </label>
                  <div className="home-page-textinput-box">
                    <TextInput
                      onChange={(e) =>
                        handleTextChange("housing_price", e)
                      }
                      value={selected?.housing_price}
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
                      value={selected?.building_description}
                    />
                  </div>
                </div>
              </div>
              <div className="home-page-chat-container dark-bg-color">
                <div className="home-page-chat-container-left">
                  <Button
                    className="margin-top-16 transparent-bg-color"
                    onClick={() => {
                      if (page === 0) return;
                      setPage(page - 1);
                    }}>
                    prev
                  </Button>
                  <Button
                    className="margin-top-16 transparent-bg-color"
                    onClick={() => {
                      if (page === data?.data?.length)
                        return;
                      setPage(page + 1);
                    }}>
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
  );
}
