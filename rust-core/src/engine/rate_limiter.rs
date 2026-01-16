// 速率限制器（令牌桶算法）
// Agent 2 实现

use anyhow::Result;
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::RwLock;
use tokio::time::sleep;

/// 速率限制器（令牌桶算法）
///
/// 用于限制 API 请求速率，防止超过币安的速率限制
///
/// # 示例
/// ```
/// let limiter = RateLimiter::new(1200.0, 10.0);
/// limiter.acquire(1.0).await?;
/// ```
pub struct RateLimiter {
    /// 当前令牌数量
    tokens: Arc<RwLock<f64>>,
    /// 最大令牌数量
    max_tokens: f64,
    /// 令牌补充速率（tokens/秒）
    refill_rate: f64,
    /// 上次补充令牌的时间
    last_refill: Arc<RwLock<Instant>>,
}

impl RateLimiter {
    /// 创建新的速率限制器
    ///
    /// # Arguments
    /// * `max_tokens` - 令牌桶最大容量
    /// * `refill_rate` - 每秒补充的令牌数
    ///
    /// # Returns
    /// 返回新的 RateLimiter 实例
    pub fn new(max_tokens: f64, refill_rate: f64) -> Self {
        Self {
            tokens: Arc::new(RwLock::new(max_tokens)),
            max_tokens,
            refill_rate,
            last_refill: Arc::new(RwLock::new(Instant::now())),
        }
    }

    /// 补充令牌
    ///
    /// 根据时间流逝自动补充令牌
    async fn refill_tokens(&self) {
        let mut tokens = self.tokens.write().await;
        let mut last_refill = self.last_refill.write().await;

        let now = Instant::now();
        let elapsed = now.duration_since(*last_refill).as_secs_f64();

        // 计算应该补充的令牌数
        let tokens_to_add = elapsed * self.refill_rate;
        *tokens = (*tokens + tokens_to_add).min(self.max_tokens);
        *last_refill = now;
    }

    /// 尝试获取令牌（非阻塞）
    ///
    /// # Arguments
    /// * `tokens` - 需要获取的令牌数
    ///
    /// # Returns
    /// 如果有足够的令牌则返回 true，否则返回 false
    pub async fn try_acquire(&self, tokens: f64) -> bool {
        // 先补充令牌
        self.refill_tokens().await;

        let mut current_tokens = self.tokens.write().await;

        if *current_tokens >= tokens {
            *current_tokens -= tokens;
            true
        } else {
            false
        }
    }

    /// 获取令牌（阻塞直到可用）
    ///
    /// # Arguments
    /// * `tokens` - 需要获取的令牌数
    ///
    /// # Returns
    /// 当成功获取令牌时返回 Ok(())
    ///
    /// # Errors
    /// 如果请求的令牌数超过最大容量，返回错误
    pub async fn acquire(&self, tokens: f64) -> Result<()> {
        if tokens > self.max_tokens {
            return Err(anyhow::anyhow!(
                "Requested tokens ({}) exceed maximum capacity ({})",
                tokens,
                self.max_tokens
            ));
        }

        loop {
            // 先补充令牌
            self.refill_tokens().await;

            {
                let mut current_tokens = self.tokens.write().await;

                if *current_tokens >= tokens {
                    *current_tokens -= tokens;
                    return Ok(());
                }
            }

            // 计算需要等待的时间
            let current_tokens = *self.tokens.read().await;
            let tokens_needed = tokens - current_tokens;
            let wait_time = (tokens_needed / self.refill_rate) * 1000.0; // 转换为毫秒

            // 等待一小段时间后重试
            sleep(Duration::from_millis(wait_time.ceil() as u64 + 10)).await;
        }
    }

    /// 获取当前可用令牌数
    ///
    /// # Returns
    /// 返回当前可用的令牌数量
    pub async fn available_tokens(&self) -> f64 {
        // 先补充令牌
        self.refill_tokens().await;
        *self.tokens.read().await
    }

