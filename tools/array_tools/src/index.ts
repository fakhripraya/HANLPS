#!/usr/bin/env node

import {
  sliceImageURLElements,
  migrateKey,
} from "./utils/tools.js";

// Add this to your index.ts
import * as commander from "commander";

const program = new commander.Command();
program
  .version("1.0.0")
  .description("Array tools for HANLPS");

// Define your commands and flags here
program
  .command("slice")
  .description(
    "Slice the array of elements in the data based on start and end"
  )
  .option(
    "--images",
    "Slice the image urls from each element data"
  )
  .action(async (_, options) => {
    if (options.images)
      await sliceImageURLElements(1, undefined);
  });

program
  .command("migrate")
  .description(
    "Migrate key based on the new BuildingModel to the whole element"
  )
  .action(async () => {
    await migrateKey();
  });

program.parse(process.argv);
