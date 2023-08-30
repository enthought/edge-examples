import { DataGrid, DataModel, TextRenderer } from "@lumino/datagrid";

class StaticDataModel extends DataModel {
  rowCount(region) {
    return region === "body" ? 100 : 1;
  }

  columnCount(region) {
    return region === "body" ? 100 : 1;
  }

  data(region, row, column) {
    if (region === "row-header") {
      return `R: ${row}, ${column}`;
    }
    if (region === "column-header") {
      return `C: ${row}, ${column}`;
    }
    if (region === "corner-header") {
      return `N: ${row}, ${column}`;
    }
    return Math.random() - 0.5;
  }
}

export function createDatagrid() {
  const elideFloatRenderer = new TextRenderer({
    elideDirection: ({ column }) => (column % 2 === 0 ? "right" : "left"),
    backgroundColor: ({ value }) =>
      value > 0 ? "rgb(49,130,189)" : "rgb(204,204,204)",
  });

  const model = new StaticDataModel();
  const grid = new DataGrid();
  grid.cellRenderers.update({ body: elideFloatRenderer });
  grid.dataModel = model;

  return grid;
}
