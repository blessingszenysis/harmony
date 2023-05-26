// @flow
import * as React from 'react';
import Draggable from 'react-draggable';

import DraggableChild from 'components/ui/DraggableItem/internal/DraggableChild';
import autobind from 'decorators/autobind';
import { noop } from 'util/util';
import type { StyleObject } from 'types/jsCore';

type Position = {
  x: number,
  y: number,
};

// Signal provided handler should return to instruct how the new drag position
// should be preserved.
//   - `STORE | void`: Store the drag position immediately.
//   - `IGNORE`: Ignore the latest drag position do not overwrite the previous
//               position.
//   - `RESET`: Reset the drag position to 0,0 immediately.
export type DragEventSignal = 'STORE' | 'IGNORE' | 'RESET' | void;

type DragSignalMap = {
  STORE: 'STORE',
  IGNORE: 'IGNORE',
  RESET: 'RESET',
};

export const DRAG_SIGNAL: DragSignalMap = {
  STORE: 'STORE',
  IGNORE: 'IGNORE',
  RESET: 'RESET',
};

// Data provided by react-draggable in the event handler callback.
// TODO(stephen): Get this from react-draggable eventually. Their current types
// do not pass flow validation though.
export type DraggableData = {
  ...Position,
  deltaX: number,
  deltaY: number,
  lastX: number,
  lastY: number,
  node: HTMLElement,
};

type DraggableEventHandler<T> = (
  e: SyntheticEvent<HTMLDivElement>,
  data: DraggableData,
  extraEventData: T | void,
) => DragEventSignal;

type DraggableProps<T> = {
  /**
   * Called while the component is being dragged.
   */
  onDrag: DraggableEventHandler<T>,

  /**
   * Called when the component first starts being dragged by the user.
   */
  onDragEnd: DraggableEventHandler<T>,

  /**
   * Called when the user releases the item and dragging is stopped.
   */
  onDragStart: DraggableEventHandler<T>,
};

type DefaultProps<T> = {
  ...DraggableProps<T>,
  disableDrag: boolean,

  /**
   * Restrict the bounding area this item can be dragged within. If not
   * provided, the item can be dragged anywhere on the page.
   * - `void`: Do not restrict dragging to any boundary.
   * - `parent`: Restrict the movement of the element to only within the
   *             element's offsetParent (the nearest node with position
   *             relative/absolute).
   * - `string`: Restrict movement of the element to only move within elements
   *             that match the CSS selector supplied.
   * - `{ bottom: number, left: number, right: number, top: number }`:
   *             Relative bounding box to restrict the movement of the element
   *             within. These indicate how far in each direction the element
   *             can move.
   */
  dragMovementBounds:
    | void
    | 'parent'
    | string
    | { bottom: number, left: number, right: number, top: number },

  /**
   * Optional css selector to limit the elements that dragging can be initiated
   * on to only those that match the selector.
   */
  dragRestrictionSelector: string,

  /**
   * Extra data to pass into the event callbacks.
   */
  extraEventData?: T,
  style?: StyleObject,
};

type Props<T> = {
  ...DefaultProps<T>,
  children: React.Element<React.ElementType>,
};

type State = {
  position: Position,
};

// Store the timestamp of the latest "drag end" event so we can suppress onClick
// events that might be generated by the browser at the same time.
let LAST_DRAG_END_TIMESTAMP = 0;

// Update the position of the draggable item based on the event signal. Convert
// our version of an event signal into the return type required by
// `react-draggable`. If no `updatePosition` method is provided, send the
// "cancel" event to `react-draggable`.
// NOTE(stephen): This method is intentionally defined outside the component to
// avoid using `this`. Because event handlers are asynchronous, there is a
// possibility of the component unmounting before the event can be handled. It
// is also possible for the component to unmount synchronously during the
// handling of the event when the DraggableEventHandler is called.
function processEventSignal(
  signal: DragEventSignal,
  data: DraggableData,
  updatePosition: (({ ...Position, ... }) => void) | void,
): void | false {
  // If `updatePosition` is not defined, we must return `false` to prevent
  // `react-draggable` from internally calling `setState` with the updated drag
  // position.
  // NOTE(stephen): This is true as of react-draggable v4.1.0 in the
  // `onDragStart`, `onDrag`, and `onDragStop` internal handlers.
  // https://github.com/mzabriskie/react-draggable/blob/v4.1.0/lib/Draggable.js#L299
  if (updatePosition === undefined) {
    return false;
  }

  if (signal === 'STORE' || signal === undefined) {
    updatePosition(data);
    return undefined;
  }

  if (signal === 'IGNORE') {
    return false;
  }

  if (signal === 'RESET') {
    updatePosition({ x: 0, y: 0 });
    return undefined;
  }

  return undefined;
}

