#!/bin/bash

# 镜像名称和标签
IMAGE_NAME="say-more-teacher"
TAG="develop"
ALIYUN_REGISTRY="registry.cn-hangzhou.personal.cr.aliyuncs.com/say-more/$IMAGE_NAME:$TAG"

# 构建镜像
echo "🚀 Building Docker image..."
docker build --platform linux/amd64 -t $IMAGE_NAME:$TAG .

# 获取刚刚构建的镜像 ID
IMAGE_ID=$(docker images $IMAGE_NAME:$TAG -q)

if [ -z "$IMAGE_ID" ]; then
  echo "❌ Failed to get image ID. Build might have failed."
  exit 1
fi

# 打标签
echo "🏷  Tagging image $IMAGE_ID as $ALIYUN_REGISTRY"
docker tag $IMAGE_ID $ALIYUN_REGISTRY

# 推送到阿里云
echo "📦 Pushing image to Aliyun registry..."
docker push $ALIYUN_REGISTRY

echo "✅ Done! Image pushed: $ALIYUN_REGISTRY"