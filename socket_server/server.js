const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const cors = require("cors");
const bodyParser = require("body-parser");
const { createAdapter } = require("@socket.io/redis-adapter");
const { createClient } = require("redis");

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

// 🔧 Redis 연결 주소 (Docker에서는 보통 redis라는 서비스명 사용)
const REDIS_URL = process.env.REDIS_URL || "redis://redis:6379";

// Redis client 생성 및 연결
const pubClient = createClient({ url: REDIS_URL });
const subClient = pubClient.duplicate();

Promise.all([pubClient.connect(), subClient.connect()])
  .then(() => {
    io.adapter(createAdapter(pubClient, subClient));
    console.log("✅ Redis adapter 연결 성공");

    io.on("connection", (socket) => {
      console.log("🟢 연결됨:", socket.id);

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

    server.listen(3000, () => {
      console.log("🚀 socket.io 서버 실행 중 (http://localhost:3001)");
    });
  })
  .catch((err) => {
    console.error("❌ Redis 연결 실패:", err);
  });
