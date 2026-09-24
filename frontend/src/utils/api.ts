export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function readErrorDetail(res: Response): Promise<string> {
  try {
    const body = await res.json();
    return body?.detail ?? `HTTP ${res.status}`;
  } catch {
    return `HTTP ${res.status}`;
  }
}