#!/usr/bin/env node

import { Command } from "commander";
import { fetchDataFromAPI } from "./utils/fetcher.js";
const program = new Command();

program
  .version("1.0.0")
  .description("API tools for HANLPS");

program
  .command("fetchig <size>")
  .description("fetch instagram data into JSON")
  .action(async (size) => {
    await fetchDataFromAPI(size as number);
  });

program.parse(process.argv);
