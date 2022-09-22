import { Button } from "@jupyter-notebook/react-components";

import {
  accentPalette,
  baseLayerLuminance,
  neutralPalette,
  PaletteRGB,
  SwatchRGB,
  StandardLuminance,
} from "@jupyter-notebook/web-components";

import React from "react";
import { render } from "react-dom";

import "./login.css";

// TODO Make this configurable in some way
// Use system preference?
const isDark = false;

baseLayerLuminance.setValueFor(
  document.body,
  isDark ? StandardLuminance.DarkMode : StandardLuminance.LightMode
);
accentPalette.setValueFor(
  document.body,
  PaletteRGB.from(SwatchRGB.create(88 / 255, 177 / 255, 191 / 255))
);
neutralPalette.setValueFor(
  document.body,
  PaletteRGB.from(SwatchRGB.create(237 / 255, 237 / 255, 237 / 255))
);

const Login = () => {
  return (
    <form action="/login" method="post" class="edge-login-form">
      <Button appearance="accent" type="submit" class="edge-login-button">
        Login with Edge
      </Button>
    </form>
  );
};

const root = document.getElementById("root");

render(<Login />, root);
