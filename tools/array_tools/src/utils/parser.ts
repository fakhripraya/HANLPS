import chalk from "chalk";
import { promises as fs } from "fs";
import {
  BuildingModel,
  MasterModel,
} from "../domain/models";
import inputJson from "../input_json/input.json" assert { type: "json" };

const shiftArray = async (): Promise<void> => {
  try {
    let masterData: MasterModel = inputJson as MasterModel;
    const sliced: BuildingModel[] = masterData.data.map(
      (val) => {
        let new_val = { ...val };
        if (new_val.image_urls) {
          new_val.image_urls = new_val.image_urls.slice(1);
        }
        return new_val;
      }
    );

    masterData.data = sliced;
    await fs.writeFile(
      "src/output_json/cutted.json",
      JSON.stringify(masterData, null, 2)
    );
    console.log(
      chalk.green(
        "Data successfully converted to JSON and saved in output.json"
      )
    );
  } catch (error) {
    console.log(chalk.red(error as string));
  }
};

const addIsReady = async (): Promise<void> => {
  try {
    let masterData: MasterModel = inputJson as MasterModel;
    const sliced: BuildingModel[] = masterData.data.map(
      (val) => {
        let new_val = { ...val };
        if (new_val) new_val.isReady = false;
        return new_val;
      }
    );

    masterData.data = sliced;
    await fs.writeFile(
      "src/output_json/cutted.json",
      JSON.stringify(masterData, null, 2)
    );
    console.log(
      chalk.green(
        "Successfully added isReady to JSON data and saved in output.json"
      )
    );
  } catch (error) {
    console.log(chalk.red(error as string));
  }
};

const addIndex = async (): Promise<void> => {
  try {
    let masterData: MasterModel = inputJson as MasterModel;
    const sliced: BuildingModel[] = masterData.data.map(
      (val, index) => {
        let new_val = { ...val };
        if (new_val) new_val.index = index;
        return new_val;
      }
    );

    masterData.data = sliced;
    await fs.writeFile(
      "src/output_json/cutted.json",
      JSON.stringify(masterData, null, 2)
    );
    console.log(
      chalk.green(
        "Successfully added index to JSON data and saved in output.json"
      )
    );
  } catch (error) {
    console.log(chalk.red(error as string));
  }
};

export { shiftArray, addIsReady, addIndex };
