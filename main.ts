// One image of Saturday 21 November 2026.
//
// The front page is drawn ahead of time by tools/make_image.py and
// committed as entry.png next to this file. This program only has to
// hand that image to the grader: copy it into the output directory
// unchanged. There is no network, no randomness and no clock involved,
// so every run of this program produces the same output bytes.

import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
