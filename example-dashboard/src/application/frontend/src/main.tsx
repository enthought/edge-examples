import "../style/style.css";
import "bootstrap/dist/css/bootstrap.min.css";

import React, { Component, CSSProperties } from "react";
import { Data, Layout, Config } from 'plotly.js';
import Plot from 'react-plotly.js';
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";

interface IPlot {
  id: string;
  data: Array<Data>;
  layout: Layout;
  style?: CSSProperties;
  config?: Config;
}

export interface IDashboard {
  plots?: Array<IPlot>;
  user_name?: string;
}

interface IState {
  id: string;
  dashboard?: IDashboard;
}

const DEFAULT_PLOT_STYLE: CSSProperties = {
  marginRight: "10px",
  marginBottom: "10px"
}

export class Main extends Component<{ urlPrefix: string, dashboard?: IDashboard }, IState> {
  constructor(props: { urlPrefix: string, dashboard?: IDashboard }) {
    super(props);
    this.state = {
      id: "",
      dashboard: props.dashboard
    };
  }
  
  render(): React.ReactNode {
    const { user_name, plots } = this.state.dashboard ?? { plots: [] };
    console.log(this.state.dashboard);
    if (!plots?.length) {
      return (
        <div>No data</div>
      )
    }

    return (
      <Col style={{backgroundColor: "#eee"}}>
        <Row>
          <h2>Edge Dashboard Example</h2>
        </Row>
        <Row style={{backgroundColor: "#eee"}}>
          <Col id="sidebar" md={3}>
            <h5>{user_name ? `Welcome ${user_name}` : "User not logged in"}</h5>
            <div>
              Plots
            </div>
            {plots.map(
              (plot) => (
                <div>
                  <a href={`#${plot.id}`}>{`${plot.layout.title}`}</a>
                </div>
              )
            )}
          </Col>
          <Col id="graphs" md={9}>
            <div style={{width: "100%", height: "100%", backgroundColor: "#eee", display: "flex", "flexWrap": "wrap"}}>
              {plots.map(
                (plot) => {
                  const { id, data, layout, config, style } = plot;
                  return (
                    <div id={id} key={id}>
                      <Plot
                        data={data}
                        layout={layout}
                        useResizeHandler={true}
                        style={{
                          ...DEFAULT_PLOT_STYLE,
                          ...style
                        }}
                        config={config}
                      />
                    </div>
                  )
                }
              )}
            </div>
          </Col>
        </Row>
      </Col>
    );
  }
}
