import "../style/style.css";
import "bootstrap/dist/css/bootstrap.min.css";

import Konva from "konva";
import React, { Component } from "react";
import Col from "react-bootstrap/Col";
import Form from "react-bootstrap/Form";
import Navbar from "react-bootstrap/Navbar";
import Row from "react-bootstrap/Row";

interface IParams {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
}

interface ILog {
  time: string;
  content: string;
}
interface IState {
  id: string;
  log: ILog[];
  parameters: {
    [key: string]: IParams;
  };
}

export class Main extends Component<{ urlPrefix: string }, IState> {
  private stageRef: React.RefObject<HTMLDivElement>;
  private stage?: Konva.Stage;
  private layer?: Konva.Layer;
  private scheduledTasks: {
    [key: string]: { name: string; konvaImage: Konva.Image };
  } = {};
  private pollHandler: any = null;
  constructor(props: { urlPrefix: string }) {
    super(props);
    this.state = {
      id: "",
      log: [],
      parameters: {
        scaleFactor: {
          label: "Scale Factor",
          value: 1.1,
          min: 1,
          max: 3,
          step: 0.02,
        },
        minNeighbors: {
          label: "Min Neighbors",
          value: 4,
          min: 3,
          max: 6,
          step: 1,
        },
      },
    };

    window.addEventListener("resize", this.resizeCanvas);
    this.stageRef = React.createRef<HTMLDivElement>();
  }

  componentDidMount(): void {
    this.stage = new Konva.Stage({
      container: "canvas-container",
    });

    this.layer = new Konva.Layer();
    this.stage.add(this.layer);
    this.stage.draw();
    this.resizeCanvas();
  }

  makeUrl = (url: string): string => `${this.props.urlPrefix}${url}`;

  resizeCanvas = () => {
    const width = this.stageRef.current!.clientWidth;
    const height = this.stageRef.current!.clientHeight;
    this.stage?.width(width);
    this.stage?.height(height);
  };

  /**
   * Poll for result every 1 second.
   */
  pollForResult = () => {
    this.pollHandler = setInterval(async () => {
      const request = await fetch(this.makeUrl("job"), {
        method: "GET",
        credentials: "same-origin",
      });
      const results = await request.json();

      const updatedLog: ILog[] = [];
      Object.entries(results).forEach(([taskId, imageStr]) => {
        if (taskId in this.scheduledTasks) {
          const task = this.scheduledTasks[taskId];

          const theImage = task.konvaImage;
          const image = new Image();
          image.src = `data:image/png;base64,${imageStr}`;
          theImage.image(image);
          theImage.opacity(1);
          updatedLog.push(this.createLog(`Task for ${task["name"]} finished`));
          delete this.scheduledTasks[taskId];
        }
      });
      this.setState({
        ...this.state,
        log: [...this.state.log, ...updatedLog],
      });
      if (Object.keys(this.scheduledTasks).length === 0) {
        clearInterval(this.pollHandler);
        this.pollHandler = null;
      }
    }, 1000);
  };

