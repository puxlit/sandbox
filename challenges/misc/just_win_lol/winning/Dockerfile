FROM golang:1.22 AS build
WORKDIR /app
COPY go.mod go.sum /app/
RUN go mod download
COPY *.go /app/
RUN CGO_ENABLED=0 GOOS=linux go build -o /winning

FROM alpine:latest AS run
WORKDIR /app
COPY --from=build /winning /app/
ENTRYPOINT ["/app/winning"]
