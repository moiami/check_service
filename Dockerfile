FROM ubuntu:latest
LABEL authors="Leonid"

ENTRYPOINT ["top", "-b"]