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
  .requiredOption(
    "-s, --start  [value]",
    "Start value of an array to be sliced"
  )
  .requiredOption(
    "-e, --end  [value]",
    "End value of an array to be sliced"
  )
  .option(
    "--images",
    "Slice the image urls from each element data"
  )
  .action(async (options) => {
    if (options.images)
      await sliceImageURLElements(
        options.start,
        options.end
      );
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
