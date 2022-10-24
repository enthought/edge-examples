import React from "react";

import { createRoot } from "react-dom/client";
import { Main } from "./main";

const configEl = document.getElementById("server-config-data");
let urlPrefix = "/";
if (configEl) {
  const configData = JSON.parse(configEl.textContent || "") as {
    [key: string]: string;
  };
  urlPrefix = configData["urlPrefix"];
}

const root = createRoot(document.getElementById("root"));
root.render(<Main urlPrefix={urlPrefix} />);
