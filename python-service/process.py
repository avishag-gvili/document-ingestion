import pika
import psycopg2
import pandas as pd

def process_document(document_id):
    try:
        conn = psycopg2.connect("dbname=document_db user=postgres password=avishag12 host=localhost")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return

    cur = conn.cursor()

    try:
        print(f"Updating document {document_id} status to 'processing'")
        cur.execute("UPDATE documents SET status = 'processing' WHERE document_id = %s", (document_id,))
        conn.commit()
    except Exception as e:
        print(f"Error updating document status: {e}")
        conn.rollback()
        return

    file_path = f'uploads/{document_id}.xlsx'
    print(f"Attempting to read Excel file from {file_path}")

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    processed_data = df.to_dict(orient='records')
    print(f"Processed data: {processed_data}")

    try:
        for data in processed_data:
            cur.execute("INSERT INTO processed_data (document_id, data) VALUES (%s, %s)", (document_id, str(data)))
        conn.commit()
    except Exception as e:
        print(f"Error inserting processed data: {e}")
        conn.rollback()
        return

    try:
        print(f"Updating document {document_id} status to 'completed'")
        cur.execute("UPDATE documents SET status = 'completed' WHERE document_id = %s", (document_id,))
        conn.commit()
    except Exception as e:
        print(f"Error updating document status to 'completed': {e}")
        conn.rollback()
        return

    cur.close()
    conn.close()

def callback(ch, method, properties, body):
    document_id = int(body)
    print(f"Received document ID: {document_id}")
    process_document(document_id)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def listen_for_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='document_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='document_queue', on_message_callback=callback)

    print('Waiting for messages...')
    channel.start_consuming()

if __name__ == '__main__':
    listen_for_messages()
