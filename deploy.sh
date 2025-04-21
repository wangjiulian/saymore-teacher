#!/bin/bash

# Image name and tag
IMAGE_NAME="say-more-teacher"
TAG="develop"
ALIYUN_REGISTRY="registry.cn-hangzhou.personal.cr.aliyuncs.com/say-more/$IMAGE_NAME:$TAG"

# Build the Docker image
echo "🚀 Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME:$TAG .

# Get the ID of the newly built image
IMAGE_ID=$(docker images $IMAGE_NAME:$TAG -q)

if [ -z "$IMAGE_ID" ]; then
  echo "❌ Failed to get image ID. Build might have failed."
  exit 1
fi

# Tag the image
echo "🏷  Tagging image $IMAGE_ID as $ALIYUN_REGISTRY"
docker tag $IMAGE_ID $ALIYUN_REGISTRY

# Push the image to Aliyun registry
echo "📦 Pushing image to Aliyun registry..."
docker push $ALIYUN_REGISTRY

echo "✅ Done! Image pushed: $ALIYUN_REGISTRY"