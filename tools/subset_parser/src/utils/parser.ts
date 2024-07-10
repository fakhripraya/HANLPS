import axios from "axios";
import chalk from "chalk";
import { promises as fs } from "fs";
import {
  BuildingModel,
  ItemModel,
  MasterModel,
} from "../domain/models";

const getData = async (
  paginationToken?: string
): Promise<MasterModel> => {
  const token =
    paginationToken ||
    "HE0zBBwpShYYZQpSAF0DQQFLB0dVR0FDSlkQbBRVPE0GWRNBF24MWUhBXkNRHA8JMB0tHxtQFX1JM2UtHiEUIAIPAxYWGAIiBwpNICgRBycMNkhnOzVdIwgnBT4yPQZUBzMsDjs3Sh1QJCofEzQdNTASBSAKHkcdRydQQz4BFQAHBAUsB1BNVUBGUUYYVi1ZC2smLQdAHFd9V1BcX14MQRZVCmoRQQJKBlszDFsnEQAcCA";

  const res = await axios.get(
    `https://instagram-scraper-api2.p.rapidapi.com/v1.2/posts?username_or_id_or_url=jktinfokost&pagination_token=${token}&url_embed_safe=true`,
    {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "x-rapidapi-ua": "RapidAPI-Playground",
        "x-rapidapi-key":
          "952c971aa2mshea4a8b7b9207039p123f06jsn2a3c1f1ae79b",
        "x-rapidapi-host":
          "instagram-scraper-api2.p.rapidapi.com",
      },
    }
  );

  if (res.status !== 200) throw new Error("Stopper");

  return res.data as MasterModel;
};

const getFix = async (
  howManyTimes = 10
): Promise<BuildingModel[]> => {
  let fixData: BuildingModel[] = [];
  let token: string | undefined;

  for (let i = 1; i <= howManyTimes; i++) {
    const data = await getData(token);
    token = data.paginationToken;

    fixData = [
      ...fixData,
      ...data.data.items.map((e: ItemModel) => {
        return {
          building_description: e.caption.text,
          image_urls: e.carousel_media.map(
            (f) => f.thumbnail_url
          ),
        } as BuildingModel;
      }),
    ];

    console.log(`producing ${i}`);
  }

  return fixData;
};

const mapperToJson = async (
  howMany: number
): Promise<void> => {
  try {
    const fix = await getFix(howMany);
    const jsonList = fix.map((e) =>
      JSON.parse(JSON.stringify(e))
    );
    const jsonString = JSON.stringify(
      { data: jsonList },
      null,
      2
    );
    await fs.writeFile("output.json", jsonString);
    console.log(
      chalk.green(
        "Data successfully converted to JSON and saved in output.json"
      )
    );
  } catch (error) {
    console.log(chalk.red(error as string));
  }
};

export { mapperToJson };
