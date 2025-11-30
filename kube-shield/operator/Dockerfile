# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Install git for go mod download
RUN apk add --no-cache git

# Copy go mod files first for better caching
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags="-w -s" -o /kubeshield-operator ./cmd/controller

# Runtime stage
FROM alpine:3.19

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /

# Copy the binary
COPY --from=builder /kubeshield-operator .

# Create non-root user
RUN addgroup -g 1000 kubeshield && \
    adduser -u 1000 -G kubeshield -s /bin/sh -D kubeshield

USER 1000:1000

ENTRYPOINT ["/kubeshield-operator"]
