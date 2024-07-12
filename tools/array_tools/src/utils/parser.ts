import chalk from "chalk";
import { promises as fs } from "fs";
import { MasterModel } from "../domain/models";
import inputJson from "../../input_json/input.json";

const cleanFirst = async (): Promise<void> => {
  try {
    const masterData: MasterModel = JSON.parse(
      inputJson.toString()
    );
    await fs.writeFile("cutted.json", jsonString);
    console.log(
      chalk.green(
        "Data successfully converted to JSON and saved in output.json"
      )
    );
  } catch (error) {
    console.log(chalk.red(error as string));
  }
};

export { cleanFirst };
