ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip py3-flask

WORKDIR /app
COPY rootfs/usr/bin/kalender.py /app/kalender.py
COPY rootfs/usr/bin/static /app/static
COPY rootfs/etc/services.d/kalender/run /etc/services.d/kalender/run

RUN chmod +x /etc/services.d/kalender/run

EXPOSE 5050