/**
 * The DraggableItem is a flexibile UI component that can make any element
 * draggable.
 */
export default class DraggableItem<T> extends React.PureComponent<
  Props<T>,
  State,
> {
  static defaultProps: DefaultProps<T> = {
    disableDrag: false,
    dragMovementBounds: undefined,
    dragRestrictionSelector: '',
    extraEventData: undefined,
    onDrag: noop,
    onDragEnd: noop,
    onDragStart: noop,
    style: undefined,
  };

  state: State = {
    position: { x: 0, y: 0 },
  };

  componentWillUnmount() {
    // Undefine the `updatePosition` method when the component unmounts so we
    // do not call `setState` on an unmounted component inside the asynchronous
    // `callEventHandler`.
    // $FlowExpectedError[incompatible-type] we'll allow this
    this.updatePosition = undefined;
  }

  // Update the stored drag position with a new value.
  // NOTE(stephen): `updatePosition` is defined as an instance property because
  // its value needs to be modifiable.
  updatePosition: ({ ...Position, ... }) => void = ({ x, y }) => {
    this.setState({ position: { x, y } });
  };

  // Convert our internal event signals into a react-draggable interpretable
  // event response. react-draggable interprets `undefined` as store and
  // `false` as ignore the event.
  callEventHandler(
    handler: DraggableEventHandler<T>,
    e: SyntheticEvent<HTMLDivElement>,
    data: DraggableData,
  ): void | false {
    const { disableDrag, extraEventData } = this.props;

    // NOTE(stephen): Need to check the disableDrag property here since
    // react-draggable will not re-check the "disabled" prop if dragging is
    // in progress.
    if (disableDrag) {
      return false;
    }

    const signal = handler(e, data, extraEventData);
    return processEventSignal(signal, data, this.updatePosition);
  }

  @autobind
  onDrag(e: SyntheticEvent<HTMLDivElement>, data: DraggableData): void | false {
    return this.callEventHandler(this.props.onDrag, e, data);
  }

  @autobind
  onDragStart(
    e: SyntheticEvent<HTMLDivElement>,
    data: DraggableData,
  ): void | false {
    return this.callEventHandler(this.props.onDragStart, e, data);
  }

  @autobind
  onDragEnd(
    e: SyntheticEvent<HTMLDivElement>,
    data: DraggableData,
  ): void | false {
    LAST_DRAG_END_TIMESTAMP = e.timeStamp;
    return this.callEventHandler(this.props.onDragEnd, e, data);
  }

  @autobind
  onClickCapture(e: SyntheticEvent<HTMLDivElement>): boolean | void {
    // Prevent click events from propagating down to child elements if the click
    // is triggered at the same time that dragging ends.
    if (e.timeStamp === LAST_DRAG_END_TIMESTAMP) {
      e.stopPropagation();
      e.preventDefault();
      return false;
    }

    return undefined;
  }

  render(): React.Element<typeof Draggable> {
    const {
      children,
      disableDrag,
      dragMovementBounds,
      dragRestrictionSelector,
      style,
    } = this.props;

    const className =
      dragRestrictionSelector.length === 0
        ? 'ui-draggable-item ui-draggable-item--fully-draggable'
        : 'ui-draggable-item';
    return (
      <Draggable
        axis="y"
        bounds={dragMovementBounds}
        disabled={disableDrag}
        handle={dragRestrictionSelector}
        onDrag={this.onDrag}
        onStop={this.onDragEnd}
        onStart={this.onDragStart}
        position={this.state.position}
      >
        <DraggableChild
          additionalStyle={style}
          className={className}
          onClickCapture={this.onClickCapture}
        >
          {children}
        </DraggableChild>
      </Draggable>
    );
  }
}
