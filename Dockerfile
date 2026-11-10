# Menggunakan base image Python resmi yang ringan (slim)
FROM python:3.11-slim

# Menentukan folder kerja di dalam kontainer
WORKDIR /app

# Menyalin file app.py dari laptop (host) ke dalam kontainer
COPY app.py /app/app.py

# Membuat direktori tempat Named Volume akan dipasang (mount)
RUN mkdir -p /var/lib/backend_data

# Memberi tahu bahwa kontainer Backend berjalan di port 5000
EXPOSE 5000

# Menjalankan server Python tanpa buffer log (-u) agar log langsung muncul
CMD ["python", "-u", "app.py"]

