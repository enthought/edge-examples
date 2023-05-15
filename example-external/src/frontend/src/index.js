import { BoxPanel, Widget } from "@lumino/widgets";

import { Button } from "@jupyter-notebook/react-components";

import {
  accentPalette,
  baseLayerLuminance,
  neutralPalette,
  PaletteRGB,
  SwatchRGB,
  StandardLuminance,
} from "@jupyter-notebook/web-components";

import { createDatagrid } from "./datagrid";

import { createPlot } from "./plot";
import { createFileBrowser } from "./filebrowser";

import "@jupyterlab/application/style/index.css";
import "@jupyterlab/filebrowser/style/index.css";
import "@jupyterlab/theme-light-extension/style/theme.css";
import "./index.css";
import { ReactWidget } from "./utils";
import React from "react";

baseLayerLuminance.setValueFor(document.body, StandardLuminance.LightMode);
accentPalette.setValueFor(
  document.body,
  PaletteRGB.from(SwatchRGB.create(88 / 255, 177 / 255, 191 / 255))
);
neutralPalette.setValueFor(
  document.body,
  PaletteRGB.from(SwatchRGB.create(237 / 255, 237 / 255, 237 / 255))
);

const main = async function () {
  const content = new BoxPanel({ direction: "left-to-right", spacing: 10 });
  content.id = "main";

  const box1 = new BoxPanel({ direction: "top-to-bottom", spacing: 10 });
  const box2 = new BoxPanel({ direction: "top-to-bottom", spacing: 10 });

  const topbar = ReactWidget.create([
    <div className="enthought-title">Enthought Demo Application</div>,
    <form action="/logout" method="post">
      <Button type="submit" className="logout-button">
        Logout
      </Button>
    </form>,
  ]);
  topbar.id = "menuBar";

  const url = "/user";
  let user = "";

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (res.ok) {
      user = data.user_id;
    }
  } catch (err) {
    console.log("Error fetching data", err);
  }

  content.addWidget(await createFileBrowser());

  const greetingWidget = new Widget();
  const greeting = document.createElement("h1");
  greeting.textContent = `Hello, ${user}!`;
  greeting.classList.add("greeting-text");
  greetingWidget.node.appendChild(greeting);
  greetingWidget.addClass("app-greeting");

  box1.addWidget(greetingWidget);
  box1.addWidget(createDatagrid());
  content.addWidget(box1);

  const logsWidget = new Widget();
  const logs = document.createElement("p");
  const logsText = [
    "[I 2022-09-14 08:19:05.254 App] extensions were successfully linked.",
    "[I 2022-09-14 08:19:05.261 App] modules were successfully loaded.",
    "[I 2022-09-14 08:19:05.520 App] Python process was successfully loaded.",
    "[I 2022-09-14 08:19:05.536 App] Job started was successfully loaded.",
    "[I 2022-09-14 08:19:05.536 SciApp] Processing data...",
    "[I 2022-09-14 08:19:05.537 SciApp] Processing data...",
    "[I 2022-09-14 08:19:05.539 App] datagrid was successfully loaded.",
    "[I 2022-09-14 08:19:05.543 App] plot was successfully loaded.",
  ];
  logsText.forEach((log) => {
    logs.appendChild(document.createTextNode(log));
    logs.appendChild(document.createElement("br"));
  });
  logs.classList.add("app-logs");
  logsWidget.node.appendChild(logs);

  box2.addWidget(createPlot());
  box2.addWidget(logsWidget);
  content.addWidget(box2);

  window.onresize = () => {
    content.update();
  };

  Widget.attach(topbar, document.body);
  Widget.attach(content, document.body);
};

window.onload = main;
