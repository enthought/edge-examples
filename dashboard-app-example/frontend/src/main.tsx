import "../style/style.css";
import "bootstrap/dist/css/bootstrap.min.css";

import React, { Component, CSSProperties } from "react";
import { Data, Layout } from 'plotly.js';
import Plot from 'react-plotly.js';
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";


const PLOTS_PER_ROW = 3;

interface IPlot {
  key: string;
  data: Array<Data>;
  layout: Layout;
  style?: CSSProperties;
}


interface IUser {
  name: string;
}

export interface IDashboard {
  plots?: Array<IPlot>;
  user?: IUser;
}

interface IState {
  id: string;
  dashboard?: IDashboard;
}

const DEFAULT_PLOT_STYLE: CSSProperties = {
  marginRight: "0.5em",
  marginBottom: "0.5em"
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
    const { user, plots } = this.state.dashboard ?? { user: undefined, plots: undefined };
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
            <h5>{user ? `Welcome ${user.name}` : "User not logged in"}</h5>
          </Col>
          <Col id="graphs" md={9}>
            <div style={{width: "100%", height: "100%", backgroundColor: "#eee", display: "flex", "flexWrap": "wrap"}}>
              {plots.map(
                (plot) => {
                  const { data, layout, style } = plot;
                  return (
                    <Plot
                      data={data}
                      layout={layout}
                      useResizeHandler={true}
                      style={{
                        ...DEFAULT_PLOT_STYLE,
                        ...style
                      }}
                      key={plot.key}
                  />
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
