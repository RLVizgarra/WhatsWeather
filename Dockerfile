FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY app/ .

ENV WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
ENV WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
ENV WHATSAPP_TO_PHONE_NUMBER=your_whatsapp_to_phone_number

EXPOSE 5000

CMD ["python", "main.py"]