import React, { Fragment } from "react";
import Card from "../../../components/Card";
import { MasterData } from "../../../interfaces/building";
import { formattedNumber } from "../../../utils/functions/global";

interface ShowGrabableStoreCardCarouselProps {
  uniqueKey: string;
  values?: MasterData | null;
  handleSelectedItem: (index: number) => void;
}

export const ShowGrabableStoreCardCarousel: React.FC<
  ShowGrabableStoreCardCarouselProps
> = (props) => (
  <Fragment>
    {props.values?.data?.map((obj, index) => (
      <Card
        onClick={() => props.handleSelectedItem(index)}
        key={`carousel-card-${props.uniqueKey}-${index}`}>
        <img
          className="card-img"
          src={obj.image_urls?.[0]}
          alt={obj.image_urls?.[0]}
        />
        <div className="breakline" />
        <div className="breakline" />
        <h3 className="light-color">
          {obj?.building_title}
        </h3>
        <p className="margin-bottom-0 light-color">
          Properti No. {index + 1}
        </p>
        <p className="margin-bottom-0 light-color">
          Rp.{" "}
          {formattedNumber(
            parseFloat(
              obj?.housing_price ? obj?.housing_price : "0"
            )
          )}
        </p>
        <p className="light-color">
          {obj?.building_address}
        </p>
        <p className="light-color">
          {obj?.building_description}
        </p>
      </Card>
    ))}
  </Fragment>
);
