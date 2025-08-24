#!/bin/bash
set -euo pipefail

# ARES Docker Build Script with Advanced Caching
# Optimized for <3min build times using BuildKit cache mounts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ares"
REGISTRY="${DOCKER_REGISTRY:-localhost:5000}"
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
VERSION=$(grep version pyproject.toml | head -1 | cut -d'"' -f2 2>/dev/null || echo "0.1.0")

# Docker BuildKit settings
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain
export BUILDKIT_INLINE_CACHE=1

echo -e "${BLUE}🚀 ARES Advanced Docker Build with Caching Optimization${NC}"
echo -e "${BLUE}=================================================${NC}"
echo "Build Date: $BUILD_DATE"
echo "VCS Ref: $VCS_REF"
echo "Version: $VERSION"
echo ""

# Function to log with timestamp
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if BuildKit is available
check_buildkit() {
    if ! docker buildx version >/dev/null 2>&1; then
        error "Docker Buildx is not available. Please install Docker Desktop or Docker CE with Buildx plugin."
        exit 1
    fi
    log "✅ Docker Buildx available"

    # Create builder if it doesn't exist
    if ! docker buildx inspect ares-builder >/dev/null 2>&1; then
        log "Creating optimized Docker builder..."
        docker buildx create --name ares-builder --driver docker-container --bootstrap
    fi

    docker buildx use ares-builder
}

# Build with cache optimization
build_with_cache() {
    local target="$1"
    local tag_name="$2"
    local cache_from_args=""
    local cache_to_args=""

    # Configure cache strategy
    if [[ "${CI:-false}" == "true" ]]; then
        # CI/CD environment - use registry cache
        cache_from_args="--cache-from type=registry,ref=${REGISTRY}/${PROJECT_NAME}:cache-${target}"
        cache_to_args="--cache-to type=registry,ref=${REGISTRY}/${PROJECT_NAME}:cache-${target},mode=max"
    else
        # Local development - use local cache
        cache_from_args="--cache-from type=local,src=/tmp/.buildx-cache-${target}"
        cache_to_args="--cache-to type=local,dest=/tmp/.buildx-cache-${target},mode=max"
    fi

    log "🔨 Building $target with advanced cache mounts..."

    # Start timer
    start_time=$(date +%s)

    # Build with optimized caching
    docker buildx build \
        --target "$target" \
        --tag "$tag_name" \
        --build-arg BUILD_DATE="$BUILD_DATE" \
        --build-arg VCS_REF="$VCS_REF" \
        --build-arg VERSION="$VERSION" \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        $cache_from_args \
        $cache_to_args \
        --load \
        --progress=plain \
        .

    # Calculate build time
    end_time=$(date +%s)
    build_time=$((end_time - start_time))

    if [ $build_time -lt 180 ]; then  # Less than 3 minutes
        log "✅ $target built successfully in ${build_time}s (Target: <180s) 🎯"
    else
        warning "$target built in ${build_time}s (Over 180s target)"
    fi

    return $build_time
}

# Performance monitoring
monitor_build_performance() {
    local target="$1"
    local build_time="$2"

    # Log performance metrics
    {
        echo "Build Performance Report - $(date)"
        echo "Target: $target"
        echo "Build Time: ${build_time}s"
        echo "Performance Target: <180s"
        echo "Status: $([ $build_time -lt 180 ] && echo "✅ PASS" || echo "⚠️  SLOW")"
        echo "Cache Hit Rate: $(docker system df --verbose | grep 'Build Cache' || echo 'Not available')"
        echo ""
    } >> build-performance.log
}

