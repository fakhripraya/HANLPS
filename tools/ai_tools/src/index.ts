#!/usr/bin/env node

import {
  generativeLoopThroughArray,
  removeSpecificFromString,
} from "./utils/tools.js";

// Add this to your index.ts
import * as commander from "commander";

const program = new commander.Command();
program.version("1.0.0").description("AI tools for HANLPS");

// Define your commands and flags here
program
  .command("generative")
  .description(
    "Generative loop through the array of elements in the data"
  )
  .action(async () => {
    await generativeLoopThroughArray();
  });

program
  .command("remove")
  .description(
    "Removal loop through the array of elements in the data with AI"
  )
  .action(async () => {
    await removeSpecificFromString();
  });

program.parse(process.argv);
