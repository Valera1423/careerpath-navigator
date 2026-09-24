import { useCallback, useEffect, useRef, useState } from 'react';

interface SpeechRecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((e: unknown) => void) | null;
  onerror: ((e: unknown) => void) | null;
  onend: (() => void) | null;
  start(): void;
  stop(): void;
}

interface ResultEvent {
  results: ArrayLike<ArrayLike<{ transcript: string }>>;
}

export function useVoiceInput(lang = 'ru-RU') {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [supported, setSupported] = useState(false);
  const ref = useRef<SpeechRecognitionLike | null>(null);

  useEffect(() => {
    const w = window as unknown as {
      SpeechRecognition?: new () => SpeechRecognitionLike;
      webkitSpeechRecognition?: new () => SpeechRecognitionLike;
    };
    const Ctor = w.SpeechRecognition ?? w.webkitSpeechRecognition;
    if (!Ctor) return;

    setSupported(true);
    const rec = new Ctor();
    rec.lang = lang;
    rec.continuous = false;
    rec.interimResults = true;

    rec.onresult = (e: unknown) => {
      const event = e as ResultEvent;
      const text = Array.from(event.results)
        .map((r) => r[0].transcript)
        .join('');
      setTranscript(text);
    };
    rec.onend = () => setIsListening(false);
    rec.onerror = () => setIsListening(false);
    ref.current = rec;
  }, [lang]);

  const start = useCallback(() => {
    if (!ref.current) return;
    setTranscript('');
    setIsListening(true);
    ref.current.start();
  }, []);

  const stop = useCallback(() => {
    ref.current?.stop();
    setIsListening(false);
  }, []);

  const reset = useCallback(() => setTranscript(''), []);

  return { isListening, transcript, supported, start, stop, reset };
}