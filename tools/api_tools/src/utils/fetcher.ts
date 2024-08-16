import axios, { AxiosError } from "axios";
import chalk from "chalk";
import { promises as fs } from "fs";
import {
  BuildingModel,
  ItemModel,
  MasterModel,
} from "../domain/models";

const getData = async (
  index: number,
  paginationToken?: string | undefined
): Promise<MasterModel | undefined> => {
  let data: MasterModel | undefined = undefined;
  try {
    console.log(chalk.green(`[${index}]: Fetch data`));
    console.log(
      chalk.green(`[${index}]: Token ${paginationToken}`)
    );
    const token = paginationToken
      ? `&pagination_token=${paginationToken}`
      : "";

    const res = await axios.get(
      `https://instagram-scraper-api2.p.rapidapi.com/v1.2/posts?username_or_id_or_url=jktinfokost${token}&url_embed_safe=true`,
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

    console.log(chalk.green(`[${index}]: Fetch data done`));
    return res.data ?? data;
  } catch (error: any) {
    if (error.response) {
      console.error(
        chalk.red(
          `[Error at index ${index}]: ${error.response.status} - ${error.response.statusText}`
        )
      );
      console.error(chalk.red(error.response.data));
    } else if (error.request) {
      console.error(
        chalk.red(
          `[Error at index ${index}]: No response received from server with request: \n ${error.request}`
        )
      );
    } else {
      console.error(
        chalk.red(
          `[Error at index ${index}]: ${error.message}`
        )
      );
    }
    console.error(
      chalk.red(
        `[Error config at index ${index}]: ${error.config}`
      )
    );
    return undefined;
  }
};

const getDataAndMap = async (
  size: number = 10
): Promise<BuildingModel[]> => {
  let fixData: BuildingModel[] = [];
  let token: string | undefined = undefined;

  console.log(chalk.green("Start fetching datas..."));
  for (let i = 1; i <= size; i++) {
    const object: MasterModel | undefined = await getData(
      i,
      token
    );
    if (!object) continue;

    console.log(object.pagination_token);
    console.log(object.data ? true : false);
    token = object.pagination_token;
    fixData = [
      ...fixData,
      ...object.data.items.map((e: ItemModel) => {
        return {
          building_description: e.caption.text,
          image_urls: e.carousel_media?.map(
            (f) => f.thumbnail_url
          ),
        } as BuildingModel;
      }),
    ];

    console.log(`producing ${i}`);
  }

  console.log(chalk.green("Successfully fetched datas"));
  return fixData;
};

const fetchDataFromAPI = async (
  size: number
): Promise<void> => {
  try {
    const fix = await getDataAndMap(size);
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
        "Data successfully converted to JSON and saved as output.json"
      )
    );
  } catch (error) {
    console.log(chalk.red(error as string));
  }
};

export { fetchDataFromAPI };
