#!/usr/bin/env node

// import { Command } from "commander";
import { mapperToJson } from "./utils/parser";
// const program = new Command();

// program.version("1.0.0").description("A simple CLI app");

// program
//   .command("parse <amount>")
//   .description("Parse data into subset")
//   .action(async (amount) => {
//     await mapperToJson(amount as number);
//   });

// program.parse(process.argv);

async function main() {
  await mapperToJson(100);
}

main();
