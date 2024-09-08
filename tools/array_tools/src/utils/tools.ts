import chalk from "chalk";
import { promises as fs } from "fs";
import {
  BuildingModel,
  MasterModel,
} from "../domain/models";
import inputJson from "../input_json/input.json" assert { type: "json" };

const sliceImageURLElements = async (
  start: number,
  end?: number
): Promise<void> => {
  try {
    let masterData: MasterModel = inputJson as MasterModel;
    const sliced: BuildingModel[] = masterData.data.map(
      (val) => {
        let new_val = { ...val };
        if (new_val.image_urls)
          new_val.image_urls = new_val.image_urls.slice(
            start,
            end
          );

        return new_val;
      }
    );

    masterData.data = sliced;
    await fs.writeFile(
      "src/output_json/sliced.json",
      JSON.stringify(masterData, null, 2)
    );
    console.log(
      chalk.green(
        "Data successfully converted to JSON and saved as sliced.json"
      )
    );
  } catch (error) {
    console.log(chalk.red(error as string));
  }
};

const migrateKey = async (): Promise<void> => {
  try {
    let masterData: MasterModel = inputJson as MasterModel;
    const migrated: BuildingModel[] = masterData.data.map(
      (val, index) => {
        let new_val = { ...val };
        if (new_val)
          new_val = {
            index: index,
            building_title: new_val.building_title ?? "",
            building_address:
              new_val.building_address ?? "",
            building_facility:
              new_val.building_facility ?? [],
            building_proximity:
              new_val.building_proximity ?? [],
            building_description:
              new_val.building_description ?? "",
            housing_price: new_val.housing_price ?? "",
            owner_name: new_val.owner_name ?? "",
            owner_whatsapp: new_val.owner_whatsapp ?? "",
            owner_phone_number:
              new_val.owner_phone_number ?? "",
            owner_email: new_val.owner_email ?? "",
            image_urls: new_val.image_urls ?? [],
            isReady: new_val.isReady ?? false,
          };
        return new_val;
      }
    );

    masterData.data = migrated;
    await fs.writeFile(
      "src/output_json/migrated.json",
      JSON.stringify(masterData, null, 2)
    );
    console.log(
      chalk.green(
        "Successfully migrated new keys to JSON data and saved as migrated.json"
      )
    );
  } catch (error) {
    console.log(chalk.red(error as string));
  }
};

export { sliceImageURLElements, migrateKey };
