import * as ReactDOM from "react-dom";

import { Widget } from "@lumino/widgets";
import { MessageLoop } from "@lumino/messaging";

/**
 * An abstract class for a Phosphor widget which renders a React component.
 */
export class ReactWidget extends Widget {
  /**
   * Creates a new `ReactWidget` that renders a constant element.
   * @param element React element to render.
   */
  static create(element) {
    return new (class extends ReactWidget {
      render() {
        return element;
      }
    })();
  }

  /**
   * Render the content of this widget using the virtual DOM.
   *
   * This method will be called anytime the widget needs to be rendered, which
   * includes layout triggered rendering.
   *
   * Subclasses should define this method and return the root React nodes here.
   */
  render() {
    throw "Not implemented";
  }

  /**
   * Called to update the state of the widget.
   *
   * The default implementation of this method triggers
   * VDOM based rendering by calling the `renderDOM` method.
   */
  onUpdateRequest(msg) {
    this.renderPromise = this.renderDOM();
  }

  /**
   * Called after the widget is attached to the DOM
   */
  onAfterAttach(msg) {
    // Make *sure* the widget is rendered.
    MessageLoop.sendMessage(this, Widget.Msg.UpdateRequest);
  }

  /**
   * Called before the widget is detached from the DOM.
   */
  onBeforeDetach(msg) {
    // Unmount the component so it can tear down.
    ReactDOM.unmountComponentAtNode(this.node);
  }

  /**
   * Render the React nodes to the DOM.
   *
   * @returns a promise that resolves when the rendering is done.
   */
  renderDOM() {
    return new Promise((resolve) => {
      const vnode = this.render();
      // Split up the array/element cases so type inference chooses the right
      // signature.
      if (Array.isArray(vnode)) {
        ReactDOM.render(vnode, this.node, resolve);
      } else if (vnode) {
        ReactDOM.render(vnode, this.node, resolve);
      } else {
        // If the virtual node is null, unmount the node content
        ReactDOM.unmountComponentAtNode(this.node);
        resolve();
      }
    });
  }
}
