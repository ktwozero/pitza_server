// server.js

const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const cors = require("cors");
const bodyParser = require("body-parser");

const app = express();
app.use(cors());
app.use(bodyParser.json());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

io.on("connection", (socket) => {
  console.log("✅ 연결됨:", socket.id);

  socket.on("join_room", (roomId) => {
    socket.join(roomId);
    console.log(`${socket.id}님이 ${roomId} 방에 입장`);
  });

  socket.on("send_message", (data) => {
    io.to(data.roomId).emit("receive_message", data);
  });
});

app.post("/socket/message", (req, res) => {
  const { roomId, sender_id, content, message_type } = req.body;

  io.to(roomId).emit("receive_message", {
    sender_id,
    content,
    message_type,
    sent_at: new Date().toISOString()
  });

  res.status(200).send({ status: "message sent" });
});

server.listen(3001, () => {
  console.log("🚀 socket.io 서버 실행 중 (http://localhost:3001)");
});