# Main build function
build_target() {
    local target="${1:-production}"
    local push="${2:-false}"

    case "$target" in
        "production"|"prod")
            local tag="${REGISTRY}/${PROJECT_NAME}:${VERSION}"
            local latest_tag="${REGISTRY}/${PROJECT_NAME}:latest"
            build_time=$(build_with_cache "production" "$tag")
            monitor_build_performance "production" "$build_time"

            if [ "$push" == "true" ]; then
                docker tag "$tag" "$latest_tag"
                docker push "$tag"
                docker push "$latest_tag"
            fi
            ;;

        "development"|"dev")
            local tag="${REGISTRY}/${PROJECT_NAME}:dev"
            build_time=$(build_with_cache "development" "$tag")
            monitor_build_performance "development" "$build_time"

            if [ "$push" == "true" ]; then
                docker push "$tag"
            fi
            ;;

        "testing"|"test")
            local tag="${REGISTRY}/${PROJECT_NAME}:test"
            build_time=$(build_with_cache "testing" "$tag")
            monitor_build_performance "testing" "$build_time"
            ;;

        "celery-worker")
            local tag="${REGISTRY}/${PROJECT_NAME}:celery-worker"
            build_time=$(build_with_cache "celery-worker" "$tag")
            monitor_build_performance "celery-worker" "$build_time"

            if [ "$push" == "true" ]; then
                docker push "$tag"
            fi
            ;;

        "celery-beat")
            local tag="${REGISTRY}/${PROJECT_NAME}:celery-beat"
            build_time=$(build_with_cache "celery-beat" "$tag")
            monitor_build_performance "celery-beat" "$build_time"

            if [ "$push" == "true" ]; then
                docker push "$tag"
            fi
            ;;

        "all")
            log "🚀 Building all targets with parallel optimization..."

            # Build base dependencies first (shared across targets)
            build_with_cache "dependencies" "${REGISTRY}/${PROJECT_NAME}:deps"

            # Build all targets in sequence (parallel causes resource contention)
            total_start=$(date +%s)

            build_target "production" "$push"
            build_target "development" "$push"
            build_target "testing"
            build_target "celery-worker" "$push"
            build_target "celery-beat" "$push"

            total_end=$(date +%s)
            total_time=$((total_end - total_start))

            log "🎯 All targets completed in ${total_time}s"
            ;;

        *)
            error "Unknown target: $target"
            echo "Available targets: production, development, testing, celery-worker, celery-beat, all"
            exit 1
            ;;
    esac
}

# Cache management functions
prune_cache() {
    log "🧹 Pruning Docker build cache..."
    docker buildx prune -f
    docker system prune -f --volumes
}

show_cache_info() {
    log "📊 Docker Build Cache Information:"
    docker system df -v
    echo ""
    docker buildx du
}

# Performance benchmark
benchmark_build() {
    log "🏃‍♂️ Running build performance benchmark..."

    # Clean build (no cache)
    prune_cache
    start_time=$(date +%s)
    build_target "production"
    clean_build_time=$(($(date +%s) - start_time))

    # Cached build (should be much faster)
    start_time=$(date +%s)
    build_target "production"
    cached_build_time=$(($(date +%s) - start_time))

    log "📈 Benchmark Results:"
    log "Clean Build: ${clean_build_time}s"
    log "Cached Build: ${cached_build_time}s"
    log "Cache Improvement: $((clean_build_time - cached_build_time))s ($((100 - (cached_build_time * 100 / clean_build_time)))% faster)"
}

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS] TARGET"
    echo ""
    echo "Targets:"
    echo "  production     Build production image (default)"
    echo "  development    Build development image"
    echo "  testing        Build testing image"
    echo "  celery-worker  Build Celery worker image"
    echo "  celery-beat    Build Celery beat scheduler image"
    echo "  all           Build all targets"
    echo ""
    echo "Options:"
    echo "  --push         Push images to registry after build"
    echo "  --benchmark    Run performance benchmark"
    echo "  --cache-info   Show cache information"
    echo "  --prune-cache  Clean build cache"
    echo "  --help         Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  DOCKER_REGISTRY  Registry to push images to (default: localhost:5000)"
    echo "  CI               Set to 'true' for CI/CD optimizations"
}

# Parse command line arguments
TARGET="production"
PUSH="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --push)
            PUSH="true"
            shift
            ;;
        --benchmark)
            check_buildkit
            benchmark_build
            exit 0
            ;;
        --cache-info)
            show_cache_info
            exit 0
            ;;
        --prune-cache)
            prune_cache
            exit 0
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        production|development|testing|celery-worker|celery-beat|all)
            TARGET="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    # Pre-flight checks
    check_buildkit

    # Build the target
    build_target "$TARGET" "$PUSH"

    # Show final cache info
    log "📊 Final build cache status:"
    show_cache_info

    log "🎉 Build completed successfully!"
    log "💡 Tip: Use '--cache-info' to monitor cache efficiency"
}

# Run main function
main "$@"
