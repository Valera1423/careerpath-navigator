import * as MaxUI from '@dementevdev/max-ui';
import type { ComponentType, ReactNode } from 'react';
import React from 'react';

type AnyProps = Record<string, unknown> & { children?: ReactNode };

const fromMax = <P,>(name: string): ComponentType<P> | undefined =>
  (MaxUI as unknown as Record<string, ComponentType<P>>)[name];

const fallback =
  <P extends AnyProps>(tag: keyof JSX.IntrinsicElements, baseClass: string) =>
  function Fallback(props: P) {
    const { children, className, ...rest } = props as AnyProps;
    return React.createElement(
      tag,
      { ...rest, className: [baseClass, className].filter(Boolean).join(' ') },
      children,
    );
  };

export const Button = fromMax<AnyProps>('Button') ?? fallback('button', 'btn');
export const Input = fromMax<AnyProps>('Input') ?? fallback('input', 'ui-input');
export const Textarea = fromMax<AnyProps>('Textarea') ?? fallback('textarea', 'ui-textarea');
export const Card = fromMax<AnyProps>('Card') ?? fallback('div', 'card');
export const Text = fromMax<AnyProps>('Text') ?? fallback('span', 'ui-text');
export const Title = fromMax<AnyProps>('Title') ?? fallback('h1', 'ui-title');
export const Tag = fromMax<AnyProps>('Tag') ?? fallback('button', 'chip');
export const Spinner = fromMax<AnyProps>('Spinner') ?? fallback('div', 'ui-spinner');
export const Progress = fromMax<AnyProps>('Progress') ?? fallback('div', 'progress');
export const Checkbox = fromMax<AnyProps>('Checkbox') ?? fallback('input', 'ui-checkbox');
export const Select = fromMax<AnyProps>('Select') ?? fallback('select', 'ui-select');

export function notify(message: string): void {
  const fn = (MaxUI as unknown as Record<string, (m: string) => void>).showToast;
  if (typeof fn === 'function') fn(message);
  else console.info('[notify]', message);
}
