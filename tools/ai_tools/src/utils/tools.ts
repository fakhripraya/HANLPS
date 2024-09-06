import chalk from "chalk";
import { promises as fs } from "fs";
import {
  BuildingModel,
  MasterModel,
} from "../domain/models";
import { GoogleGenerativeAI } from "@google/generative-ai";
import inputJson from "../input_json/input.json" assert { type: "json" };

const delay = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

export const removeSpecificFromString =
  async (): Promise<void> => {
    let masterData: MasterModel = inputJson as MasterModel;
    try {
      console.log(chalk.green("Start the removal loop"));
      console.log(
        chalk.green(`Lenght: ${masterData.data.length}`)
      );
      for (
        let index = 0;
        index < masterData.data.length;
        index++
      ) {
        const temp_val = { ...masterData.data[index] };
        if (temp_val) {
          console.log(
            chalk.green(`[${index + 1}]: Removing...`)
          );
          const temp = await customAIPrompt(
            index,
            temp_val.building_description,
            `
              I want you to make the same description as the information, 
              the difference is the description i want is without the contact person or CP,
              like without whatsapp or phone number.
              
              return only the string, don't add anything irrelevant
            `
          );

          masterData.data[index].building_description =
            temp;
        } else {
          console.log(
            chalk.red(
              `Error on index: ${index + 1}, data not found`
            )
          );
        }
      }
    } catch (error) {
      console.log(chalk.red(error as string));
    } finally {
      await fs.writeFile(
        "src/output_json/ai_updated.json",
        JSON.stringify(masterData, null, 2)
      );

      console.log(
        chalk.green(
          "Successfully added index to JSON data and saved as ai_updated.json"
        )
      );
    }
  };

export const generativeLoopThroughArray =
  async (): Promise<void> => {
    let masterData: MasterModel = inputJson as MasterModel;
    const sliced: BuildingModel[] = [];
    try {
      console.log(chalk.green("Start the generative loop"));
      for (
        let index = 0;
        index < masterData.data.length;
        index++
      ) {
        const temp_val = { ...masterData.data[index] };
        const synced = await syncData(temp_val);
        if (synced) {
          temp_val.building_address =
            synced?.building_address;
          temp_val.building_description =
            synced?.building_description;
          temp_val.building_facility =
            synced?.building_facility;
          temp_val.building_proximity =
            synced?.building_proximity;
          temp_val.building_description =
            synced?.building_description;
          temp_val.housing_price = synced?.housing_price;
          temp_val.owner_whatsapp = synced?.owner_whatsapp;
          temp_val.owner_phone_number =
            synced?.owner_phone_number;
          temp_val.owner_email = synced?.owner_email;
          sliced.push(synced ?? temp_val);
          console.log(
            chalk.green(`Producing item no: ${index + 1}`)
          );
        } else {
          console.log(
            chalk.red(
              `Error on index: ${index + 1}, data not found`
            )
          );
        }
      }
    } catch (error) {
      console.log(chalk.red(error as string));
    } finally {
      masterData.data = sliced;
      await fs.writeFile(
        "src/output_json/ai_updated.json",
        JSON.stringify(masterData, null, 2)
      );

      console.log(
        chalk.green(
          "Successfully added index to JSON data and saved as ai_updated.json"
        )
      );
    }
  };

export const syncData = async (
  building: BuildingModel
): Promise<BuildingModel | undefined> => {
  if (!building.building_description) return;

  const genAI = new GoogleGenerativeAI(
    process.env.GEMINI_API_KEY ?? ""
  );
  const model = genAI.getGenerativeModel({
    model: process.env.GEMINI_MODEL ?? "",
  });

  const prompt = `
    I have an Information about a boarding house building.

    The information:
    ${building.building_description}

    Determine:
    1. building_title: the title of the building as string default empty string
    2. building_address: the address of the building, don't include any symbol. The value must be as string with default value of empty string
    3. building_proximity: the building list of nearest landmark and area including where the building area is as string default empty string
    4. building_facility: the building facility as string default empty string
    5. building_description: the whole information above but enhanced without symbol but keep the newline, to ease reading and vector searching as string default empty string
    6. housing_price: the cheapest price per month in Rupiah without decimal as number
    7. owner_whatsapp: the number of the contact person or CP, if applicable as string default empty string
    8. owner_phone_number: same number as owner_whatsapp as string default empty string
    9. owner_email: the email of the contact person or CP, if applicable as string default empty string
    
    Reply in JSON format
  `;

  try {
    const result = await model.generateContent([prompt]);
    const json_obj = result.response.text();

    let cleanJson = "";
    cleanJson = json_obj.replace(/```json|```/g, "").trim();
    const parsed = JSON.parse(cleanJson);

    const new_building: BuildingModel = { ...building };
    new_building.building_title = parsed["building_title"];
    new_building.building_address =
      parsed["building_address"];
    new_building.building_proximity =
      parsed["building_proximity"];
    new_building.building_facility =
      parsed["building_facility"];
    new_building.building_description =
      parsed["building_description"];
    new_building.housing_price = parsed["housing_price"];
    new_building.owner_whatsapp = parsed["owner_whatsapp"];
    new_building.owner_phone_number =
      parsed["owner_phone_number"];
    new_building.owner_email = parsed["owner_email"];

    return new_building;
  } catch (error) {
    console.log(
      chalk.red(
        `Error when generating building on index: ${building.index}. Skipping...`
      )
    );
    console.log(chalk.red(error as string));
    return;
  }
};

export const customAIPrompt = async (
  index: number,
  field: any,
  command: string
): Promise<string | undefined> => {
  if (!field) return;

  const genAI = new GoogleGenerativeAI(
    process.env.GEMINI_API_KEY ?? ""
  );
  const model = genAI.getGenerativeModel({
    model: process.env.GEMINI_MODEL ?? "",
  });

  const prompt = `
    I have an information and a command that will alter the field value based on it.

    The information:
    ${field}

    The Command:
    ${command}

    return the processed field in string format
  `;

  try {
    const result = await model.generateContent([prompt]);
    const json_obj = result.response.text();
    await delay(5000);

    return json_obj;
  } catch (error: any) {
    console.log(
      chalk.red(
        `Error removal on index: ${index} caused by ${error}, Skipping...`
      )
    );
  }
};
