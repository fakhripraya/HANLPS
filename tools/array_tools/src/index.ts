#!/usr/bin/env node

import {
  shiftArray,
  addIsReady,
  addIndex,
  addKey,
} from "./utils/parser";

async function main() {
  await addKey();
}

main();
