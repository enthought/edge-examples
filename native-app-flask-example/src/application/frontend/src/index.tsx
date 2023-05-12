import React from "react";

import { createRoot } from "react-dom/client";
import { Main } from "./main";

const configEl = document.getElementById("server-config-data");
let urlPrefix = "/";
let username: string | undefined = undefined;
if (configEl) {
  const configData = JSON.parse(configEl.textContent || "") as {
    [key: string]: string;
  };
  urlPrefix = configData["urlPrefix"];
  username = configData["user_name"];
}

const root = createRoot(document.getElementById("root"));
root.render(<Main urlPrefix={urlPrefix} username={username}/>);
