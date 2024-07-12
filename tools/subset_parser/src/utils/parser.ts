import axios, { AxiosError } from "axios";
import chalk from "chalk";
import { promises as fs } from "fs";
import {
  BuildingModel,
  ItemModel,
  MasterModel,
} from "../domain/models";

const getData = async (
  paginationToken?: string
): Promise<MasterModel | undefined> => {
  let data: MasterModel | undefined = undefined;
  try {
    console.log(chalk.green("Fetch data"));
    const token =
      paginationToken ||
      "HE0zBBwpShYYZQpSAFQDQwFDB0VVQkFBSlQQZhRUPE0GWRNBF24MWUhBXkNRHA8JMB0tHxtQFX1JM2U3HiMUEgIlA0EWFAIiByZNUigePickIVNmLjUvMT02FRAxMixcEysCLDsxSh1QNCohEykdNjA-BQYKHkdCRyNQQz4BFQAHBAUsB1BNVUBGUUYYVi1ZC2smLQdAHFZ9XVBSX1wMRxZWCmoRRgJKBlszDFsnEQAcCA";

    const res = await axios.get(
      `https://instagram-scraper-api2.p.rapidapi.com/v1.2/posts?username_or_id_or_url=jktinfokost&pagination_token=${token}&url_embed_safe=true`,
      {
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "x-rapidapi-ua": "RapidAPI-Playground",
          "x-rapidapi-key":
            "5bed0ca8e2mshfdf387ce894f6f7p1cb5f9jsnb1fcb6b25091",
          "x-rapidapi-host":
            "instagram-scraper-api2.p.rapidapi.com",
        },
      }
    );

    console.log(chalk.green("Fetch data done"));
    data = res.data;
    return data;
  } catch (error: any) {
    if (error.response) {
      console.error(
        chalk.red(
          `Error: ${error.response.status} - ${error.response.statusText}`
        )
      );
      console.error(chalk.red(error.response.data));
    } else if (error.request) {
      console.error(
        chalk.red("Error: No response received from server")
      );
      console.error(chalk.red(error.request));
    } else {
      console.error(chalk.red("Error:", error.message));
    }
    console.error(chalk.red("Error config:", error.config));
  }
};

const getFix = async (
  howManyTimes = 10
): Promise<BuildingModel[]> => {
  let fixData: BuildingModel[] = [];
  let token: string | undefined;

  console.log(chalk.green("Start loop on getFix"));
  for (let i = 1; i <= howManyTimes; i++) {
    const data = await getData(token);
    if (!data) continue;

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
    console.log(chalk.green("Get fix object"));
    const fix = await getFix(howMany);
    console.log(chalk.green("Get fix object done"));
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
