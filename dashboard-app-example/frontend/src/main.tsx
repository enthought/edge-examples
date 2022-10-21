import "../style/style.css";
import "bootstrap/dist/css/bootstrap.min.css";

import React, { Component } from "react";
import Plot from 'react-plotly.js';
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import Navbar from "react-bootstrap/Navbar";
import Row from "react-bootstrap/Row";


interface IData {
  graph?: {
    x: Array<number>,
    y: Array<number>
  }
}

interface IState {
  id: string;
  data?: IData
}

export class Main extends Component<{ urlPrefix: string, data?: IData }, IState> {
  private stageRef: React.RefObject<HTMLDivElement>;
  private pollHandler: any = null;
  constructor(props: { urlPrefix: string, data?: IData }) {
    super(props);
    this.state = {
      id: "",
      data: props.data
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
    if (!this.state.data?.graph) {
      return (
        <div>No data</div>
      )
    }
    return (
      <Plot
        data={[
          {
            x: this.state.data.graph.x,
            y: this.state.data.graph.y,
            type: 'scatter',
            mode: 'lines+markers',
            marker: {color: 'red'},
          },
        ]}
        layout={{
          title: "A Fancy Plot",
          autosize: true
        }}
        useResizeHandler={true}
        style={{
          width: "100%", height: "100%"
        }}
      />
    );
  }
}
