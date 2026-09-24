import { assign, createMachine } from 'xstate';
import type { SimulatorNode } from '../types';

interface Context {
  sessionId: number | null;
  node: SimulatorNode | null;
  history: string[];
  feedback: string | null;
  isFinished: boolean;
}

type Event =
  | { type: 'START'; sessionId: number; node: SimulatorNode }
  | { type: 'CHOOSE'; choiceId: string; next: SimulatorNode; feedback: string; isFinished: boolean }
  | { type: 'RESET' };

export const simulatorMachine = createMachine({
  id: 'simulator',
  initial: 'idle',
  types: {} as { context: Context; events: Event },
  context: {
    sessionId: null,
    node: null,
    history: [],
    feedback: null,
    isFinished: false,
  },
  states: {
    idle: {
      on: {
        START: {
          target: 'playing',
          actions: assign({
            sessionId: ({ event }) => event.sessionId,
            node: ({ event }) => event.node,
            history: [],
            feedback: null,
            isFinished: false,
          }),
        },
      },
    },
    playing: {
      on: {
        CHOOSE: {
          target: 'playing',
          actions: assign({
            node: ({ event }) => event.next,
            history: ({ context, event }) => [...context.history, event.choiceId],
            feedback: ({ event }) => event.feedback,
            isFinished: ({ event }) => event.isFinished,
          }),
        },
        RESET: 'idle',
      },
    },
  },
});