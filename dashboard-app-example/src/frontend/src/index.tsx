import React from "react";

import { createRoot } from "react-dom/client";
import { Main, IDashboard } from "./main";

const configEl = document.getElementById("server-config-data");
let urlPrefix = "/";
let dashboard: IDashboard = {};
if (configEl) {
  const configData = JSON.parse(configEl.textContent || "") as {
    [key: string]: any;
  };
  urlPrefix = configData["urlPrefix"];
  dashboard = configData["dashboard"];
}

const root = createRoot(document.getElementById("root"));
root.render(<Main urlPrefix={urlPrefix} dashboard={dashboard} />);
