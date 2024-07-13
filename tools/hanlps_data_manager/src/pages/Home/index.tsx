/* eslint-disable @typescript-eslint/no-explicit-any */
import "./style.scss";
import { useEffect, useRef, useState } from "react";
import Button from "../../components/Button";
import { MasterData } from "../../interfaces/building";
import TextArea from "../../components/TextArea";
import TextInput from "../../components/TextInput";

export default function Home() {
  // REFS //
  const chatBodyContainerRef =
    useRef<HTMLInputElement>(null);

  const [data, setData] = useState<MasterData | null>(null);
  const [page, setPage] = useState<number>(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("/json/data.json");
        const jsonData: MasterData = await response.json();
        console.log(jsonData);
        setData(jsonData);
      } catch (error) {
        console.error(
          "Error fetching the JSON data:",
          error
        );
      }
    };

    fetchData();
  }, []);

  return (
    <div className="home-page">
      <div className="visible home-page-container">
        <div className="home-page-wrapper">
          <div className="home-page-flex-container">
            <div className="home-page-body-container">
              <div className="home-page-body-header-container">
                <div className="home-page-body-header-left">
                  <h4>Edit</h4>
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
                      value={
                        data?.data?.[page].building_title
                      }
                      type="text"
                      className="home-page-textinput darker-bg-color"
                    />
                  </div>
                  <label className="margin-top-16">
                    Alamat
                  </label>
                  <div className="home-page-textinput-box">
                    <TextInput
                      value={
                        data?.data?.[page].building_address
                      }
                      type="text"
                      className="home-page-textinput darker-bg-color"
                    />
                  </div>
                  <label className="margin-top-16">
                    Harga
                  </label>
                  <div className="home-page-textinput-box">
                    <TextInput
                      value={
                        data?.data?.[page].housing_price
                      }
                      type="text"
                      className="home-page-textinput darker-bg-color"
                    />
                  </div>
                  <label className="margin-top-16">
                    Pemilik
                  </label>
                  <div className="home-page-textinput-box">
                    <TextInput
                      value={data?.data?.[page].owner_name}
                      type="text"
                      className="home-page-textinput darker-bg-color"
                    />
                  </div>
                  <label className="margin-top-16">
                    Whatsapp Pemilik
                  </label>
                  <div className="home-page-textinput-box">
                    <TextInput
                      value={
                        data?.data?.[page].owner_whatsapp
                      }
                      type="text"
                      className="home-page-textinput darker-bg-color"
                    />
                  </div>
                  <label className="margin-top-16">
                    Nomor Telepon Pemilik
                  </label>
                  <div className="home-page-textinput-box">
                    <TextInput
                      value={
                        data?.data?.[page]
                          .owner_phone_number
                      }
                      type="text"
                      className="home-page-textinput darker-bg-color"
                    />
                  </div>
                  <label className="margin-top-16">
                    Email Pemilik
                  </label>
                  <div className="home-page-textinput-box">
                    <TextInput
                      value={
                        data?.data?.[page]
                          .owner_phone_number
                      }
                      type="text"
                      className="home-page-textinput darker-bg-color"
                    />
                  </div>
                  <div className="home-page-textinput-box">
                    <label className="home-page-input-title">
                      Deskripsi
                    </label>
                    <TextArea
                      className="home-page-longtext-area darker-bg-color"
                      value={
                        data?.data?.[page]
                          .building_description
                      }
                    />
                  </div>
                </div>
              </div>
              <div className="home-page-chat-container dark-bg-color">
                <Button
                  className="margin-top-16 transparent-bg-color"
                  onClick={() => {
                    if (page === data?.data?.length) return;
                    setPage(page + 1);
                  }}>
                  next
                </Button>
                <Button
                  className="margin-top-16 transparent-bg-color"
                  onClick={() => {
                    if (page === 0) return;
                    setPage(page - 1);
                  }}>
                  prev
                </Button>
                <Button
                  className="margin-top-16"
                  onClick={() => {}}>
                  save
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
