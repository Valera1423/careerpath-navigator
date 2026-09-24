import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: '' };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error('[ErrorBoundary]', error, info.componentStack);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div className="screen center">
          <h3>Что-то пошло не так</h3>
          <p className="muted">{this.state.message}</p>
          <button className="btn" onClick={() => location.reload()}>
            Перезагрузить
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}