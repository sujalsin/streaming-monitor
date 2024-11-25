import { io } from 'socket.io-client';

export const socket = io('http://localhost:8000', {
  path: '/ws/socket.io',
  autoConnect: true,
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  transports: ['websocket', 'polling'],
});
