#!/usr/bin/env node

import { shiftArray, addIsReady } from "./utils/parser";

async function main() {
  await addIsReady();
}

main();
