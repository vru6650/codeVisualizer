# codeVisualizer

## JavaScript support

### Prerequisites
* [Node.js](https://nodejs.org/) is required for running files with Node.
* (Optional) [Deno](https://deno.land/) enables the **Run JavaScript (Deno)** command.
* (Optional) Install ESLint inside your project with `npm i -D eslint` (or add a global `eslint` to your PATH).

### Running JavaScript
* Open a `.js`, `.mjs`, or `.cjs` file in the editor.
* Choose **Tools → Run JavaScript (Node)** or press <kbd>F7</kbd> to execute it with Node.js. The command uses the nearest `package.json` directory as the working folder and streams stdout/stderr into the Shell with a `$ …` prefix and `[exit code]` footer.
* If Deno is installed, **Tools → Run JavaScript (Deno)** runs the active file with `deno run -A` using the file's folder as the working directory.

### Linting with ESLint
* Install ESLint locally (preferred) with `npm i -D eslint` so the plug-in finds `node_modules/.bin/eslint`. A global `eslint` on PATH is used as a fallback.
* Trigger **Tools → Lint JavaScript (ESLint)** or press <kbd>Shift</kbd>+<kbd>F7</kbd> to lint the active file. Output is shown with ESLint's `--format unix` so messages render as `file:line:col: …`; clicking a diagnostic jumps to the corresponding location in the editor.
