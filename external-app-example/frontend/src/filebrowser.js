import { Signal } from "@lumino/signaling";

import { FileBrowser, FilterFileBrowserModel } from "@jupyterlab/filebrowser";
import { nullTranslator } from "@jupyterlab/translation";
import { DocumentManager } from "@jupyterlab/docmanager";
import { DocumentRegistry } from "@jupyterlab/docregistry";
import { ServiceManager } from "@jupyterlab/services";

class FakeDrive {
  constructor() {
    this._fileChanged = new Signal(this);
    this._isDisposed = false;
  }

  /**
   * The name of the drive.
   */
  get name() {
    return "Fake";
  }

  /**
   * A signal emitted when a file operation takes place.
   */
  get fileChanged() {
    return this._fileChanged;
  }

  /**
   * Test whether the manager has been disposed.
   */
  get isDisposed() {
    return this._isDisposed;
  }

  /**
   * Dispose of the resources held by the manager.
   */
  dispose() {
    if (this.isDisposed) {
      return;
    }
    this._isDisposed = true;
    Signal.clearData(this);
  }

  /**
   * Get a file or directory.
   *
   * @param path: The path to the file.
   * @param options: The options used to fetch the file.
   * @param path
   * @param options
   * @returns A promise which resolves with the file content.
   */
  get(path, options) {
    return {
      name: "",
      path,
      last_modified: "",
      created: "",
      format: null,
      mimetype: "",
      content: [
        {
          name: "dir",
          path: "dir",
          last_modified: "",
          created: "",
          format: null,
          mimetype: "",
          content: [],
          size: undefined,
          writable: true,
          type: "directory",
        },
        {
          name: "file1.txt",
          path: "file1.txt",
          last_modified: "",
          created: "",
          format: "txt",
          mimetype: "",
          content: null,
          size: undefined,
          writable: true,
          type: "file",
        },
        {
          name: "file2.txt",
          path: "file2.txt",
          last_modified: "",
          created: "",
          format: "txt",
          mimetype: "",
          content: null,
          size: undefined,
          writable: true,
          type: "file",
        },
        {
          name: "file3.txt",
          path: "file3.txt",
          last_modified: "",
          created: "",
          format: "txt",
          mimetype: "",
          content: null,
          size: undefined,
          writable: true,
          type: "file",
        },
      ],
      size: undefined,
      writable: true,
      type: "directory",
    };
  }

  getDownloadUrl(path) {
    throw new Error("Not implemented");
  }

  newUntitled(options = {}) {
    throw new Error("Not implemented");
  }

  delete(path) {
    throw new Error("Not implemented");
  }

  rename(path, newPath) {
    throw new Error("Not implemented");
  }

  save(path, options) {
    throw new Error("Not implemented");
  }

  copy(fromFile, toDir) {
    throw new Error("Not implemented");
  }

  createCheckpoint(path) {
    throw new Error("Not implemented");
  }

  listCheckpoints(path) {
    throw new Error("Not implemented");
  }

  restoreCheckpoint(path, checkpointID) {
    throw new Error("Not implemented");
  }

  deleteCheckpoint(path, checkpointID) {
    throw new Error("Not implemented");
  }
}

export async function createFileBrowser() {
  const manager = new ServiceManager();
  await manager.ready;

  const opener = {
    open: (widget) => {
      // This is a noop, should we do something?
    },
  };

  const docRegistry = new DocumentRegistry();
  const docManager = new DocumentManager({
    registry: docRegistry,
    manager,
    opener,
  });

  const drive = new FakeDrive();
  docManager.services.contents.addDrive(drive);

  const model = new FilterFileBrowserModel({
    translator: nullTranslator,
    manager: docManager,
    driveName: drive.name,
  });

  return new FileBrowser({
    id: "filebrowser",
    model,
  });
}
