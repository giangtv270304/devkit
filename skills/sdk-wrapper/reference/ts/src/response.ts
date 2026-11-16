/** Envelope of every successful call. */
export interface ApiResponse<T> {
  requestId: string;
  data: T;
}