    /// 重置令牌桶
    ///
    /// 将令牌数量重置为最大值
    pub async fn reset(&self) {
        let mut tokens = self.tokens.write().await;
        let mut last_refill = self.last_refill.write().await;

        *tokens = self.max_tokens;
        *last_refill = Instant::now();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tokio::time::{sleep, Duration};

    #[tokio::test]
    async fn test_rate_limiter_creation() {
        let limiter = RateLimiter::new(100.0, 10.0);
        let available = limiter.available_tokens().await;
        assert_eq!(available, 100.0);
    }

    #[tokio::test]
    async fn test_try_acquire_success() {
        let limiter = RateLimiter::new(100.0, 10.0);
        let result = limiter.try_acquire(50.0).await;
        assert!(result);

        let available = limiter.available_tokens().await;
        assert!((available - 50.0).abs() < 0.1); // 允许浮点误差
    }

    #[tokio::test]
    async fn test_try_acquire_failure() {
        let limiter = RateLimiter::new(100.0, 10.0);
        limiter.try_acquire(90.0).await;

        let result = limiter.try_acquire(50.0).await;
        assert!(!result);
    }

    #[tokio::test]
    async fn test_acquire_blocking() {
        let limiter = RateLimiter::new(100.0, 50.0); // 每秒补充 50 tokens

        // 先消耗所有令牌
        limiter.acquire(100.0).await.unwrap();

        let start = Instant::now();
        // 这个调用应该等待约 1 秒（50 tokens / 50 tokens per second）
        limiter.acquire(50.0).await.unwrap();
        let elapsed = start.elapsed();

        assert!(elapsed.as_secs() >= 1);
    }

    #[tokio::test]
    async fn test_refill_tokens() {
        let limiter = RateLimiter::new(100.0, 10.0);

        // 消耗一些令牌
        limiter.try_acquire(50.0).await;
        let initial = limiter.available_tokens().await;
        assert!((initial - 50.0).abs() < 0.1);

        // 等待 1 秒，应该补充 10 个令牌
        sleep(Duration::from_secs(1)).await;
        let available = limiter.available_tokens().await;
        assert!(available >= 59.0 && available <= 61.0); // 允许一些误差
    }

    #[tokio::test]
    async fn test_refill_max_cap() {
        let limiter = RateLimiter::new(100.0, 10.0);

        // 等待很长时间
        sleep(Duration::from_secs(20)).await;

        // 令牌数量不应超过最大值
        let available = limiter.available_tokens().await;
        assert_eq!(available, 100.0);
    }

    #[tokio::test]
    async fn test_reset() {
        let limiter = RateLimiter::new(100.0, 10.0);

        // 消耗所有令牌
        limiter.acquire(100.0).await.unwrap();
        let after_consume = limiter.available_tokens().await;
        assert!(after_consume < 0.1); // 接近 0

        // 重置
        limiter.reset().await;
        let after_reset = limiter.available_tokens().await;
        assert!((after_reset - 100.0).abs() < 0.1);
    }

    #[tokio::test]
    async fn test_acquire_exceeds_max() {
        let limiter = RateLimiter::new(100.0, 10.0);

        let result = limiter.acquire(150.0).await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_concurrent_acquire() {
        let limiter = Arc::new(RateLimiter::new(1000.0, 100.0));

        let mut handles = vec![];

        // 10 个并发任务，每个尝试获取 100 tokens
        for _ in 0..10 {
            let limiter_clone = limiter.clone();
            let handle = tokio::spawn(async move {
                limiter_clone.acquire(100.0).await.unwrap();
            });
            handles.push(handle);
        }

        // 等待所有任务完成
        for handle in handles {
            handle.await.unwrap();
        }

        // 应该消耗了 1000 tokens
        let available = limiter.available_tokens().await;
        assert!(available < 10.0); // 允许一些补充
    }
}
