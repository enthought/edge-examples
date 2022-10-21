import "../style/style.css";
import "bootstrap/dist/css/bootstrap.min.css";

import React, { Component } from "react";
import { Data } from 'plotly.js';
import Plot from 'react-plotly.js';
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";


const PLOTS_PER_ROW = 3;

interface IPlot {
  title: string;
  key: string;
  data: Array<Data>;
}

export interface IDashboard {
  plots?: Array<IPlot>
}

interface IState {
  id: string;
  dashboard?: IDashboard
}
export class Main extends Component<{ urlPrefix: string, dashboard?: IDashboard }, IState> {
  constructor(props: { urlPrefix: string, dashboard?: IDashboard }) {
    super(props);
    this.state = {
      id: "",
      dashboard: props.dashboard
    };
  }
  
  makeUrl = (url: string): string => `${this.props.urlPrefix}${url}`;

  render(): React.ReactNode {
    console.log(this.state);
    if (!this.state.dashboard?.plots?.length) {
      return (
        <div>No data</div>
      )
    }
    const rows: Array<Array<IPlot>> = [];
    this.state.dashboard?.plots.forEach(
      (plot, index) => {
        const rowNum = Math.floor(index / PLOTS_PER_ROW);
        if (rowNum > rows.length - 1) {
          rows.push([] as Array<IPlot>);
        };
        rows[rowNum].push(plot)
      }
    )

    console.log(rows);

    return (
      <Col style={{backgroundColor: "#eee"}}>
        <Row>
          <h2>Edge Dashboard Example</h2>
        </Row>
        <Row style={{backgroundColor: "#eee"}}>
          <Col id="sidebar" md={3}>
            Side Info
          </Col>
          <Col id="graphs" md={9}>
            {rows.map(row => (
              <Row style={{marginBottom: "1em", backgroundColor: "#eee"}}>
                {row.map(plot => (
                  <Col md={4}>
                    <Plot
                      data={plot.data}
                      layout={{
                        title: plot.title,
                        autosize: true
                      }}
                      useResizeHandler={true}
                      style={{
                        width: "100%", height: "100%"
                      }}
                    />                   
                  </Col>
                ))}
              </Row>
            ))}
          </Col>
        </Row>
      </Col>
    );
  }
}