  handleOnDrop = async (e: React.DragEvent<HTMLDivElement>) => {
    this.preventDefault(e);
    const posX = e.nativeEvent.offsetX;
    const posY = e.nativeEvent.offsetY;

    const imageFiles = e.dataTransfer.files;
    const updatedLog: ILog[] = [];
    for (let index = 0; index < imageFiles.length; index++) {
      const file = imageFiles[index];
      const url = URL.createObjectURL(file);

      const img = new Image();
      img.src = url;
      const layer = this.layer;

      img.onload = () => {
        const imgWidth = img.width;
        const imgHeight = img.height;
        const max = 600;
        const ratio = imgWidth > imgHeight ? imgWidth / max : imgHeight / max;
        const width = imgWidth / ratio;
        const height = imgHeight / ratio;
        const theImg = new Konva.Image({
          image: img,
          x: posX - width / 2,
          y: posY - height / 2,
          width,
          height,
          draggable: true,
          rotation: 0,
        });
        theImg.opacity(0.5);

        layer?.add(theImg);
        layer?.draw();
        theImg.addEventListener("dblclick", () => {
          URL.revokeObjectURL(url);
          const id = theImg.id();
          if (id in this.scheduledTasks) {
            const newLog = this.createLog(
              "Removed task " + this.scheduledTasks[id]["name"]
            );
            delete this.scheduledTasks[id];
            this.setState({
              ...this.state,
              log: [...this.state.log, newLog],
            });
          }
          theImg.destroy();
          layer?.draw();
        });
        file.arrayBuffer().then(async (arrayBuffer) => {
          const base64 = btoa(
            new Uint8Array(arrayBuffer).reduce(
              (data, byte) => data + String.fromCharCode(byte),
              ""
            )
          );
          const params = {};
          for (const key in this.state.parameters) {
            params[key] = this.state.parameters[key].value;
          }
          const request = await fetch(this.makeUrl("job"), {
            method: "POST",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ image: base64, params }),
            credentials: "same-origin",
          });
          const result = await request.json();
          const id = result.id;
          const newLog = this.createLog("Scheduled task for " + file.name);
          if (!this.pollHandler) {
            this.pollForResult();
          }
          updatedLog.push(newLog);
          theImg.id(id);
          this.scheduledTasks[id] = { name: file.name, konvaImage: theImg };

          this.setState({
            ...this.state,
            log: [...this.state.log, ...updatedLog],
          });
        });
      };
    }
  };

  preventDefault = (e: any) => {
    e.preventDefault();
    e.stopPropagation();
  };

  paramsOnChange = (key: string, value: number) => {
    this.setState((old) => ({
      ...old,
      parameters: {
        ...old.parameters,
        [key]: {
          ...old.parameters[key],
          value,
        },
      },
    }));
  };

  parameterForm = (key, option: IParams): JSX.Element => {
    const { min, max, value, step } = option;
    return (
      <Form.Group key={key}>
        <Form.Label>{option.label}</Form.Label>
        <Form.Group as={Row}>
          <Col xs="9">
            <Form.Range
              value={value}
              onChange={(e) =>
                this.paramsOnChange(key, parseFloat(e.currentTarget.value))
              }
              min={min}
              max={max}
              step={step}
            />
          </Col>
          <Col xs="3">
            <Form.Control
              value={option.value}
              onChange={(e) =>
                this.paramsOnChange(key, parseFloat(e.currentTarget.value))
              }
              min={min}
              max={max}
              step={step}
            />
          </Col>
        </Form.Group>
      </Form.Group>
    );
  };

  createLog = (content: string) => {
    return {
      time: new Date().toLocaleString("en-US", { hour12: false }),
      content,
    };
  };
  setLog = (content: string) => {
    const newLog = this.createLog(content);
    this.setState({
      ...this.state,
      log: [...this.state.log, newLog],
    });
  };

  render(): React.ReactNode {
    return (
      <div style={{ height: "100%", display: "flex", flexWrap: "wrap" }}>
        <Col className={"control-panel"} md={3}>
          <div className="parameter-panel" style={{ marginBottom: "20px" }}>
            <Navbar style={{ justifyContent: "center", background: "#dee2e6" }}>
              <Navbar.Brand>PARAMETERS</Navbar.Brand>
            </Navbar>
            <Form style={{ padding: "10px" }}>
              {Object.entries(this.state.parameters).map(([key, value]) =>
                this.parameterForm(key, value)
              )}
            </Form>
          </div>
          <div className="log-panel">
            <Navbar style={{ justifyContent: "center", background: "#dee2e6" }}>
              <Navbar.Brand>LOGS</Navbar.Brand>
            </Navbar>
            <div style={{ padding: "10px", overflow: "auto" }}>
              <div className="full-height flex-column">
                {this.state.log.map((log, idx) => (
                  <span key={idx}>
                    <>
                      <b>{log.time}: </b> {log.content}
                    </>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </Col>
        <Col className={"display-panel"} md={9}>
          <Navbar style={{ justifyContent: "center", background: "#dee2e6" }}>
            <Navbar.Brand>DROP IMAGES BELOW TO START &#8681;</Navbar.Brand>
          </Navbar>
          <div
            className="drop-zone"
            onDragEnter={this.preventDefault}
            onDragLeave={this.preventDefault}
            onDragOver={this.preventDefault}
            onDrop={this.handleOnDrop}
            ref={this.stageRef}
            id={"canvas-container"}
          ></div>
        </Col>
      </div>
    );
  }
}
