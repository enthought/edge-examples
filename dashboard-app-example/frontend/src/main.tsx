import "../style/style.css";
import "bootstrap/dist/css/bootstrap.min.css";

import React, { Component } from "react";
import Plot from 'react-plotly.js';
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import Navbar from "react-bootstrap/Navbar";
import Row from "react-bootstrap/Row";

interface IState {
  id: string;
}

export class Main extends Component<{ urlPrefix: string }, IState> {
  private stageRef: React.RefObject<HTMLDivElement>;
  private pollHandler: any = null;
  constructor(props: { urlPrefix: string }) {
    super(props);
    this.state = {
      id: ""
    };

    window.addEventListener("resize", this.resizeCanvas);
    this.stageRef = React.createRef<HTMLDivElement>();
  }

  componentDidMount(): void {
    this.resizeCanvas();
  }

  makeUrl = (url: string): string => `${this.props.urlPrefix}${url}`;

  resizeCanvas = () => {
  };

  preventDefault = (e: any) => {
    e.preventDefault();
    e.stopPropagation();
  };

  render(): React.ReactNode {
    return (
      <Plot
        data={[
          {
            x: [1, 2, 3],
            y: [2, 6, 3],
            type: 'scatter',
            mode: 'lines+markers',
            marker: {color: 'red'},
          },
          {type: 'bar', x: [1, 2, 3], y: [2, 5, 3]},
        ]}
        layout={ {width: 320, height: 240, title: 'A Fancy Plot'} }
      />
    );
  }
}
