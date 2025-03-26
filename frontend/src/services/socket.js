import { io } from "socket.io-client";

// Inizializza la connessione WebSocket al backend Flask-SocketIO
export const socket = io("http://localhost:5000", {
  autoConnect: false,
  transports: ["websocket"], // evita polling se possibile
});
