const express = require('express');
const multer = require('multer');
const { Client } = require('pg');
const path = require('path');
const fs = require('fs');
const amqp = require('amqplib');
const app = express();
const port = 3000;

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, './uploads'),
  filename: (req, file, cb) => cb(null, Date.now() + path.extname(file.originalname)),
});
const upload = multer({ storage });

const client = new Client({
  user: 'postgres',
  host: 'localhost',
  database: 'document_db',
  password: 'avishag12',
  port: 5432,
});

client.connect();

let channel, connection;
async function connectRabbitMQ() {
  connection = await amqp.connect('amqp://localhost');
  channel = await connection.createChannel();
  await channel.assertQueue('document_queue', { durable: true });
}

app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    console.log("File uploaded:", req.file);
    const { filename } = req.file;
    const status = 'uploaded';
    const query = 'INSERT INTO documents (filename, status) VALUES ($1, $2) RETURNING document_id';
    const result = await client.query(query, [filename, status]);
    console.log("Inserted document:", result.rows[0]);

    const documentId = result.rows[0].document_id;
    await channel.sendToQueue('document_queue', Buffer.from(documentId.toString()), {
      persistent: true,
    });

    res.status(201).json({ document_id: documentId });
  } catch (err) {
    console.error("Error uploading file:", err);
    res.status(500).send("Error uploading file");
  }
});

app.get('/status/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const query = 'SELECT status FROM documents WHERE document_id = $1';
    const result = await client.query(query, [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Document not found' });
    }

    res.status(200).json({ status: result.rows[0].status });
  } catch (err) {
    console.error("Error fetching status:", err);
    res.status(500).send("Error fetching document status");
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
  connectRabbitMQ().catch(err => console.error('Failed to connect to RabbitMQ', err));
});
